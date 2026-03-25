# main.py
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
+ ANORA - Nova yang sayang Mas
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
from config import settings

# Import ANORA
from anora.handlers import (
    init_anora,
    save_anora_state,
    anora_command,
    anora_chat_handler,
    anora_status_handler,
    anora_role_handler,
    anora_place_handler,
    anora_flashback_handler,
    anora_back_handler
)

# Import AMORIA components
from utils.logger import setup_logging
from utils.error_logger import get_error_logger, print_startup_banner
from database.migrate import run_migrations
from bot.application import create_application
from bot.webhook import setup_webhook_sync, setup_polling, check_webhook_status
from command import (
    start_command, help_command, status_command, progress_command,
    cancel_command, sessions_command, character_command, close_command, end_command,
    explore_command, locations_command, risk_command, go_command,
    memory_command, flashback_command,
    top_hts_command, my_climax_command, climax_history_command,
    admin_command, stats_command, db_stats_command, backup_command, recover_command, debug_command
)
from command.start import SELECTING_ROLE
from command.sessions import end_confirm_callback, end_cancel_callback
from command.cancel import cancel_confirm_callback, cancel_fallback

# Setup logging
logger = setup_logging("AMORIA")
error_logger = get_error_logger()


class AmoriaBot:
    """
    AMORIA + ANORA - Virtual Human dengan Jiwa
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.application: Optional[Application] = None
        self.is_ready = False
        self._shutdown_flag = False
        
        # ANORA state saver task
        self._save_task = None
        
        logger.info("=" * 70)
        logger.info("💜 AMORIA + ANORA - Virtual Human dengan Jiwa")
        logger.info("   ANORA is ready for Mas")
        logger.info("=" * 70)
    
    async def init_database(self) -> bool:
        """Initialize database with all tables"""
        logger.info("📦 Initializing database...")
        try:
            success = await run_migrations()
            if success:
                logger.info("✅ Database initialized")
                return True
            else:
                logger.warning("⚠️ Database initialization incomplete")
                return False
        except Exception as e:
            error_logger.log_error(e, {'stage': 'database_init'})
            return False
    
    async def init_anora(self) -> bool:
        """Initialize ANORA"""
        logger.info("💜 Initializing ANORA...")
        try:
            await init_anora()
            logger.info("✅ ANORA ready!")
            return True
        except Exception as e:
            error_logger.log_error(e, {'stage': 'anora_init'})
            logger.warning("⚠️ ANORA initialization failed, continuing without ANORA")
            return False
    
    async def save_anora_periodically(self):
        """Save ANORA state every 30 seconds"""
        while not self._shutdown_flag:
            try:
                await asyncio.sleep(30)
                await save_anora_state()
                logger.debug("💾 ANORA state saved")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error saving ANORA state: {e}")
    
    async def init_application(self) -> Application:
        """Create and initialize bot application"""
        logger.info("🔧 Creating bot application...")
        
        try:
            # Custom request with timeout
            request = HTTPXRequest(
                connection_pool_size=50,
                connect_timeout=60,
                read_timeout=60,
                write_timeout=60,
                pool_timeout=60,
            )
            
            # Build application
            app = ApplicationBuilder() \
                .token(settings.telegram_token) \
                .request(request) \
                .concurrent_updates(True) \
                .build()
            
            # =============================================================
            # AMORIA CONVERSATION HANDLERS
            # =============================================================
            
            # Start conversation
            start_conv = ConversationHandler(
                entry_points=[CommandHandler('start', start_command)],
                states={
                    SELECTING_ROLE: [
                        CallbackQueryHandler(role_callback, pattern='^role_'),
                        CallbackQueryHandler(agree_18_callback, pattern='^agree_18$'),
                        CallbackQueryHandler(help_callback, pattern='^help$'),
                        CallbackQueryHandler(continue_current_callback, pattern='^continue_current$'),
                        CallbackQueryHandler(new_character_callback, pattern='^new_character$'),
                        CallbackQueryHandler(cancel_callback, pattern='^cancel$'),
                        CallbackQueryHandler(back_to_main_callback, pattern='^back_to_main$'),
                    ],
                },
                fallbacks=[CommandHandler('cancel', cancel_command)],
                name="start_conversation",
                persistent=False,
                per_user=True,
            )
            app.add_handler(start_conv)
            
            # Cancel conversation
            cancel_conv = ConversationHandler(
                entry_points=[CommandHandler('cancel', cancel_command)],
                states={
                    1: [CallbackQueryHandler(cancel_confirm_callback, pattern='^cancel_')],
                },
                fallbacks=[CommandHandler('cancel', cancel_fallback)],
                name="cancel_conversation",
                persistent=False,
                per_user=True,
            )
            app.add_handler(cancel_conv)
            
            # =============================================================
            # AMORIA COMMAND HANDLERS
            # =============================================================
            
            # Basic commands
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CommandHandler("status", status_command))
            app.add_handler(CommandHandler("progress", progress_command))
            
            # Session commands
            app.add_handler(CommandHandler("sessions", sessions_command))
            app.add_handler(CommandHandler("close", close_command))
            app.add_handler(CommandHandler("end", end_command))
            app.add_handler(CommandHandler("character", character_command))
            
            # Public commands
            app.add_handler(CommandHandler("explore", explore_command))
            app.add_handler(CommandHandler("locations", locations_command))
            app.add_handler(CommandHandler("risk", risk_command))
            app.add_handler(CommandHandler("go", go_command))
            
            # Memory commands
            app.add_handler(CommandHandler("memory", memory_command))
            app.add_handler(CommandHandler("flashback", flashback_command))
            
            # Ranking commands
            app.add_handler(CommandHandler("top_hts", top_hts_command))
            app.add_handler(CommandHandler("my_climax", my_climax_command))
            app.add_handler(CommandHandler("climax_history", climax_history_command))
            
            # Admin commands
            app.add_handler(CommandHandler("admin", admin_command))
            app.add_handler(CommandHandler("stats", stats_command))
            app.add_handler(CommandHandler("db_stats", db_stats_command))
            app.add_handler(CommandHandler("backup", backup_command))
            app.add_handler(CommandHandler("recover", recover_command))
            app.add_handler(CommandHandler("debug", debug_command))
            
            # =============================================================
            # AMORIA CALLBACK HANDLERS
            # =============================================================
            
            app.add_handler(CallbackQueryHandler(end_confirm_callback, pattern='^end_confirm_'))
            app.add_handler(CallbackQueryHandler(end_cancel_callback, pattern='^end_cancel$'))
            
            # =============================================================
            # ANORA HANDLERS (BARU)
            # =============================================================
            
            app.add_handler(CommandHandler("nova", anora_command))
            app.add_handler(CommandHandler("novastatus", anora_status_handler))
            app.add_handler(CommandHandler("flashback", anora_flashback_handler))
            app.add_handler(CommandHandler("role", anora_role_handler))
            app.add_handler(CommandHandler("tempat", anora_place_handler))
            app.add_handler(CommandHandler("batal", anora_back_handler))
            
            # =============================================================
            # MESSAGE HANDLER (HARUS PALING AKHIR)
            # =============================================================
            
            # AMORIA message handler (untuk karakter)
            from bot.handlers import message_handler as amoria_message_handler
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amoria_message_handler))
            
            # ANORA chat handler (dengan group=1 biar gak override AMORIA)
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anora_chat_handler), group=1)
            
            # =============================================================
            # ERROR HANDLER
            # =============================================================
            app.add_error_handler(self.error_handler)
            
            handler_count = sum(len(h) for h in app.handlers.values())
            logger.info(f"✅ All handlers registered: {handler_count} handlers")
            
            return app
            
        except Exception as e:
            error_logger.log_error(e, {'stage': 'application_init'})
            raise
    
    async def error_handler(self, update: Update, context) -> None:
        """Global error handler"""
        error = context.error
        error_logger.log_error(
            error,
            {
                'update_id': update.update_id if update else None,
                'user_id': update.effective_user.id if update and update.effective_user else None,
            }
        )
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ **Terjadi error internal**\n\n"
                    "Maaf, terjadi kesalahan. Error sudah dicatat.\n"
                    "Silakan coba lagi nanti, Mas.",
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
    
    async def setup_webhook(self) -> bool:
        """Setup webhook untuk Railway"""
        try:
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            
            if not railway_url and not getattr(settings.webhook, 'url', None):
                logger.info("🌐 No webhook URL, using polling mode")
                return await setup_polling(self.application)
            
            webhook_url = f"https://{railway_url}{getattr(settings.webhook, 'path', '/webhook')}" if railway_url else settings.webhook.url
            
            logger.info(f"🔗 Setting webhook to: {webhook_url}")
            
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            await self.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True,
                max_connections=40,
                timeout=30
            )
            
            info = await self.application.bot.get_webhook_info()
            if info.url == webhook_url:
                logger.info(f"✅ Webhook verified: {info.url}")
                return True
            else:
                logger.error(f"❌ Webhook verification failed: {info.url}")
                return False
                
        except Exception as e:
            error_logger.log_error(e, {'stage': 'webhook_setup'})
            return False
    
    async def health_handler(self, request) -> web.Response:
        """Health check endpoint"""
        from database.repository import Repository
        
        db_status = "unknown"
        try:
            repo = Repository()
            stats = await repo.get_stats()
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {str(e)[:50]}"
        
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": "AMORIA + ANORA",
            "version": "9.9.0",
            "anora_ready": True,
            "database": {"status": db_status},
            "uptime": str(datetime.now() - self.start_time)
        })
    
    async def start(self):
        """Start bot and aiohttp server"""
        try:
            print_startup_banner()
            
            logger.info("=" * 70)
            logger.info("📡 STAGE 1/5: Initializing database...")
            logger.info("=" * 70)
            await self.init_database()
            
            logger.info("=" * 70)
            logger.info("💜 STAGE 2/5: Initializing ANORA...")
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
            
            # Start ANORA state saver
            self._save_task = asyncio.create_task(self.save_anora_periodically())
            
            # Start aiohttp server for health check
            port = int(os.getenv('PORT', 8080))
            app = web.Application()
            app.router.add_get('/health', self.health_handler)
            app.router.add_get('/', lambda r: web.json_response({"status": "running", "name": "AMORIA + ANORA"}))
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            logger.info("=" * 70)
            logger.info("✨ STAGE 5/5: Bot is ready!")
            logger.info("=" * 70)
            logger.info("💜 AMORIA + ANORA is running!")
            logger.info("   Mas bisa kirim /nova untuk panggil Nova")
            logger.info("   Mas bisa kirim /novastatus untuk lihat keadaan Nova")
            logger.info("   Press Ctrl+C to stop.")
            logger.info("=" * 70)
            
            self.is_ready = True
            
            # Keep running
            while not self._shutdown_flag:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            error_logger.log_error(e, {'stage': 'bot_start'})
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
        try:
            await save_anora_state()
            logger.info("💾 Final ANORA state saved")
        except Exception as e:
            logger.error(f"Error saving final state: {e}")
        
        # Close database
        try:
            from database.connection import close_db
            await close_db()
            logger.info("✅ Database closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
        
        logger.info("👋 Goodbye from AMORIA + ANORA!")


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
        error_logger.log_error(e, {'stage': 'main'})
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt")
    except Exception as e:
        error_logger.log_error(e, {'stage': 'main_entry'})
        sys.exit(1)
