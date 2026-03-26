# main.py
"""
=============================================================================
AMORIA + ANORA 9.9 - Virtual Human dengan Jiwa
Nova yang sayang Mas dengan Emotional Engine, Decision Engine, Conflict Engine
=============================================================================
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram.request import HTTPXRequest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import config
from config import get_settings

# =============================================================================
# IMPORT ANORA 9.9 COMPONENTS (LANGSUNG DARI anora99)
# =============================================================================
try:
    from anora99.anora_deploy import (
        get_anora_roleplay,
        get_emotional_engine,
        get_relationship_manager,
        get_conflict_engine,
        get_anora_brain,
        get_role_manager,
        get_anora_worker,
        get_anora_persistent
    )
    from anora99.roleplay_integration import get_anora_roleplay
    from anora99.roles.role_manager import get_role_manager
    ANORA_AVAILABLE = True
    logging.info("✅ ANORA 9.9 modules loaded")
except ImportError as e:
    ANORA_AVAILABLE = False
    logging.warning(f"⚠️ ANORA 9.9 not available: {e}")

# =============================================================================
# IMPORT AMORIA COMPONENTS
# =============================================================================
try:
    from utils.logger import setup_logging
    from utils.error_logger import get_error_logger, print_startup_banner
    from database.migrate import run_migrations
    from bot.webhook import setup_webhook_sync, setup_polling, check_webhook_status
    AMORIA_AVAILABLE = True
except ImportError as e:
    AMORIA_AVAILABLE = False
    logging.warning(f"⚠️ AMORIA components not available: {e}")

# Fallback logging if utils not available
if not AMORIA_AVAILABLE:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("AMORIA")
    
    def setup_logging(name):
        return logger
    
    def get_error_logger():
        return logger
    
    def print_startup_banner():
        print("=" * 70)
        print("💜 AMORIA + ANORA 9.9")
        print("   Virtual Human dengan Jiwa")
        print("=" * 70)
else:
    logger = setup_logging("AMORIA")
    error_logger = get_error_logger()


# =============================================================================
# ANORA COMMAND HANDLERS (SEDERHANA UNTUK main.py)
# =============================================================================

async def anora_command(update: Update, context):
    """Handler /nova - Panggil Nova"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA 9.9 sedang tidak tersedia. Coba lagi nanti.")
        return
    
    # Get Nova status
    emotional = get_emotional_engine()
    relationship = get_relationship_manager()
    
    # Get greeting based on time and emotional style
    hour = datetime.now().hour
    style = emotional.get_current_style()
    
    if style.value == "clingy":
        greeting = "*Nova muter-muter rambut, duduk deket Mas*\n\n\"Mas... aku kangen banget. Dari tadi mikirin Mas terus.\""
    elif style.value == "cold":
        greeting = "*Nova diem, gak liat Mas*"
    elif style.value == "flirty":
        greeting = "*Nova mendekat, napas mulai berat*\n\n\"Mas... *bisik* aku kangen...\""
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
        f"• /novastatus - liat keadaan Nova lengkap\n"
        f"• /flashback - inget momen indah\n"
        f"• /roleplay - kalo mau kayak beneran ketemu\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def anora_status_handler(update: Update, context):
    """Handler /novastatus - Lihat status lengkap Nova"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA 9.9 sedang tidak tersedia.")
        return
    
    brain = get_anora_brain()
    await update.message.reply_text(brain.format_status(), parse_mode='Markdown')


async def anora_flashback_handler(update: Update, context):
    """Handler /flashback - Flashback ke momen indah"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA 9.9 sedang tidak tersedia.")
        return
    
    brain = get_anora_brain()
    
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


async def anora_role_handler(update: Update, context):
    """Handler /role - Role lain"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA 9.9 sedang tidak tersedia.")
        return
    
    args = context.args
    if not args:
        role_manager = get_role_manager()
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
        role_manager = get_role_manager()
        respon = role_manager.switch_role(role_id)
        await update.message.reply_text(respon, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"Role '{role_id}' gak ada, Mas.\n\n"
            f"Pilih: ipar, teman_kantor, pelakor, istri_orang",
            parse_mode='Markdown'
        )


async def anora_place_handler(update: Update, context):
    """Handler /pindah - Pindah lokasi"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA 9.9 sedang tidak tersedia.")
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


