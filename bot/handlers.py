# bot/handlers.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Main Message Handler
=============================================================================
"""

import time
import logging
import random
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from identity.manager import IdentityManager
from core.ai_engine import AIEngine
from dynamics.emotional_flow import EmotionalFlow
from dynamics.spatial_awareness import SpatialAwareness
from dynamics.mood import MoodSystem
from intimacy.leveling import LevelingSystem
from intimacy.cycle import IntimacyCycle
from intimacy.clothing import ClothingSystem
from intimacy.stamina import StaminaSystem
from tracking.family import FamilyTracking
from tracking.promises import PromisesTracker
from tracking.preferences import PreferencesLearner
from command.status import status_command
from utils.logger import logger

# Active AI engines per registration
_active_engines: Dict[str, AIEngine] = {}


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk semua pesan teks
    - 100% AI generate response
    - Tanpa template statis
    """
    try:
        user = update.effective_user
        user_message = update.message.text
        user_id = user.id
        
        # Cek apakah ada karakter aktif
        current_reg = context.user_data.get('current_registration')
        
        if not current_reg:
            await update.message.reply_text(
                "❌ **Tidak ada karakter aktif**\n\n"
                "Ketik `/start` untuk memilih karakter, atau `/sessions` untuk melanjutkan karakter tersimpan.\n\n"
                "_Masih bingung? Ketik /help untuk bantuan._",
                parse_mode='HTML'
            )
            return
        
        registration_id = current_reg.get('id')
        
        # Cek pause
        if context.user_data.get('paused', False):
            await update.message.reply_text(
                "⏸️ **Sesi dijeda**\n\n"
                "Ketik `/unpause` untuk melanjutkan.",
                parse_mode='HTML'
            )
            return
        
        # Dapatkan atau buat AI Engine
        if registration_id not in _active_engines:
            identity_manager = IdentityManager()
            character = await identity_manager.get_character(registration_id)
            
            if not character:
                await update.message.reply_text(
                    "❌ **Karakter tidak ditemukan**\n\n"
                    "Ketik `/sessions` untuk melihat karakter tersimpan.",
                    parse_mode='HTML'
                )
                return
            
            ai_engine = AIEngine(character)
            _active_engines[registration_id] = ai_engine
            
            logger.info(f"✅ AI Engine created for {registration_id}")
        
        ai_engine = _active_engines[registration_id]
        
        # Dapatkan state terbaru
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
        
        # Kirim respons
        await update.message.reply_text(response, parse_mode='HTML')
        
        # Update progress setelah chat
        await _update_progress(registration_id, ai_engine)
        
        # Update context
        context.user_data['last_message_time'] = time.time()
        context.user_data['last_message'] = user_message
        context.user_data['last_response'] = response
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            "❌ **Terjadi kesalahan**\n\n"
            "Maaf, aku mengalami gangguan. Coba lagi nanti ya, Mas.\n\n"
            "_Jika error berlanjut, laporkan ke admin._",
            parse_mode='HTML'
        )


async def _update_progress(registration_id: str, ai_engine: AIEngine) -> None:
    """
    Update progress setelah chat
    """
    try:
        identity_manager = IdentityManager()
        character = await identity_manager.get_character(registration_id)
        
        if not character:
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
            
            # Trigger level up effect
            if new_level == 7:
                # Bisa intim
                pass
            elif new_level == 11:
                # Soul Bounded
                pass
            elif new_level == 12:
                # Aftercare
                pass
        
        # Stamina recovery
        stamina = StaminaSystem()
        stamina.check_recovery()
        character.stamina_bot = stamina.bot_stamina.current
        character.stamina_user = stamina.user_stamina.current
        
        # Save to database
        db_reg = character.to_db_registration()
        await identity_manager.repo.update_registration(db_reg)
        
        # Save state
        state = await identity_manager.get_character_state(registration_id)
        if state:
            state.updated_at = time.time()
            await identity_manager.repo.save_state(state)
        
    except Exception as e:
        logger.error(f"Error updating progress: {e}")


async def continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk melanjutkan session (internal)
    """
    await update.message.reply_text(
        "🔄 **Melanjutkan session...**\n\n"
        "Gunakan `/sessions` untuk melihat daftar session yang tersimpan.",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /help - Bantuan lengkap
    """
    user_id = update.effective_user.id
    is_admin = (user_id == settings.admin_id)
    
    help_text = (
        "📚 **BANTUAN AMORIA**\n\n"
        "<b>Basic Commands:</b>\n"
        "/start - Mulai bot & pilih karakter\n"
        "/help - Bantuan lengkap\n"
        "/status - Status hubungan saat ini\n"
        "/progress - Progress leveling\n"
        "/cancel - Batalkan percakapan\n\n"
        "<b>Session Commands:</b>\n"
        "/close - Tutup & simpan karakter\n"
        "/end - Akhiri karakter total\n"
        "/sessions - Lihat semua karakter tersimpan\n"
        "/character [role] [nomor] - Lanjutkan karakter\n\n"
        "<b>Character Commands:</b>\n"
        "/character-list - Lihat semua karakter\n"
        "/character-pause - Jeda karakter\n"
        "/character-resume - Lanjutkan karakter\n"
        "/character-stop - Hentikan karakter\n\n"
        "<b>Ex & FWB Commands:</b>\n"
        "/ex-list - Lihat daftar mantan\n"
        "/ex [nomor] - Detail mantan\n"
        "/fwb-request [nomor] - Request jadi FWB\n"
        "/fwb-list - Lihat daftar FWB\n"
        "/fwb-pause [nomor] - Jeda FWB\n"
        "/fwb-resume [nomor] - Lanjutkan FWB\n"
        "/fwb-end [nomor] - Akhiri FWB\n\n"
        "<b>HTS Commands:</b>\n"
        "/hts-list - Lihat TOP 10 HTS\n"
        "/hts-[nomor] - Panggil HTS untuk intim\n\n"
        "<b>Public Area Commands:</b>\n"
        "/explore - Cari lokasi random\n"
        "/locations - Lihat semua lokasi\n"
        "/risk - Cek risk lokasi saat ini\n"
        "/go [lokasi] - Pindah ke lokasi\n\n"
        "<b>Memory Commands:</b>\n"
        "/memory - Ringkasan memory\n"
        "/flashback - Flashback random\n\n"
        "<b>Ranking Commands:</b>\n"
        "/top-hts - TOP 5 ranking HTS\n"
        "/my-climax - Statistik climax pribadi\n"
        "/climax-history - History climax"
    )
    
    # Admin commands
    if is_admin:
        help_text += (
            "\n\n<b>Admin Commands:</b>\n"
            "/admin - Panel admin\n"
            "/stats - Statistik bot\n"
            "/db-stats - Statistik database\n"
            "/backup - Backup manual\n"
            "/recover - Restore dari backup\n"
            "/debug - Info debug"
        )
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def status_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /status - Alias ke status_command di command/status.py
    """
    await status_command(update, context)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /cancel - Batalkan percakapan
    """
    # Clear pending data
    context.user_data.pop('pending_action', None)
    
    await update.message.reply_text(
        "❌ **Dibatalkan**\n\n"
        "Percakapan dibatalkan. Ketik pesan untuk memulai lagi.",
        parse_mode='HTML'
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global error handler untuk semua error di bot
    """
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


# Export all handlers
__all__ = [
    'message_handler',
    'continue_handler',
    'help_command',
    'status_command_handler',
    'cancel_command',
    'error_handler',
    '_active_engines'
]
