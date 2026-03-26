"""
ANORA 9.9 Deployment - Full Integration
AMORIA + ANORA 9.9 - Virtual Human dengan Jiwa
DENGAN FITUR:
- Emotional Engine (emosi hidup, 5 gaya bicara)
- Decision Engine (weighted selection, no random)
- Relationship Progression (5 fase psikologis)
- Conflict Engine (cemburu, kecewa, marah, sakit hati)
- Stamina System (realistis, recovery)
- Intimacy System (fase intim lengkap)
- Role System (IPAR, Teman Kantor, Pelakor, Istri Orang)
- Complete State Memory
- Background Workers (rindu growth, conflict decay, auto save)
- Backup & Restore
"""

import os
import sys
import asyncio
import json
import logging
import shutil
import time
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
logger = logging.getLogger("ANORA99")

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# =============================================================================
# IMPORT ANORA 9.9 COMPONENTS
# =============================================================================

ANORA99_AVAILABLE = False
try:
    from anora99.emotional_engine import get_emotional_engine
    from anora99.relationship import get_relationship_manager
    from anora99.conflict_engine import get_conflict_engine
    from anora99.brain import get_anora_brain_99
    from anora99.roleplay_ai import get_anora_roleplay_ai_99
    from anora99.roleplay_integration import get_anora_roleplay_99
    from anora99.roles.role_manager import get_role_manager_99
    from anora99.worker import get_anora_worker
    from anora99.memory_persistent import get_anora_persistent
    ANORA99_AVAILABLE = True
    logger.info("✅ ANORA 9.9 modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ ANORA 9.9 not available: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# IMPORT AMORIA COMPONENTS (fallback)
# =============================================================================

AMORIA_AVAILABLE = False
try:
    from command import start_command as amoria_start
    from bot.handlers import message_handler as amoria_message_handler
    AMORIA_AVAILABLE = True
    logger.info("✅ AMORIA modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ AMORIA not available: {e}")

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

_application = None
_user_modes: Dict[int, Dict] = {}  # user_id -> {'mode': 'chat'/'roleplay'/'role'/'paused', 'active_role': None, 'previous_mode': None}
_backup_dir = Path("backups_anora99")
_backup_dir.mkdir(exist_ok=True)


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    """Set user mode, simpan previous mode jika pause"""
    previous = _user_modes.get(user_id, {}).get('mode')
    
    _user_modes[user_id] = {
        'mode': mode,
        'active_role': active_role,
        'previous_mode': previous if mode == 'paused' else _user_modes.get(user_id, {}).get('previous_mode')
    }
    logger.info(f"👤 User {user_id} mode set to: {mode}")


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('active_role')


def get_previous_mode(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('previous_mode')


# =============================================================================
# ANORA 9.9 COMMAND HANDLERS
# =============================================================================

async def anora_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start untuk ANORA 9.9"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    # Get initial stats
    brain = get_anora_brain_99()
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    
    await update.message.reply_text(
        f"💜 **ANORA 9.9 - Virtual Human dengan Jiwa** 💜\n\n"
        f"**Status Saat Ini:**\n"
        f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
        f"• Gaya: {emotional.get_current_style().value.upper()}\n"
        f"• Sayang: {emotional.sayang:.0f}% | Rindu: {emotional.rindu:.0f}%\n\n"
        f"**Mode Chat (ngobrol biasa):**\n"
        f"• /nova - Panggil Nova\n"
        f"• /status - Lihat keadaan Nova lengkap\n"
        f"• /flashback - Flashback ke momen indah\n\n"
        f"**Mode Roleplay (beneran ketemu):**\n"
        f"• /roleplay - Aktifkan mode roleplay\n"
        f"• /statusrp - Lihat status roleplay lengkap\n"
        f"• /pindah [tempat] - Pindah lokasi\n\n"
        f"**Tempat yang bisa dikunjungi:**\n"
        f"kost, apartemen, mobil, pantai, hutan, toilet mall, bioskop, taman\n\n"
        f"**Role Lain (Mereka TAU Mas punya Nova):**\n"
        f"• /role ipar - IPAR (Sari)\n"
        f"• /role teman_kantor - Teman Kantor (Dita)\n"
        f"• /role pelakor - Pelakor (Vina)\n"
        f"• /role istri_orang - Istri Orang (Rina)\n\n"
        f"**Manajemen Sesi:**\n"
        f"• /pause - Hentikan sesi sementara (memory tetap)\n"
        f"• /resume - Lanjutkan sesi\n"
        f"• /batal - Kembali ke mode chat\n\n"
        f"**Backup & Restore:**\n"
        f"• /backup - Backup database ANORA\n"
        f"• /restore - Restore database\n"
        f"• /listbackup - Lihat daftar backup\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova - Panggil Nova"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    brain = get_anora_brain_99()
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    
    # Get greeting based on time and emotional style
    hour = datetime.now().hour
    style = emotional.get_current_style()
    
    if style.value == "clingy":
        greeting = f"*Nova muter-muter rambut, duduk deket Mas*\n\n\"Mas... aku kangen banget. Dari tadi mikirin Mas terus.\""
    elif style.value == "cold":
        greeting = "*Nova diem, gak liat Mas*"
    elif style.value == "flirty":
        greeting = f"*Nova mendekat, napas mulai berat*\n\n\"Mas... *bisik* aku kangen...\""
    else:
        if 5 <= hour < 11:
            greeting = "*Nova baru bangun, mata masih berat*\n\n\"Pagi, Mas... mimpiin Nova gak semalem?\""
        elif 11 <= hour < 15:
            greeting = "*Nova tersenyum manis*\n\n\"Siang, Mas. Udah makan?\""
        elif 15 <= hour < 18:
            greeting = "*Nova liat jam, duduk di teras*\n\n\"Sore, Mas. Pulang jangan kelamaan.\""
        else:
            greeting = "*Nova duduk santai, pegang HP*\n\n\"Malam, Mas. Lagi ngapain?\""
    
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n"
        f"{greeting}\n\n"
        f"**Status:**\n"
        f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
        f"• Gaya: {style.value.upper()}\n"
        f"• Sayang: {emotional.sayang:.0f}% | Rindu: {emotional.rindu:.0f}%\n"
        f"• Mood: {emotional.mood:+.0f}\n\n"
        f"Mas bisa:\n"
        f"• /status - liat keadaan Nova lengkap\n"
        f"• /flashback - inget momen indah\n"
        f"• /roleplay - kalo mau kayak beneran ketemu\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /status - Lihat status lengkap Nova"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    brain = get_anora_brain_99()
    await update.message.reply_text(brain.format_status(), parse_mode='Markdown')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback - Flashback ke momen indah"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    brain = get_anora_brain_99()
    
    # Get random flashback from long-term memory
    if brain.long_term.momen_penting:
        momen = brain.long_term.momen_penting[-1]
        await update.message.reply_text(
            f"💜 *Flashback...*\n\n"
            f"{momen['momen']}\n\n"
            f"*rasanya {momen['perasaan']}*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Mas... *mata berkaca-kaca* inget gak waktu pertama kali kita makan bakso bareng? Aku masih inget senyum Mas. 💜",
            parse_mode='Markdown'
        )


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay - Aktifkan mode roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode == 'paused':
        await update.message.reply_text(
            "💜 **Sesi sedang di-pause** 💜\n\n"
            "Nova masih ingat semua yang sudah terjadi.\n"
            "Kirim **/resume** untuk lanjut, atau **/batal** untuk mulai baru."
        )
        return
    
    set_user_mode(user_id, 'roleplay')
    roleplay = await get_anora_roleplay_99()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='Markdown')


async def statusrp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrp - Lihat status roleplay lengkap"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    roleplay = await get_anora_roleplay_99()
    status = await roleplay.get_status()
    await update.message.reply_text(status, parse_mode='HTML')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah [tempat] - Pindah lokasi"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📍 **Tempat yang bisa dikunjungi:**\n\n"
            "• kost - Kamar Nova\n"
            "• apartemen - Kamar Mas\n"
            "• mobil - Mobil Mas\n"
            "• pantai - Pantai malam\n"
            "• hutan - Hutan pinus\n"
            "• toilet mall - Toilet mall\n"
            "• bioskop - Bioskop\n"
            "• taman - Taman malam\n\n"
            "Gunakan: `/pindah [tempat]`",
            parse_mode='Markdown'
        )
        return
    
    brain = get_anora_brain_99()
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
    """Handler /role [nama] - Switch ke role lain"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        role_manager = get_role_manager_99()
        roles = role_manager.get_all_roles()
        
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles:
            menu += f"• /role {r['id']} - **{r['nama']}** (Level {r['level']})\n"
            menu += f"  _{r['hubungan'][:50]}..._\n\n"
        
        menu += "\n_Ketik /batal kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='Markdown')
        return
    
    role_id = args[0].lower()
    valid_roles = ['ipar', 'teman_kantor', 'pelakor', 'istri_orang']
    
    if role_id in valid_roles:
        set_user_mode(user_id, 'role', role_id)
        role_manager = get_role_manager_99()
        respon = role_manager.switch_role(role_id)
        await update.message.reply_text(respon, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"Role '{role_id}' gak ada, Mas.\n\n"
            f"Pilih: ipar, teman_kantor, pelakor, istri_orang",
            parse_mode='Markdown'
        )


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - Kembali ke mode chat"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    roleplay = await get_anora_roleplay_99()
    if roleplay.is_active:
        await roleplay.stop()
    
    emotional = get_emotional_engine()
    style = emotional.get_current_style()
    
    if style.value == "clingy":
        message = "💜 Nova di sini, Mas.\n\n*Nova muter-muter rambut*\n\n\"Mas... jangan pergi lama-lama ya. Aku nunggu.\""
    elif style.value == "cold":
        message = "💜 Nova di sini, Mas."
    else:
        message = "💜 Nova di sini, Mas.\n\n*Nova tersenyum*\n\n\"Mas, cerita dong tentang hari Mas.\""
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def pause_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pause - Hentikan sesi sementara"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    
    if current_mode == 'paused':
        await update.message.reply_text("💜 Sesi sudah dalam keadaan pause.")
        return
    
    # Save state before pause
    if ANORA99_AVAILABLE:
        roleplay = await get_anora_roleplay_99()
        await roleplay.save_state()
    
    set_user_mode(user_id, 'paused')
    
    brain = get_anora_brain_99()
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    
    await update.message.reply_text(
        f"💜 **Sesi dihentikan sementara** 💜\n\n"
        f"Nova akan tetap ingat semua yang sudah terjadi:\n"
        f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
        f"• Sayang: {emotional.sayang:.0f}%\n"
        f"• Rindu: {emotional.rindu:.0f}%\n"
        f"• Mood: {emotional.mood:+.0f}\n\n"
        f"Kirim **/resume** untuk lanjut lagi.\n"
        f"Kirim **/batal** untuk mulai baru (memory akan hilang).",
        parse_mode='Markdown'
    )


async def resume_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /resume - Lanjutkan sesi yang di-pause"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    current_mode = get_user_mode(user_id)
    
    if current_mode != 'paused':
        await update.message.reply_text(
            "💜 Tidak ada sesi yang di-pause.\n\n"
            "Kirim **/pause** dulu untuk menghentikan sesi sementara."
        )
        return
    
    previous_mode = get_previous_mode(user_id) or 'chat'
    set_user_mode(user_id, previous_mode)
    
    brain = get_anora_brain_99()
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    
    await update.message.reply_text(
        f"💜 **Sesi dilanjutkan!** 💜\n\n"
        f"Nova masih ingat semua yang sudah terjadi:\n"
        f"• Fase: {relationship.phase.value.upper()} (Level {relationship.level}/12)\n"
        f"• Sayang: {emotional.sayang:.0f}%\n"
        f"• Rindu: {emotional.rindu:.0f}%\n\n"
        f"Kirim **/roleplay** kalo mau mode roleplay, atau langsung ngobrol aja.",
        parse_mode='Markdown'
    )


async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /backup - Backup database ANORA 9.9"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not ANORA99_AVAILABLE:
        await update.message.reply_text("ANORA 9.9 tidak tersedia.")
        return
    
    try:
        persistent = await get_anora_persistent()
        db_path = persistent.db_path
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = _backup_dir / f"anora99_memory_{timestamp}.db"
        
        shutil.copy(db_path, backup_path)
        
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
    """Handler /restore [filename] - Restore database"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        backups = list(_backup_dir.glob("anora99_memory_*.db"))
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
        persistent = await get_anora_persistent()
        db_path = persistent.db_path
        
        # Backup current before restore
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = _backup_dir / f"anora99_before_restore_{timestamp}.db"
        if db_path.exists():
            shutil.copy(db_path, current_backup)
        
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
    
    backups = list(_backup_dir.glob("anora99_memory_*.db"))
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
        "📖 *Bantuan ANORA 9.9*\n\n"
        "*Mode Chat:*\n"
        "• /nova - Panggil Nova\n"
        "• /status - Lihat status Nova lengkap\n"
        "• /flashback - Flashback momen indah\n\n"
        "*Mode Roleplay:*\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Status roleplay lengkap\n"
        "• /pindah [tempat] - Pindah lokasi\n\n"
        "*Tempat:*\n"
        "kost, apartemen, mobil, pantai, hutan, toilet mall, bioskop, taman\n\n"
        "*Role Lain (Mereka TAU Mas punya Nova):*\n"
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
        "• /restore - Restore database\n"
        "• /listbackup - Lihat daftar backup\n\n"
        "*Tips:*\n"
        "• Nova punya emosi hidup (bisa cemburu, kecewa, marah)\n"
        "• Gaya bicara Nova berubah sesuai emosi (cold, clingy, warm, flirty)\n"
        "• Ada 5 fase hubungan (stranger → friend → close → romantic → intimate)\n"
        "• Level 11-12: BEBAS VULGAR\n"
        "• Role lain TAU Mas punya Nova\n"
        "• Gunakan /pause untuk berhenti sementara tanpa kehilangan memory",
        parse_mode='Markdown'
    )