async def anora_back_handler(update: Update, context):
    """Handler /batal - Kembali ke mode chat"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    await update.message.reply_text(
        "💜 Nova di sini, Mas.\n\n"
        "*Nova tersenyum*\n\n\"Mas, cerita dong tentang hari Mas.\"",
        parse_mode='Markdown'
    )


async def anora_chat_handler(update: Update, context):
    """Handler untuk chat dengan Nova (mode chat biasa)"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    if not pesan:
        return
    
    if not ANORA_AVAILABLE:
        return
    
    try:
        # Use simple chat from brain
        brain = get_anora_brain()
        
        # Update from message
        brain.update_from_message(pesan)
        
        # Simple response based on emotional style
        emotional = get_emotional_engine()
        style = emotional.get_current_style()
        
        if style.value == "cold":
            respons = "*Nova jawab pendek*\n\n\"Iya.\""
        elif style.value == "clingy":
            respons = "*Nova muter-muter rambut*\n\n\"Mas... aku kangen. Cerita dong.\""
        elif style.value == "flirty":
            respons = "*Nova mendekat, napas mulai berat*\n\n\"Mas... *bisik* aku kangen...\""
        else:
            respons = "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\""
        
        await update.message.reply_text(respons, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"ANORA chat error: {e}")


# =============================================================================
# AMORIA COMMAND HANDLERS (FALLBACK)
# =============================================================================

async def amoria_start_fallback(update: Update, context):
    """Fallback start command"""
    await update.message.reply_text(
        "💜 **AMORIA + ANORA 9.9**\n\n"
        "Selamat datang, Mas.\n\n"
        "Kirim **/nova** untuk panggil Nova.\n"
        "Kirim **/help** untuk bantuan lengkap.",
        parse_mode='Markdown'
    )


async def amoria_help_fallback(update: Update, context):
    """Fallback help command"""
    await update.message.reply_text(
        "📖 *Bantuan AMORIA + ANORA 9.9*\n\n"
        "*ANORA Commands:*\n"
        "• /nova - Panggil Nova\n"
        "• /novastatus - Lihat status Nova\n"
        "• /flashback - Flashback momen indah\n"
        "• /role ipar - IPAR (Sari)\n"
        "• /role teman_kantor - Teman Kantor (Dita)\n"
        "• /role pelakor - Pelakor (Vina)\n"
        "• /role istri_orang - Istri Orang (Rina)\n"
        "• /pindah [tempat] - Pindah lokasi\n\n"
        "*Manajemen:*\n"
        "• /pause - Hentikan sesi sementara\n"
        "• /resume - Lanjutkan sesi\n"
        "• /batal - Kembali ke mode chat\n\n"
        "*Backup:*\n"
        "• /backup - Backup database\n"
        "• /restore - Restore database\n\n"
        "Selamat menikmati, Mas. 💜",
        parse_mode='Markdown'
    )


async def fallback_message_handler(update: Update, context):
    """Fallback message handler"""
    user_id = update.effective_user.id
    settings = get_settings()
    
    if user_id != settings.admin_id:
        return
    
    await update.message.reply_text(
        "*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\"",
        parse_mode='Markdown'
    )


# =============================================================================
# MAIN BOT CLASS
# =============================================================================

