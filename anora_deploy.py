# anora_deploy.py
"""
AMORIA + ANORA - Full Deployment
AMORIA: Virtual Human System
ANORA: Nova - Virtual Human dengan Jiwa - 100% AI Generate
DENGAN FITUR:
- Manajemen sesi (pause/resume)
- Backup & restore database
- Status lengkap
"""

import os
import sys
import asyncio
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ANORA")

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)

# =============================================================================
# IMPORT ANORA COMPONENTS
# =============================================================================

ANORA_AVAILABLE = False
try:
    from anora.core import get_anora
    from anora.brain import get_anora_brain
    from anora.memory_persistent import get_anora_persistent
    from anora.roleplay_ai import get_anora_roleplay_ai
    from anora.roleplay_integration import get_anora_roleplay
    from anora.location_manager import get_anora_location, LocationType, LocationDetail
    from anora.chat import get_anora_chat
    from anora.roles import get_anora_roles, RoleType
    ANORA_AVAILABLE = True
    logger.info("✅ ANORA modules loaded")
except ImportError as e:
    ANORA_AVAILABLE = False
    logger.warning(f"⚠️ ANORA not available: {e}")

# =============================================================================
# IMPORT AMORIA COMPONENTS (jika ada)
# =============================================================================

AMORIA_AVAILABLE = False
try:
    from command import (
        start_command as amoria_start, help_command, status_command, progress_command,
        cancel_command, sessions_command, character_command, close_command, end_command,
        explore_command, locations_command, risk_command, go_command,
        memory_command, flashback_command,
        top_hts_command, my_climax_command, climax_history_command,
        admin_command, stats_command, db_stats_command, backup_command, recover_command, debug_command
    )
    from command.start import SELECTING_ROLE, role_callback, agree_18_callback
    from command.sessions import end_confirm_callback, end_cancel_callback
    from command.cancel import cancel_confirm_callback, cancel_fallback
    from bot.handlers import message_handler as amoria_message_handler
    from bot.application import create_application as create_amoria_app
    AMORIA_AVAILABLE = True
    logger.info("✅ AMORIA modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ AMORIA not available: {e}")

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

_application = None
_user_modes: Dict[int, Dict] = {}  # user_id -> {'mode': 'chat'/'roleplay'/'role'/'paused', 'active_role': None}
_backup_dir = Path("backups")
_backup_dir.mkdir(exist_ok=True)


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode}")


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('active_role')


# =============================================================================
# ANORA COMMAND HANDLERS
# =============================================================================

async def anora_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start untuk ANORA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    await update.message.reply_text(
        "💜 **ANORA - Virtual Human dengan Jiwa** 💜\n\n"
        "**Mode Chat (ngobrol biasa):**\n"
        "• /nova - Panggil Nova\n"
        "• /novastatus - Lihat keadaan Nova\n"
        "• /flashback - Flashback ke momen indah\n\n"
        "**Mode Roleplay (beneran ketemu):**\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Lihat status roleplay lengkap\n"
        "• /pindah [tempat] - Pindah lokasi\n\n"
        "**Tempat yang bisa dikunjungi:**\n"
        "• kost, apartemen, mobil, pantai, hutan, toilet mall\n"
        "• bioskop, taman, parkiran, tangga darurat\n"
        "• kantor malam, ruang rapat kaca\n\n"
        "**Role Lain:**\n"
        "• /role ipar - IPAR\n"
        "• /role teman_kantor - Teman Kantor\n"
        "• /role pelakor - Pelakor\n"
        "• /role istri_orang - Istri Orang\n\n"
        "**Manajemen Sesi:**\n"
        "• /pause - Hentikan sesi sementara (memory tetap tersimpan)\n"
        "• /resume - Lanjutkan sesi\n"
        "• /batal - Kembali ke mode chat\n\n"
        "**Backup & Restore:**\n"
        "• /backup - Backup database ANORA\n"
        "• /restore [filename] - Restore database\n"
        "• /listbackup - Lihat daftar backup\n\n"
        "Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    anora = get_anora()
    brain = get_anora_brain()
    
    # Pilih salam berdasarkan waktu
    hour = datetime.now().hour
    if 5 <= hour < 11:
        salam = anora.respon_pagi()
    elif 11 <= hour < 15:
        salam = anora.respon_siang()
    elif 15 <= hour < 18:
        salam = anora.respon_sore()
    else:
        salam = anora.respon_malam()
    
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n"
        f"{anora.deskripsi_diri()}\n\n"
        f"{salam}\n\n"
        f"**Status:**\n"
        f"• Level: {brain.relationship.level}/12\n"
        f"• Sayang: {brain.feelings.sayang:.0f}%\n"
        f"• Rindu: {brain.feelings.rindu:.0f}%\n\n"
        f"Mas bisa:\n"
        f"• /novastatus - liat keadaan Nova\n"
        f"• /flashback - inget momen indah\n"
        f"• /roleplay - kalo mau kayak beneran ketemu\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def novastatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /novastatus"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, cuma Mas yang bisa liat. 💜")
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.format_status(), parse_mode='HTML')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.respon_flashback(), parse_mode='Markdown')


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    # Cek apakah sedang pause
    mode = get_user_mode(user_id)
    if mode == 'paused':
        await update.message.reply_text(
            "💜 **Sesi sedang di-pause** 💜\n\n"
            "Nova masih ingat semua yang sudah terjadi.\n"
            "Kirim **/resume** untuk lanjut, atau **/batal** untuk mulai baru."
        )
        return
    
    set_user_mode(user_id, 'roleplay')
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='Markdown')