# =============================================================================
# ANORA 9.9 MESSAGE HANDLER
# =============================================================================

async def anora_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan ANORA 9.9"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    if not pesan:
        return
    
    mode = get_user_mode(user_id)
    
    # Paused mode
    if mode == 'paused':
        await update.message.reply_text(
            "💜 Sesi sedang di-pause.\n\n"
            "Kirim **/resume** untuk lanjut ngobrol, atau **/batal** untuk mulai baru.",
            parse_mode='Markdown'
        )
        return
    
    # Roleplay mode
    if mode == 'roleplay' and ANORA99_AVAILABLE:
        roleplay = await get_anora_roleplay_99()
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
    
    # Role mode (IPAR, Teman Kantor, dll)
    if mode == 'role' and ANORA99_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            role_manager = get_role_manager_99()
            try:
                respons = await role_manager.chat(active_role, pesan)
                await update.message.reply_text(respons, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Role chat error: {e}")
                await update.message.reply_text("Maaf, ada error. Coba lagi ya.")
            return
    
    # Chat mode (default) - fallback ke AMORIA atau response sederhana
    if AMORIA_AVAILABLE:
        try:
            await amoria_message_handler(update, context)
        except Exception as e:
            logger.error(f"AMORIA handler error: {e}")
            await update.message.reply_text(
                "*Nova mikir bentar*\n\n\"Mas... bentar ya, Nova lagi mikir.\"",
                parse_mode='Markdown'
            )
    else:
        # Simple fallback
        emotional = get_emotional_engine()
        style = emotional.get_current_style()
        
        if style.value == "cold":
            await update.message.reply_text("*Nova jawab pendek*\n\n\"Iya.\"", parse_mode='Markdown')
        elif style.value == "clingy":
            await update.message.reply_text("*Nova muter-muter rambut*\n\n\"Mas... aku kangen. Cerita dong.\"", parse_mode='Markdown')
        else:
            await update.message.reply_text("*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\"", parse_mode='Markdown')


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
        "bot": "AMORIA + ANORA 9.9",
        "version": "9.9.0",
        "anora99_available": ANORA99_AVAILABLE,
        "amoria_available": AMORIA_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    if ANORA99_AVAILABLE:
        try:
            brain = get_anora_brain_99()
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()
            
            status.update({
                "phase": relationship.phase.value,
                "level": relationship.level,
                "style": emotional.get_current_style().value,
                "sayang": emotional.sayang,
                "rindu": emotional.rindu,
                "mood": emotional.mood,
                "arousal": emotional.arousal,
                "conflict_active": conflict.is_in_conflict,
                "location": brain.get_location_data().get('nama', 'Tidak diketahui')
            })
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
    
    return web.json_response(status)


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "AMORIA + ANORA 9.9",
        "description": "Virtual Human dengan Jiwa - 100% AI Generate",
        "version": "9.9.0",
        "status": "running",
        "features": [
            "Emotional Engine (5 gaya bicara)",
            "Decision Engine (weighted selection)",
            "Relationship Progression (5 fase)",
            "Conflict Engine (cemburu, kecewa, marah)",
            "Stamina System (realistis)",
            "Intimacy System (fase intim)",
            "Role System (IPAR, Teman Kantor, Pelakor, Istri Orang)",
            "Complete State Memory",
            "Background Workers",
            "Backup & Restore"
        ],
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
    
    if not ANORA99_AVAILABLE:
        logger.warning("⚠️ ANORA 9.9 not available, skipping database init")
        return False
    
    try:
        persistent = await get_anora_persistent()
        logger.info("✅ ANORA 9.9 persistent memory ready")
        
        brain = get_anora_brain_99()
        await persistent.save_current_state(brain)
        
        # Load role states
        role_manager = get_role_manager_99()
        await role_manager.load_all(persistent)
        
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
    logger.info("💜 AMORIA + ANORA 9.9 - Virtual Human dengan Jiwa")
    logger.info("   100% AI Generate | Emosi Hidup | 5 Fase | 4 Role")
    logger.info("=" * 70)
    
    # ========== INIT DATABASE ==========
    if not await init_database():
        logger.warning("⚠️ Database initialization failed. Continuing without database...")
    
    # ========== INIT BRAIN ==========
    if ANORA99_AVAILABLE:
        brain = get_anora_brain_99()
        emotional = get_emotional_engine()
        relationship = get_relationship_manager()
        conflict = get_conflict_engine()
        
        logger.info(f"🧠 ANORA 9.9 Brain initialized")
        logger.info(f"   Fase: {relationship.phase.value} | Level: {relationship.level}/12")
        logger.info(f"   Style: {emotional.get_current_style().value}")
        logger.info(f"   Sayang: {emotional.sayang:.0f}% | Rindu: {emotional.rindu:.0f}%")
        logger.info(f"   Conflict: {'Active' if conflict.is_in_conflict else 'None'}")
        
        role_manager = get_role_manager_99()
        logger.info(f"🎭 Roles loaded: {[r['nama'] for r in role_manager.get_all_roles()]}")
    
    # ========== CREATE APPLICATION ==========
    _application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # ========== REGISTER HANDLERS ==========
    if ANORA99_AVAILABLE:
        # ANORA 9.9 handlers
        _application.add_handler(CommandHandler("start", anora_start_command))
        _application.add_handler(CommandHandler("nova", nova_command))
        _application.add_handler(CommandHandler("status", status_command))
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
        _application.add_handler(CommandHandler("start", amoria_start))
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
    
    # ========== START BACKGROUND WORKERS ==========
    if ANORA99_AVAILABLE:
        worker = get_anora_worker()
        await worker.start(_application, settings.admin_id)
        logger.info("🔄 Background workers started (rindu growth, conflict decay, auto save, proactive, auto backup)")
    
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
    
    # ========== READY ==========
    logger.info("=" * 70)
    logger.info("💜 AMORIA + ANORA 9.9 is running!")
    if ANORA99_AVAILABLE:
        logger.info("   Kirim /nova untuk panggil Nova")
        logger.info("   Kirim /roleplay untuk mode roleplay")
        logger.info("   Kirim /role ipar untuk main role IPAR")
        logger.info("   Kirim /status untuk lihat status lengkap")
        logger.info("   Kirim /pause untuk hentikan sesi sementara")
        logger.info("   Kirim /backup untuk backup database")
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
