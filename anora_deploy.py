# run_deploy.py
"""
AMORIA + ANORA - Full Deployment
AMORIA: Virtual Human System
ANORA: Nova - Virtual Human dengan Jiwa - 100% AI Generate
"""

import os
import sys
import asyncio
import json
import logging
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
_user_modes: Dict[int, Dict] = {}  # user_id -> {'mode': 'chat'/'roleplay'/'role', 'active_role': None}


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('active_role')


# =============================================================================
# ANORA HANDLERS
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
        "**Lainnya:**\n"
        "• /batal - Kembali ke mode chat\n\n"
        "Apa yang Mas mau? 💜",
        parse_mode='HTML'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    anora = get_anora()
    
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n"
        f"{anora.deskripsi_diri()}\n\n"
        f"{anora.respon_pagi() if datetime.now().hour < 12 else anora.respon_siang()}\n\n"
        f"Mas bisa:\n"
        f"• /novastatus - liat keadaan Nova\n"
        f"• /flashback - inget momen indah\n"
        f"• /roleplay - kalo mau kayak beneran ketemu\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='HTML'
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
    await update.message.reply_text(anora.respon_flashback(), parse_mode='HTML')


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'roleplay')
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='HTML')


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
        await update.message.reply_text(loc_mgr.list_locations(), parse_mode='HTML')
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
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(result.get('message', 'Lokasi tidak ditemukan.'), parse_mode='HTML')


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
        await update.message.reply_text(menu, parse_mode='HTML')
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
        await update.message.reply_text(respon, parse_mode='HTML')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada.", parse_mode='HTML')


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal"""
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
        parse_mode='HTML'
    )


async def anora_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan ANORA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    mode = get_user_mode(user_id)
    
    if mode == 'roleplay':
        roleplay = await get_anora_roleplay()
        respons = await roleplay.process(pesan)
        await update.message.reply_text(respons, parse_mode='HTML')
        return
    
    if mode == 'role':
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
                respon = await roles.chat(role_map[active_role], pesan)
                await update.message.reply_text(respon, parse_mode='HTML')
                return
    
    anora_chat = get_anora_chat()
    respons = await anora_chat.process(pesan)
    await update.message.reply_text(respons, parse_mode='HTML')


# =============================================================================
# AMORIA HANDLERS (jika ada)
# =============================================================================

async def amoria_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start untuk AMORIA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    await update.message.reply_text(
        "💜 **AMORIA** 💜\n\n"
        "Kirim /nova untuk panggil Nova\n"
        "Kirim /roleplay untuk mode roleplay\n"
        "Kirim /help untuk bantuan lengkap",
        parse_mode='HTML'
    )


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
            logger.info(f"📨 Message from {user}: {text}")
        
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    if not ANORA_AVAILABLE:
        return web.json_response({
            "status": "healthy",
            "bot": "AMORIA",
            "version": "9.9.0",
            "anora_available": False,
            "timestamp": datetime.now().isoformat()
        })
    
    try:
        brain = get_anora_brain()
        roleplay = await get_anora_roleplay()
        loc = brain.get_location_data()
        
        return web.json_response({
            "status": "healthy",
            "bot": "ANORA",
            "version": "9.9.0",
            "anora_available": True,
            "roleplay_active": roleplay.is_active,
            "level": brain.relationship.level,
            "sayang": brain.feelings.sayang,
            "location": loc.get('nama', 'Tidak diketahui') if isinstance(loc, dict) else loc.nama,
            "stamina_nova": roleplay.stamina.nova_current,
            "stamina_mas": roleplay.stamina.mas_current,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return web.json_response({
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=500)


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
    try:
        if ANORA_AVAILABLE:
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
        logger.error("❌ Database initialization failed. Continuing without database...")
    
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
    
    # ========== PROACTIVE LOOP ==========
    async def proactive_loop():
        while True:
            await asyncio.sleep(60)
            try:
                if ANORA_AVAILABLE:
                    mode = get_user_mode(settings.admin_id)
                    if mode == 'roleplay':
                        ai = get_anora_roleplay_ai()
                        anora = get_anora()
                        brain = get_anora_brain()
                        roleplay = await get_anora_roleplay()
                        pesan = await ai.get_proactive(anora, brain, roleplay.stamina)
                        if pesan and _application:
                            await _application.bot.send_message(
                                chat_id=settings.admin_id,
                                text=pesan,
                                parse_mode='HTML'
                            )
                            logger.info("💬 Proactive message sent")
            except Exception as e:
                logger.error(f"Proactive error: {e}")
    
    # ========== STAMINA RECOVERY LOOP ==========
    async def stamina_recovery_loop():
        while True:
            await asyncio.sleep(600)
            try:
                if ANORA_AVAILABLE:
                    roleplay = await get_anora_roleplay()
                    roleplay.stamina.update_recovery()
                    await roleplay.save_state()
            except Exception as e:
                logger.error(f"Stamina recovery error: {e}")
    
    # ========== SAVE STATE LOOP ==========
    async def save_state_loop():
        while True:
            await asyncio.sleep(60)
            try:
                if ANORA_AVAILABLE:
                    roleplay = await get_anora_roleplay()
                    await roleplay.save_state()
            except Exception as e:
                logger.error(f"Save state error: {e}")
    
    if ANORA_AVAILABLE:
        asyncio.create_task(proactive_loop())
        asyncio.create_task(stamina_recovery_loop())
        asyncio.create_task(save_state_loop())
    
    # ========== READY ==========
    logger.info("=" * 70)
    logger.info("💜 AMORIA + ANORA is running!")
    if ANORA_AVAILABLE:
        logger.info("   Kirim /nova untuk panggil Nova")
        logger.info("   Kirim /roleplay untuk mode beneran ketemu")
        logger.info("   Kirim /pindah pantai untuk ke pantai")
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
