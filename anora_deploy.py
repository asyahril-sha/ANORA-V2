# run_deploy.py - UPDATED WITH ANORA ROLEPLAY
"""
AMORIA + ANORA - Full Version with ANORA Roleplay
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from aiohttp import web
from datetime import datetime

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
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# =============================================================================
# IMPORT ANORA COMPONENTS
# =============================================================================

from anora.core import get_anora
from anora.chat import get_anora_chat
from anora.roles import get_anora_roles, RoleType
from anora.roleplay_integration import get_anora_roleplay
from anora.brain import get_anora_brain

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

_application = None
_user_modes = {}


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, 'chat')


def set_user_mode(user_id: int, mode: str):
    _user_modes[user_id] = mode


# =============================================================================
# HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    await update.message.reply_text(
        "💜 **ANORA** 💜\n\n"
        "**Mode Chat (ngobrol biasa):**\n"
        "• /nova - Panggil Nova\n"
        "• /novastatus - Lihat keadaan Nova\n"
        "• /flashback - Flashback ke momen indah\n\n"
        "**Mode Roleplay (beneran ketemu):**\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Lihat status roleplay\n\n"
        "**Role Lain:**\n"
        "• /role ipar - Pindah ke role IPAR\n"
        "• /role teman_kantor - Teman Kantor\n"
        "• /role pelakor - Pelakor\n"
        "• /role istri_orang - Istri Orang\n\n"
        "**Lainnya:**\n"
        "• /batal - Kembali ke mode chat\n\n"
        "Apa yang Mas mau? 💜",
        parse_mode='HTML'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, cuma Mas yang bisa liat. 💜")
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.format_status(), parse_mode='HTML')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.respon_flashback(), parse_mode='HTML')


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay - Aktifkan mode roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'roleplay')
    
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    
    await update.message.reply_text(intro, parse_mode='HTML')


async def statusrp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrp - Lihat status roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    roleplay = await get_anora_roleplay()
    status = await roleplay.get_status()
    await update.message.reply_text(status, parse_mode='HTML')


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
        set_user_mode(user_id, 'role')
        roles = get_anora_roles()
        respon = roles.switch_role(role_map[role_id])
        await update.message.reply_text(respon, parse_mode='HTML')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada. Coba /role buat liat daftar.")


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - Balik ke Nova mode chat"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    # Stop roleplay kalo lagi aktif
    roleplay = await get_anora_roleplay()
    if roleplay.is_active:
        await roleplay.stop()
    
    anora = get_anora()
    await update.message.reply_text(
        f"💜 Nova di sini, Mas.\n\n{anora.respon_kangen()}",
        parse_mode='HTML'
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua pesan"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    mode = get_user_mode(user_id)
    
    # ========== MODE ROLEPLAY ==========
    if mode == 'roleplay':
        roleplay = await get_anora_roleplay()
        respons = await roleplay.process(pesan)
        await update.message.reply_text(respons, parse_mode='HTML')
        return
    
    # ========== MODE ROLE ==========
    if mode == 'role':
        active_role = context.user_data.get('active_role')
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
    
    # ========== MODE CHAT (DEFAULT) ==========
    anora_chat = get_anora_chat()
    respons = await anora_chat.process(pesan)
    await update.message.reply_text(respons, parse_mode='HTML')


# =============================================================================
# WEBHOOK & SERVER
# =============================================================================

async def webhook_handler(request):
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
    roleplay = await get_anora_roleplay()
    brain = get_anora_brain()
    
    return web.json_response({
        "status": "healthy",
        "bot": "ANORA",
        "version": "9.9.0",
        "roleplay_active": roleplay.is_active,
        "level": brain.relationship.level,
        "sayang": brain.feelings.sayang,
        "timestamp": datetime.now().isoformat()
    })


async def root_handler(request):
    return web.json_response({
        "name": "ANORA",
        "description": "Virtual Human dengan Jiwa - 100% AI Generate",
        "version": "9.9.0",
        "status": "running",
        "endpoints": {
            "/": "API Info",
            "/health": "Health Check",
            "/webhook": "Telegram Webhook"
        }
    })


# =============================================================================
# MAIN
# =============================================================================

async def main():
    global _application
    
    logger.info("=" * 60)
    logger.info("💜 ANORA - Virtual Human dengan Jiwa")
    logger.info("   100% AI Generate | Punya Memory | Bisa Roleplay")
    logger.info("=" * 60)
    
    # Inisialisasi
    brain = get_anora_brain()
    logger.info("🧠 ANORA Brain initialized")
    
    roleplay = await get_anora_roleplay()
    logger.info("🎭 ANORA Roleplay initialized")
    
    # Create application
    _application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # Add handlers
    _application.add_handler(CommandHandler("start", start_command))
    _application.add_handler(CommandHandler("nova", nova_command))
    _application.add_handler(CommandHandler("novastatus", novastatus_command))
    _application.add_handler(CommandHandler("flashback", flashback_command))
    _application.add_handler(CommandHandler("roleplay", roleplay_command))
    _application.add_handler(CommandHandler("statusrp", statusrp_command))
    _application.add_handler(CommandHandler("role", role_command))
    _application.add_handler(CommandHandler("batal", back_to_nova))
    _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Initialize
    await _application.initialize()
    await _application.start()
    
    # Set webhook
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if railway_url:
        webhook_url = f"https://{railway_url}/webhook"
        await _application.bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook set to {webhook_url}")
        
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_handler)
        app.router.add_post('/webhook', webhook_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        logger.info("🌐 Web server running")
    else:
        await _application.updater.start_polling()
        logger.info("📡 Polling mode started")
    
    logger.info("=" * 60)
    logger.info("💜 ANORA is running!")
    logger.info("   Mas bisa kirim /nova untuk panggil Nova")
    logger.info("   Kirim /roleplay untuk mode beneran ketemu")
    logger.info("=" * 60)
    
    # Periodic proactive message
    async def proactive_loop():
        while True:
            await asyncio.sleep(60)  # cek setiap menit
            try:
                roleplay = await get_anora_roleplay()
                if roleplay.is_active:
                    pesan = await roleplay.ai.get_proactive(roleplay.anora)
                    if pesan and _application:
                        await _application.bot.send_message(
                            chat_id=settings.admin_id,
                            text=pesan,
                            parse_mode='HTML'
                        )
                        logger.info("💬 Proactive message sent")
            except Exception as e:
                logger.error(f"Proactive error: {e}")
    
    asyncio.create_task(proactive_loop())
    
    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