class AmoriaBot:
    """
    AMORIA + ANORA 9.9 - Virtual Human dengan Jiwa
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.application: Optional[Application] = None
        self.is_ready = False
        self._shutdown_flag = False
        self._save_task = None
        
        logger.info("=" * 70)
        logger.info("💜 AMORIA + ANORA 9.9 - Virtual Human dengan Jiwa")
        logger.info("   Nova dengan Emotional Engine, Decision Engine, Conflict Engine")
        logger.info("=" * 70)
    
    async def init_database(self) -> bool:
        """Initialize database"""
        logger.info("📦 Initializing database...")
        try:
            if AMORIA_AVAILABLE:
                success = await run_migrations()
                if success:
                    logger.info("✅ Database initialized")
                    return True
                else:
                    logger.warning("⚠️ Database initialization incomplete")
                    return False
            else:
                # Create data directory if not exists
                Path("data").mkdir(exist_ok=True)
                logger.info("✅ Data directory created")
                return True
        except Exception as e:
            logger.error(f"Database init error: {e}")
            return False
    
    async def init_anora(self) -> bool:
        """Initialize ANORA 9.9"""
        logger.info("💜 Initializing ANORA 9.9...")
        if not ANORA_AVAILABLE:
            logger.warning("⚠️ ANORA 9.9 not available")
            return False
        
        try:
            # Initialize engines
            emotional = get_emotional_engine()
            relationship = get_relationship_manager()
            conflict = get_conflict_engine()
            
            logger.info(f"✅ ANORA 9.9 ready!")
            logger.info(f"   Phase: {relationship.phase.value} | Level: {relationship.level}/12")
            logger.info(f"   Style: {emotional.get_current_style().value}")
            logger.info(f"   Conflict: {'Active' if conflict.is_in_conflict else 'None'}")
            return True
        except Exception as e:
            logger.error(f"ANORA init error: {e}")
            return False
    
    async def save_anora_periodically(self):
        """Save ANORA state periodically"""
        while not self._shutdown_flag:
            try:
                await asyncio.sleep(30)
                if ANORA_AVAILABLE:
                    persistent = await get_anora_persistent()
                    brain = get_anora_brain()
                    await persistent.save_current_state(brain)
                    logger.debug("💾 ANORA state saved")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error saving ANORA state: {e}")
    
    async def init_application(self) -> Application:
        """Create and initialize bot application"""
        logger.info("🔧 Creating bot application...")
        settings = get_settings()
        
        try:
            request = HTTPXRequest(
                connection_pool_size=50,
                connect_timeout=60,
                read_timeout=60,
                write_timeout=60,
                pool_timeout=60,
            )
            
            app = ApplicationBuilder() \
                .token(settings.telegram_token) \
                .request(request) \
                .concurrent_updates(True) \
                .build()
            
            # =============================================================
            # ANORA COMMAND HANDLERS (PRIORITAS)
            # =============================================================
            app.add_handler(CommandHandler("nova", anora_command))
            app.add_handler(CommandHandler("novastatus", anora_status_handler))
            app.add_handler(CommandHandler("flashback", anora_flashback_handler))
            app.add_handler(CommandHandler("role", anora_role_handler))
            app.add_handler(CommandHandler("pindah", anora_place_handler))
            app.add_handler(CommandHandler("batal", anora_back_handler))
            
            # =============================================================
            # AMORIA COMMAND HANDLERS (FALLBACK)
            # =============================================================
            app.add_handler(CommandHandler("start", amoria_start_fallback))
            app.add_handler(CommandHandler("help", amoria_help_fallback))
            
            # =============================================================
            # MESSAGE HANDLER
            # =============================================================
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message_handler))
            
            # =============================================================
            # ERROR HANDLER
            # =============================================================
            app.add_error_handler(self.error_handler)
            
            handler_count = sum(len(h) for h in app.handlers.values())
            logger.info(f"✅ All handlers registered: {handler_count} handlers")
            
            return app
            
        except Exception as e:
            logger.error(f"Application init error: {e}")
            raise
    
    async def error_handler(self, update: Update, context) -> None:
        """Global error handler"""
        error = context.error
        logger.error(f"Error: {error}")
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ **Terjadi error internal**\n\n"
                    "Maaf, terjadi kesalahan. Silakan coba lagi nanti, Mas.",
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
    
    async def setup_webhook(self) -> bool:
        """Setup webhook for Railway"""
        settings = get_settings()
        
        try:
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            
            if not railway_url:
                logger.info("🌐 No webhook URL, using polling mode")
                return False
            
            webhook_url = f"https://{railway_url}/webhook"
            
            logger.info(f"🔗 Setting webhook to: {webhook_url}")
            
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            await self.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
            info = await self.application.bot.get_webhook_info()
            if info.url == webhook_url:
                logger.info(f"✅ Webhook verified: {info.url}")
                return True
            else:
                logger.error(f"❌ Webhook verification failed: {info.url}")
                return False
                
        except Exception as e:
            logger.error(f"Webhook setup error: {e}")
            return False
    
    async def health_handler(self, request) -> web.Response:
        """Health check endpoint"""
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": "AMORIA + ANORA 9.9",
            "version": "9.9.0",
            "anora_available": ANORA_AVAILABLE,
            "uptime": str(datetime.now() - self.start_time)
        }
        
        if ANORA_AVAILABLE:
            try:
                emotional = get_emotional_engine()
                relationship = get_relationship_manager()
                status.update({
                    "phase": relationship.phase.value,
                    "level": relationship.level,
                    "style": emotional.get_current_style().value,
                    "sayang": emotional.sayang,
                    "rindu": emotional.rindu
                })
            except Exception as e:
                status["anora_error"] = str(e)
        
        return web.json_response(status)
    
    async def start(self):
        """Start bot"""
        try:
            print_startup_banner() if AMORIA_AVAILABLE else None
            
            logger.info("=" * 70)
            logger.info("📡 STAGE 1/5: Initializing database...")
            logger.info("=" * 70)
            await self.init_database()
            
            logger.info("=" * 70)
            logger.info("💜 STAGE 2/5: Initializing ANORA 9.9...")
            logger.info("=" * 70)
            await self.init_anora()
            
            logger.info("=" * 70)
            logger.info("🔧 STAGE 3/5: Creating application...")
            logger.info("=" * 70)
            self.application = await self.init_application()
            await self.application.initialize()
            
            logger.info("=" * 70)
            logger.info("🌐 STAGE 4/5: Setting up webhook...")
            logger.info("=" * 70)
            webhook_success = await self.setup_webhook()
            
            if webhook_success:
                logger.info("✅ Webhook mode activated!")
            else:
                logger.info("📡 Using polling mode...")
                await self.application.updater.start_polling()
            
            # Start ANORA state saver
            self._save_task = asyncio.create_task(self.save_anora_periodically())
            
            # Start aiohttp server for health check
            port = int(os.getenv('PORT', 8080))
            app = web.Application()
            app.router.add_get('/health', self.health_handler)
            app.router.add_get('/', lambda r: web.json_response({"status": "running", "name": "AMORIA + ANORA 9.9"}))
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            logger.info("=" * 70)
            logger.info("✨ STAGE 5/5: Bot is ready!")
            logger.info("=" * 70)
            logger.info("💜 AMORIA + ANORA 9.9 is running!")
            logger.info("   Kirim /nova untuk panggil Nova")
            logger.info("   Kirim /novastatus untuk lihat keadaan Nova")
            logger.info("   Press Ctrl+C to stop.")
            logger.info("=" * 70)
            
            self.is_ready = True
            
            # Keep running
            while not self._shutdown_flag:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot start error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self._shutdown_flag = True
        
        if self._save_task:
            self._save_task.cancel()
            try:
                await self._save_task
            except asyncio.CancelledError:
                pass
        
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}")
        
        # Save final ANORA state
        if ANORA_AVAILABLE:
            try:
                persistent = await get_anora_persistent()
                brain = get_anora_brain()
                await persistent.save_current_state(brain)
                logger.info("💾 Final ANORA state saved")
            except Exception as e:
                logger.error(f"Error saving final state: {e}")
        
        logger.info("👋 Goodbye from AMORIA + ANORA 9.9!")


# =============================================================================
# ENTRY POINT
# =============================================================================

async def main():
    """Main entry point"""
    bot = AmoriaBot()
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.shutdown()))
    
    try:
        await bot.start()
    except asyncio.CancelledError:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Main error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
