# bot/application.py
import logging
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler
from config import settings
from command.start import start_command, SELECTING_ROLE, role_callback, cancel_callback
from command.status import status_command

logger = logging.getLogger(__name__)

def create_application():
    app = Application.builder().token(settings.telegram_token).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            SELECTING_ROLE: [
                CallbackQueryHandler(role_callback, pattern='^role_'),
                CallbackQueryHandler(cancel_callback, pattern='^cancel$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_callback)],
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("status", status_command))
    
    logger.info("✅ Handlers registered")
    return app