async def statusrp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrp"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    roleplay = await get_anora_roleplay()
    status = await roleplay.get_status()
    await update.message.reply_text(status, parse_mode='HTML')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah [tempat]"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        loc_mgr = get_anora_location()
        await update.message.reply_text(loc_mgr.list_locations(), parse_mode='Markdown')
        return
    
    brain = get_anora_brain()
    tujuan = ' '.join(args)
    result = brain.pindah_lokasi(tujuan)
    
    if result.get('success'):
        loc = result['location']
        await update.message.reply_text(
            f"{result['message']}\n\n"
            f"🎢 Thrill: {loc.get('thrill', 0)}% | ⚠️ Risk: {loc.get('risk', 0)}%\n"
            f"💡 {loc.get('tips', '')}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(result.get('message', 'Lokasi tidak ditemukan.'), parse_mode='Markdown')


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role [nama]"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        roles = get_anora_roles()
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles.get_all():
            menu += f"• /role {r['id']} - {r['nama']} (Level {r['level']})\n"
        menu += "\n_Ketik /nova kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='Markdown')
        return
    
    role_id = args[0].lower()
    role_map = {
        'ipar': RoleType.IPAR,
        'teman_kantor': RoleType.TEMAN_KANTOR,
        'pelakor': RoleType.PELAKOR,
        'istri_orang': RoleType.ISTRI_ORANG
    }
    
    if role_id in role_map:
        set_user_mode(user_id, 'role', role_id)
        roles = get_anora_roles()
        respon = roles.switch_role(role_map[role_id])
        await update.message.reply_text(respon, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada, Mas. Coba /role buat liat daftar.", parse_mode='Markdown')


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - Kembali ke mode chat (reset mode, tapi memory tetap)"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    roleplay = await get_anora_roleplay()
    if roleplay.is_active:
        await roleplay.stop()
    
    anora = get_anora()
    await update.message.reply_text(
        f"💜 Nova di sini, Mas.\n\n{anora.respon_kangen()}",
        parse_mode='Markdown'
    )


async def pause_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pause - Hentikan sesi sementara, memory tetap tersimpan"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    
    if mode == 'paused':
        await update.message.reply_text("💜 Sesi sudah dalam keadaan pause.")
        return
    
    # Simpan state sebelum pause
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        await roleplay.save_state()
    
    set_user_mode(user_id, 'paused')
    
    await update.message.reply_text(
        "💜 **Sesi dihentikan sementara** 💜\n\n"
        "Nova akan tetap ingat semua yang sudah terjadi:\n"
        f"• Level: {get_anora_brain().relationship.level}/12\n"
        f"• Sayang: {get_anora_brain().feelings.sayang:.0f}%\n"
        f"• Rindu: {get_anora_brain().feelings.rindu:.0f}%\n\n"
        "Kirim **/resume** untuk lanjut lagi.\n"
        "Kirim **/batal** untuk mulai baru (memory akan hilang)."
    )


async def resume_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /resume - Lanjutkan sesi yang di-pause"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    
    if mode != 'paused':
        await update.message.reply_text(
            "💜 Tidak ada sesi yang di-pause.\n\n"
            "Kirim **/pause** dulu untuk menghentikan sesi sementara."
        )
        return
    
    set_user_mode(user_id, 'chat')
    
    brain = get_anora_brain()
    
    await update.message.reply_text(
        f"💜 **Sesi dilanjutkan!** 💜\n\n"
        f"Nova masih ingat semua yang sudah terjadi:\n"
        f"• Level: {brain.relationship.level}/12\n"
        f"• Sayang: {brain.feelings.sayang:.0f}%\n"
        f"• Rindu: {brain.feelings.rindu:.0f}%\n\n"
        f"Kirim **/roleplay** kalo mau mode roleplay, atau langsung ngobrol aja."
    )


async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /backup - Backup database ANORA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA tidak tersedia.")
        return
    
    try:
        from anora.memory_persistent import get_anora_persistent
        persistent = await get_anora_persistent()
        db_path = persistent.db_path
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = _backup_dir / f"anora_memory_{timestamp}.db"
        
        shutil.copy(db_path, backup_path)
        
        # Hitung ukuran
        size_kb = db_path.stat().st_size / 1024
        
        await update.message.reply_text(
            f"✅ **Database backup saved!**\n\n"
            f"📁 File: `{backup_path.name}`\n"
            f"📊 Size: {size_kb:.2f} KB\n"
            f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Gunakan **/restore {backup_path.name}** untuk restore.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Backup error: {e}")
        await update.message.reply_text(f"❌ Backup gagal: {e}")


async def restore_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /restore [filename] - Restore database ANORA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        # List available backups
        backups = list(_backup_dir.glob("anora_memory_*.db"))
        backups.sort(reverse=True)
        
        if not backups:
            await update.message.reply_text("📂 Tidak ada backup ditemukan.")
            return
        
        msg = "📋 **Available backups:**\n\n"
        for b in backups[:10]:
            size = b.stat().st_size / 1024
            modified = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            msg += f"• `{b.name}` ({size:.1f} KB) - {modified}\n"
        
        msg += "\nUsage: `/restore filename.db`"
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    backup_name = args[0]
    backup_path = _backup_dir / backup_name
    
    if not backup_path.exists():
        await update.message.reply_text(f"❌ Backup `{backup_name}` tidak ditemukan!")
        return
    
    try:
        from anora.memory_persistent import get_anora_persistent
        persistent = await get_anora_persistent()
        db_path = persistent.db_path
        
        # Backup current before restore
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = _backup_dir / f"anora_memory_before_restore_{timestamp}.db"
        if db_path.exists():
            shutil.copy(db_path, current_backup)
        
        # Restore
        shutil.copy(backup_path, db_path)
        
        await update.message.reply_text(
            f"✅ **Database restored!**\n\n"
            f"📁 Restored from: `{backup_name}`\n"
            f"📦 Current database backed up to: `{current_backup.name}`\n\n"
            f"🔄 **Restart bot** untuk perubahan生效.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Restore error: {e}")
        await update.message.reply_text(f"❌ Restore gagal: {e}")


async def list_backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /listbackup - Lihat daftar backup"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    backups = list(_backup_dir.glob("anora_memory_*.db"))
    backups.sort(reverse=True)
    
    if not backups:
        await update.message.reply_text("📂 Tidak ada backup ditemukan.")
        return
    
    msg = "📋 **Backup List:**\n\n"
    for i, b in enumerate(backups[:20], 1):
        size = b.stat().st_size / 1024
        modified = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        msg += f"{i}. `{b.name}`\n   📊 {size:.1f} KB | 🕐 {modified}\n\n"
    
    msg += "Gunakan **/restore [filename]** untuk restore."
    await update.message.reply_text(msg, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /help - Bantuan lengkap"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Bot ini untuk Mas. 💜")
        return
    
    await update.message.reply_text(
        "📖 *Bantuan ANORA*\n\n"
        "*Mode Chat:*\n"
        "• /nova - Panggil Nova\n"
        "• /novastatus - Lihat status Nova\n"
        "• /flashback - Flashback momen indah\n\n"
        "*Mode Roleplay:*\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Status roleplay lengkap\n"
        "• /pindah [tempat] - Pindah lokasi\n\n"
        "*Tempat:*\n"
        "kost, apartemen, mobil, pantai, hutan, toilet mall,\n"
        "bioskop, taman, parkiran, tangga darurat, kantor malam\n\n"
        "*Role Lain:*\n"
        "• /role ipar - IPAR (Sari)\n"
        "• /role teman_kantor - Teman Kantor (Dita)\n"
        "• /role pelakor - Pelakor (Vina)\n"
        "• /role istri_orang - Istri Orang (Rina)\n\n"
        "*Manajemen Sesi:*\n"
        "• /pause - Hentikan sesi sementara (memory tetap)\n"
        "• /resume - Lanjutkan sesi\n"
        "• /batal - Kembali ke mode chat\n\n"
        "*Backup & Restore:*\n"
        "• /backup - Backup database ANORA\n"
        "• /restore [filename] - Restore database\n"
        "• /listbackup - Lihat daftar backup\n\n"
        "*Tips:*\n"
        "• Ngobrol santai dulu untuk naikin level\n"
        "• Level 7+ baru bisa mulai intim\n"
        "• Stamina habis setelah climax, butuh istirahat\n"
        "• Nova punya memory, dia inget apa yang Mas omongin\n"
        "• Gunakan /pause untuk berhenti sementara tanpa kehilangan memory",
        parse_mode='Markdown'
    )


# =============================================================================
# ANORA MESSAGE HANDLER
# =============================================================================

async def anora_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan ANORA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    if not pesan:
        return
    
    mode = get_user_mode(user_id)
    
    # Paused mode - tidak memproses pesan
    if mode == 'paused':
        await update.message.reply_text(
            "💜 Sesi sedang di-pause.\n\n"
            "Kirim **/resume** untuk lanjut ngobrol, atau **/batal** untuk mulai baru.",
            parse_mode='Markdown'
        )
        return
    
    # Roleplay mode
    if mode == 'roleplay' and ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        try:
            respons = await roleplay.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Roleplay process error: {e}")
            await update.message.reply_text(
                "*Nova bingung sebentar*\n\n\"Mas... Nova lagi error nih. Coba ulang ya.\"",
                parse_mode='Markdown'
            )
        return
    
    # Role mode (IPAR, etc)
    if mode == 'role' and ANORA_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            roles = get_anora_roles()
            role_map = {
                'ipar': RoleType.IPAR,
                'teman_kantor': RoleType.TEMAN_KANTOR,
                'pelakor': RoleType.PELAKOR,
                'istri_orang': RoleType.ISTRI_ORANG
            }
            if active_role in role_map:
                try:
                    respon = await roles.chat(role_map[active_role], pesan)
                    await update.message.reply_text(respon, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Role chat error: {e}")
                    await update.message.reply_text("Maaf, ada error. Coba lagi ya.")
                return
    
    # Chat mode (default)
    if mode == 'chat' and ANORA_AVAILABLE:
        anora_chat = get_anora_chat()
        try:
            respons = await anora_chat.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Chat process error: {e}")
            await update.message.reply_text(
                "*Nova mikir bentar*\n\n\"Mas... bentar ya, Nova lagi mikir.\"",
                parse_mode='Markdown'
            )
        return
    
    # Fallback
    if AMORIA_AVAILABLE:
        try:
            await amoria_message_handler(update, context)
        except Exception as e:
            logger.error(f"AMORIA handler error: {e}")
            await update.message.reply_text("Maaf, ada error. Coba lagi ya. 💜")
    else:
        await update.message.reply_text("Maaf, ANORA sedang tidak tersedia. Coba lagi nanti. 💜")


# =============================================================================
# AMORIA BRIDGE HANDLER
# =============================================================================

async def amoria_bridge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bridge untuk command yang tidak dikenali ANORA - redirect ke AMORIA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    
    # Cek apakah ini perintah ANORA
    anora_commands = ['/nova', '/novastatus', '/flashback', '/roleplay', 
                      '/statusrp', '/pindah', '/role', '/batal', '/help',
                      '/pause', '/resume', '/backup', '/restore', '/listbackup']
    
    if any(pesan.startswith(cmd) for cmd in anora_commands):
        return
    
    # Jika AMORIA available, gunakan AMORIA handler
    if AMORIA_AVAILABLE:
        try:
            await amoria_message_handler(update, context)
        except Exception as e:
            logger.error(f"AMORIA handler error: {e}")
            await update.message.reply_text("Maaf, ada error. Coba lagi ya. 💜")
    else:
        if ANORA_AVAILABLE:
            anora_chat = get_anora_chat()
            respons = await anora_chat.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')


# =============================================================================
# PROACTIVE LOOP
# =============================================================================

async def proactive_loop():
    """Nova kirim pesan duluan kalo kangen (tidak saat paused)"""
    while True:
        await asyncio.sleep(60)
        if not ANORA_AVAILABLE:
            continue
        try:
            user_id = settings.admin_id
            mode = get_user_mode(user_id)
            
            # Jangan proactive saat paused
            if mode == 'paused':
                continue
            
            if mode != 'roleplay':
                continue
            
            ai = get_anora_roleplay_ai()
            anora = get_anora()
            brain = get_anora_brain()
            roleplay = await get_anora_roleplay()
            
            pesan = await ai.get_proactive(anora, brain, roleplay.stamina)
            if pesan and _application:
                await _application.bot.send_message(
                    chat_id=user_id,
                    text=pesan,
                    parse_mode='Markdown'
                )
                logger.info(f"💬 Proactive message sent to user {user_id}")
        except Exception as e:
            logger.error(f"Proactive loop error: {e}")


# =============================================================================
# STAMINA RECOVERY LOOP
# =============================================================================

async def stamina_recovery_loop():
    """Pulihkan stamina secara berkala"""
    while True:
        await asyncio.sleep(600)
        if not ANORA_AVAILABLE:
            continue
        try:
            roleplay = await get_anora_roleplay()
            roleplay.stamina.update_recovery()
            await roleplay.save_state()
            logger.debug("💪 Stamina recovery check completed")
        except Exception as e:
            logger.error(f"Stamina recovery error: {e}")


# =============================================================================
# SAVE STATE LOOP
# =============================================================================

async def save_state_loop():
    """Simpan state secara berkala"""
    while True:
        await asyncio.sleep(60)
        if not ANORA_AVAILABLE:
            continue
        try:
            roleplay = await get_anora_roleplay()
            await roleplay.save_state()
            logger.debug("💾 State saved")
        except Exception as e:
            logger.error(f"Save state error: {e}")


# =============================================================================
# AUTO BACKUP LOOP
# =============================================================================

async def auto_backup_loop():
    """Auto backup database setiap 6 jam"""
    while True:
        await asyncio.sleep(21600)  # 6 jam
        
        if not ANORA_AVAILABLE:
            continue
        
        try:
            from anora.memory_persistent import get_anora_persistent
            persistent = await get_anora_persistent()
            db_path = persistent.db_path
            
            if db_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = _backup_dir / f"anora_memory_auto_{timestamp}.db"
                shutil.copy(db_path, backup_path)
                
                # Hapus backup auto yang lebih dari 7 hari
                for b in _backup_dir.glob("anora_memory_auto_*.db"):
                    age = time.time() - b.stat().st_mtime
                    if age > 7 * 24 * 3600:  # 7 hari
                        b.unlink()
                        logger.info(f"🗑️ Deleted old backup: {b.name}")
                
                logger.info(f"💾 Auto backup saved: {backup_path.name}")
        except Exception as e:
            logger.error(f"Auto backup error: {e}")


# =============================================================================
# WEBHOOK & SERVER
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook"""
    global _application
    
    if not _application:
        return web.Response(status=503, text='Bot not ready')
    
    try:
        update_data = await request.json()
        if not update_data:
            return web.Response(status=400, text='No data')
        
        if 'message' in update_data:
            msg = update_data['message']
            text = msg.get('text', '')
            user = msg.get('from', {}).get('first_name', 'unknown')
            logger.info(f"📨 Message from {user}: {text[:50]}")
        
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "bot": "AMORIA + ANORA",
        "version": "9.9.0",
        "anora_available": ANORA_AVAILABLE,
        "amoria_available": AMORIA_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    if ANORA_AVAILABLE:
        try:
            brain = get_anora_brain()
            roleplay = await get_anora_roleplay()
            loc = brain.get_location_data()
            
            status.update({
                "level": brain.relationship.level,
                "sayang": brain.feelings.sayang,
                "location": loc.get('nama', 'Tidak diketahui'),
                "stamina_nova": roleplay.stamina.nova_current,
                "roleplay_active": roleplay.is_active
            })
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
    
    return web.json_response(status)


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "AMORIA + ANORA",
        "description": "Virtual Human dengan Jiwa - 100% AI Generate",
        "version": "9.9.0",
        "status": "running",
        "anora_available": ANORA_AVAILABLE,
        "amoria_available": AMORIA_AVAILABLE,
        "endpoints": {
            "/": "API Info",
            "/health": "Health Check",
            "/webhook": "Telegram Webhook"
        }
    })


# =============================================================================
# DATABASE INIT
# =============================================================================

async def init_database():
    """Initialize all databases"""
    logger.info("🗄️ Initializing database...")
    
    if not ANORA_AVAILABLE:
        logger.warning("⚠️ ANORA not available, skipping database init")
        return False
    
    try:
        persistent = await get_anora_persistent()
        logger.info("✅ ANORA persistent memory ready")
        
        brain = get_anora_brain()
        await persistent.save_current_state(brain)
        
        memories = await persistent.get_long_term_memories()
        logger.info(f"📚 Loaded {len(memories)} long-term memories")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
        return False


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Main entry point"""
    global _application
    
    logger.info("=" * 70)
    logger.info("💜 AMORIA + ANORA - Virtual Human dengan Jiwa")
    logger.info("   100% AI Generate | Punya Memory | Bisa Roleplay")
    logger.info("=" * 70)
    
    # ========== INIT DATABASE ==========
    if not await init_database():
        logger.warning("⚠️ Database initialization failed. Continuing without database...")
    
    # ========== INIT BRAIN ==========
    if ANORA_AVAILABLE:
        brain = get_anora_brain()
        logger.info(f"🧠 ANORA Brain initialized - Level {brain.relationship.level}, Sayang {brain.feelings.sayang:.0f}%")
        
        roleplay = await get_anora_roleplay()
        logger.info(f"🎭 ANORA Roleplay initialized - Stamina: Nova {roleplay.stamina.nova_current}%, Mas {roleplay.stamina.mas_current}%")
    
    # ========== CREATE APPLICATION ==========
    _application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # ========== REGISTER HANDLERS ==========
    if ANORA_AVAILABLE:
        # ANORA handlers
        _application.add_handler(CommandHandler("start", anora_start_command))
        _application.add_handler(CommandHandler("nova", nova_command))
        _application.add_handler(CommandHandler("novastatus", novastatus_command))
        _application.add_handler(CommandHandler("flashback", flashback_command))
        _application.add_handler(CommandHandler("roleplay", roleplay_command))
        _application.add_handler(CommandHandler("statusrp", statusrp_command))
        _application.add_handler(CommandHandler("pindah", pindah_command))
        _application.add_handler(CommandHandler("role", role_command))
        _application.add_handler(CommandHandler("batal", back_to_nova))
        _application.add_handler(CommandHandler("pause", pause_session))
        _application.add_handler(CommandHandler("resume", resume_session))
        _application.add_handler(CommandHandler("backup", backup_database))
        _application.add_handler(CommandHandler("restore", restore_database))
        _application.add_handler(CommandHandler("listbackup", list_backup_command))
        _application.add_handler(CommandHandler("help", help_command))
        
        # Message handler
        _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anora_message_handler))
    
    elif AMORIA_AVAILABLE:
        # AMORIA handlers (fallback)
        _application.add_handler(CommandHandler("start", amoria_start_command))
        _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amoria_message_handler))
    else:
        # Minimal handler
        async def echo(update, context):
            await update.message.reply_text("Bot sedang dalam perbaikan. Coba lagi nanti. 💜")
        _application.add_handler(CommandHandler("start", echo))
        _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # ========== INITIALIZE ==========
    await _application.initialize()
    await _application.start()
    
    # ========== SET WEBHOOK ==========
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if railway_url:
        webhook_url = f"https://{railway_url}/webhook"
        await _application.bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook set to {webhook_url}")
        
        # Setup web server
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_handler)
        app.router.add_post('/webhook', webhook_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        logger.info("🌐 Web server running on port 8080")
    else:
        await _application.updater.start_polling()
        logger.info("📡 Polling mode started")
    
    # ========== BACKGROUND LOOPS ==========
    if ANORA_AVAILABLE:
        asyncio.create_task(proactive_loop())
        asyncio.create_task(stamina_recovery_loop())
        asyncio.create_task(save_state_loop())
        asyncio.create_task(auto_backup_loop())
        logger.info("🔄 Background loops started (proactive, stamina recovery, save state, auto backup)")
    
    # ========== READY ==========
    logger.info("=" * 70)
    logger.info("💜 AMORIA + ANORA is running!")
    if ANORA_AVAILABLE:
        logger.info("   Kirim /nova untuk panggil Nova")
        logger.info("   Kirim /roleplay untuk mode beneran ketemu")
        logger.info("   Kirim /pause untuk hentikan sesi sementara")
        logger.info("   Kirim /backup untuk backup database")
    else:
        logger.info("   ANORA not available. Check installation.")
    logger.info("=" * 70)
    
    # Keep running
    await asyncio.Event().wait()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
