# bot/handlers.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Main Message Handler - Complete with all handlers
=============================================================================
"""

import time
import logging
import random
import asyncio
import traceback
from typing import Dict, Optional, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import settings
from identity.manager import IdentityManager
from core.ai_engine import AIEngine
from intimacy.leveling import LevelingSystem
from intimacy.stamina import StaminaSystem
from utils.logger import logger
from utils.error_logger import log_error, log_info, log_warning

_active_engines: Dict[str, AIEngine] = {}

# =============================================================================
# CONSTANTS
# =============================================================================
MAX_MESSAGE_LENGTH = 4000


# =============================================================================
# HELPER: SEND LONG MESSAGE
# =============================================================================

async def send_long_message(update: Update, text: str, parse_mode: str = 'HTML'):
    """Kirim pesan panjang dengan split jika melebihi batas Telegram"""
    if len(text) <= MAX_MESSAGE_LENGTH:
        await update.message.reply_text(text, parse_mode=parse_mode)
        return
    
    parts = []
    remaining = text
    
    while len(remaining) > MAX_MESSAGE_LENGTH:
        split_pos = remaining[:MAX_MESSAGE_LENGTH].rfind('\n')
        if split_pos == -1:
            split_pos = remaining[:MAX_MESSAGE_LENGTH].rfind(' ')
        if split_pos == -1:
            split_pos = MAX_MESSAGE_LENGTH
        
        parts.append(remaining[:split_pos])
        remaining = remaining[split_pos:]
    
    parts.append(remaining)
    
    for i, part in enumerate(parts, 1):
        prefix = f"📄 Bagian {i}/{len(parts)}:\n\n" if len(parts) > 1 else ""
        await update.message.reply_text(prefix + part, parse_mode=parse_mode)


# =============================================================================
# MAIN MESSAGE HANDLER
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk semua pesan teks"""
    try:
        user = update.effective_user
        user_message = update.message.text
        user_id = user.id
        
        current_reg = context.user_data.get('current_registration')
        
        if not current_reg:
            await update.message.reply_text(
                "❌ **Tidak ada karakter aktif**\n\n"
                "Ketik `/start` untuk memilih karakter.",
                parse_mode='HTML'
            )
            return
        
        registration_id = current_reg.get('id')
        
        if context.user_data.get('paused', False):
            await update.message.reply_text(
                "⏸️ **Sesi dijeda**\n\nKetik `/unpause` untuk melanjutkan.",
                parse_mode='HTML'
            )
            return
        
        if registration_id not in _active_engines:
            identity_manager = IdentityManager()
            character = await identity_manager.get_character(registration_id)
            
            if not character:
                await update.message.reply_text(
                    "❌ **Karakter tidak ditemukan**\n\nKetik `/sessions` untuk melihat karakter.",
                    parse_mode='HTML'
                )
                return
            
            _active_engines[registration_id] = AIEngine(character)
            logger.info(f"✅ AI Engine created for {registration_id}")
        
        ai_engine = _active_engines[registration_id]
        
        # Dapatkan state (hanya lokasi, posisi, pakaian)
        identity_manager = IdentityManager()
        state = await identity_manager.get_character_state(registration_id)
        
        # Update waktu typing
        await update.message.chat.send_action(action="typing")
        
        # Simulasi delay natural (1-3 detik)
        await asyncio.sleep(random.uniform(1, 3))
        
        # Proses pesan dengan AI
        response = await ai_engine.process_message(
            user_message=user_message,
            context={
                'state': state,
                'user_name': current_reg.get('user_name', 'User'),
                'bot_name': current_reg.get('bot_name', 'Amoria'),
                'role': current_reg.get('role', 'pdkt'),
                'level': current_reg.get('level', 1)
            }
        )
        
        # Kirim respons dengan fungsi split
        await send_long_message(update, response, parse_mode='HTML')
        
        # Update progress setelah chat
        await _update_progress(registration_id, ai_engine)
        
        # Update context
        context.user_data['last_message_time'] = time.time()
        context.user_data['last_message'] = user_message
        context.user_data['last_response'] = response
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        traceback.print_exc()
        await update.message.reply_text(
            "❌ **Terjadi kesalahan**\n\nMaaf, aku mengalami gangguan. Coba lagi nanti.",
            parse_mode='HTML'
        )


# =============================================================================
# UPDATE PROGRESS
# =============================================================================

async def _update_progress(registration_id: str, ai_engine: AIEngine) -> None:
    """Update progress setelah chat"""
    try:
        identity_manager = IdentityManager()
        character = await identity_manager.get_character(registration_id)
        
        if not character:
            logger.warning(f"Character not found for {registration_id}")
            return
        
        # Update total chats
        character.total_chats += 1
        character.last_updated = time.time()
        
        # Leveling system
        leveling = LevelingSystem()
        old_level = character.level
        level_info = leveling.calculate_level(character.total_chats, character.in_intimacy_cycle)
        new_level = level_info.level
        
        if new_level > old_level:
            character.level = new_level
            logger.info(f"Level up for {registration_id}: {old_level} → {new_level}")
        
        # Stamina recovery
        stamina = StaminaSystem()
        stamina.check_recovery()
        character.bot.stamina = stamina.bot_stamina.current
        character.user.stamina = stamina.user_stamina.current
        
        # Save to database
        db_reg = character.to_db_registration()
        await identity_manager.repo.update_registration(db_reg)
        
        # Save state dengan pengecekan aman
        try:
            state = await identity_manager.get_character_state(registration_id)
            
            if state is not None:
                # Jika state adalah dict
                if isinstance(state, dict):
                    state['updated_at'] = time.time()
                    from database.models import StateTracker
                    state_obj = StateTracker.from_dict(state)
                    await identity_manager.repo.save_state(state_obj)
                    logger.debug(f"State saved (dict) for {registration_id}")
                
                # Jika state adalah objek StateTracker
                elif hasattr(state, 'updated_at'):
                    state.updated_at = time.time()
                    await identity_manager.repo.save_state(state)
                    logger.debug(f"State saved (object) for {registration_id}")
                
                # Jika state adalah string atau tipe lain
                else:
                    logger.warning(f"State has unexpected type {type(state)} for {registration_id}, skipping save")
            else:
                logger.debug(f"No state found for {registration_id}")
                
        except Exception as state_error:
            logger.error(f"Error saving state for {registration_id}: {state_error}")
        
    except Exception as e:
        logger.error(f"Error updating progress for {registration_id}: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# UNPAUSE HANDLER
# =============================================================================

async def unpause_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk melanjutkan session yang dijeda"""
    context.user_data['paused'] = False
    await update.message.reply_text(
        "▶️ **Sesi dilanjutkan!**\n\nYuk lanjut ngobrol... 🥰",
        parse_mode='HTML'
    )


# =============================================================================
# SESSIONS HANDLER
# =============================================================================

async def sessions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk melihat semua karakter tersimpan"""
    identity_manager = IdentityManager()
    characters = await identity_manager.get_all_characters()
    
    if not characters:
        await update.message.reply_text(
            "📋 **DAFTAR KARAKTER**\n\nBelum ada karakter tersimpan.\nKetik /start untuk membuat karakter baru.",
            parse_mode='HTML'
        )
        return
    
    lines = ["📋 **DAFTAR KARAKTER**", ""]
    
    for i, char in enumerate(characters[:10], 1):
        status = "🟢" if char.status == 'active' else "⚪"
        lines.append(f"{i}. {status} **{char.bot.name}** ({char.role.value.upper()}) - Level {char.level}")
    
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')


# =============================================================================
# STATUS HANDLER
# =============================================================================

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk melihat status hubungan"""
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\nKetik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    identity_manager = IdentityManager()
    character = await identity_manager.get_character(current_reg.get('id'))
    
    if not character:
        await update.message.reply_text("❌ Gagal memuat data karakter.", parse_mode='HTML')
        return
    
    state = await identity_manager.get_character_state(current_reg.get('id'))
    
    location = state.get('location_bot', 'ruang tamu') if state else 'ruang tamu'
    arousal = character.bot.arousal
    emotion = character.bot.emotion
    
    response = f"""
📊 **STATUS HUBUNGAN**

👤 **{character.bot.name}** ({character.role.value.upper()})
📍 **Lokasi:** {location}
🎭 **Emosi:** {emotion} | Arousal: {arousal}%
📊 **Level:** {character.level}/12
💬 **Total Chat:** {character.total_chats}
💪 **Stamina:** {character.bot.stamina}% / {character.user.stamina}%
"""
    
    await update.message.reply_text(response, parse_mode='HTML')


# =============================================================================
# PROGRESS HANDLER
# =============================================================================

async def progress_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk melihat progress leveling (rahasia)"""
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\nKetik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    identity_manager = IdentityManager()
    character = await identity_manager.get_character(current_reg.get('id'))
    
    if not character:
        await update.message.reply_text("❌ Gagal memuat data karakter.", parse_mode='HTML')
        return
    
    leveling = LevelingSystem()
    level_info = leveling.calculate_level(character.total_chats, character.in_intimacy_cycle)
    bar = level_info.get_progress_bar(20)
    
    response = f"""
📊 **PROGRESS HUBUNGAN** _(RAHASIA)_

👤 **{character.bot.name}** (Level {character.level}/12)

📊 Progress: {bar} {level_info.progress:.0f}%
💬 Total Chat: {character.total_chats}
💦 Climax: {character.bot.total_climax + character.user.total_climax}x

⚠️ Bot tidak tahu Mas melihat ini!
💡 Semakin banyak chat, semakin cepat level naik!
"""
    
    await update.message.reply_text(response, parse_mode='HTML')


# =============================================================================
# CLOSE HANDLER
# =============================================================================

async def close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk menutup karakter saat ini"""
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\nKetik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    identity_manager = IdentityManager()
    await identity_manager.close_current_session()
    context.user_data.pop('current_registration', None)
    
    await update.message.reply_text(
        "📁 **Karakter ditutup!**\n\nKetik `/sessions` untuk melihat karakter tersimpan.",
        parse_mode='HTML'
    )


# =============================================================================
# END HANDLER
# =============================================================================

async def end_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk mengakhiri karakter permanen"""
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\nKetik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    bot_name = current_reg.get('bot_name', 'Unknown')
    
    keyboard = [[
        InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"end_confirm_{current_reg['id']}"),
        InlineKeyboardButton("❌ Batal", callback_data="end_cancel")
    ]]
    
    await update.message.reply_text(
        f"⚠️ **Yakin ingin menghapus {bot_name}?**\n\nSEMUA DATA akan hilang permanen!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


# =============================================================================
# CANCEL COMMAND HANDLER
# =============================================================================

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk /cancel - Batalkan percakapan"""
    context.user_data.pop('pending_action', None)
    context.user_data.pop('pending_state', None)
    
    await update.message.reply_text(
        "❌ **Dibatalkan**\n\nPercakapan dibatalkan. Ketik pesan untuk memulai lagi.",
        parse_mode='HTML'
    )


# =============================================================================
# HELP COMMAND HANDLER
# =============================================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk /help - Bantuan lengkap"""
    user_id = update.effective_user.id
    is_admin = (user_id == settings.admin_id)
    
    help_text = (
        "📚 **BANTUAN AMORIA 9.9**\n\n"
        "<b>Basic Commands:</b>\n"
        "/start - Mulai bot & pilih karakter\n"
        "/help - Bantuan lengkap\n"
        "/status - Status hubungan saat ini\n"
        "/progress - Progress leveling\n"
        "/cancel - Batalkan percakapan\n"
        "/unpause - Lanjutkan sesi yang dijeda\n\n"
        "<b>Session Commands:</b>\n"
        "/close - Tutup & simpan karakter\n"
        "/end - Akhiri karakter total\n"
        "/sessions - Lihat semua karakter tersimpan\n"
        "/character [role] [nomor] - Lanjutkan karakter\n\n"
        "<b>Character Commands:</b>\n"
        "/character_list - Lihat semua karakter\n"
        "/character_pause - Jeda karakter\n"
        "/character_resume - Lanjutkan karakter\n"
        "/character_stop - Hentikan karakter"
    )
    
    if is_admin:
        help_text += (
            "\n\n<b>Admin Commands:</b>\n"
            "/admin - Panel admin\n"
            "/stats - Statistik bot\n"
            "/db_stats - Statistik database\n"
            "/backup - Backup manual\n"
            "/recover - Restore dari backup\n"
            "/debug - Info debug"
        )
    
    await update.message.reply_text(help_text, parse_mode='HTML')


# =============================================================================
# ERROR HANDLER
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler untuk semua error di bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ **Terjadi error internal**\n\n"
                "Maaf, terjadi kesalahan. Silakan coba lagi nanti, Mas.\n\n"
                "_Jika error berlanjut, laporkan ke admin._",
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error sending error message: {e}")


# =============================================================================
# CALLBACK HANDLERS
# =============================================================================

async def end_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi hapus karakter"""
    query = update.callback_query
    await query.answer()
    
    registration_id = query.data.replace("end_confirm_", "")
    identity_manager = IdentityManager()
    
    await identity_manager.end_character(registration_id)
    
    if context.user_data.get('current_registration', {}).get('id') == registration_id:
        context.user_data.pop('current_registration', None)
    
    await query.edit_message_text(
        "💔 **Karakter dihapus permanen!**\n\nKetik `/start` untuk membuat karakter baru.",
        parse_mode='HTML'
    )


async def end_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback batal hapus karakter"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✅ **Penghapusan dibatalkan.**\n\nKarakter tetap tersimpan.",
        parse_mode='HTML'
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main handlers
    'message_handler',
    'error_handler',
    'help_command',
    'cancel_command',
    'unpause_handler',
    'sessions_handler',
    'status_handler',
    'progress_handler',
    'close_handler',
    'end_handler',
    
    # Callbacks
    'end_confirm_callback',
    'end_cancel_callback',
    
    # Helpers
    'send_long_message',
    '_active_engines',
]
