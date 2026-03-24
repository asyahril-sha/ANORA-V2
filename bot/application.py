# bot/application.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
PTB Application Factory - All Handlers & Callbacks
Target Realism 9.9/10
=============================================================================
"""

import logging
from typing import Optional

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

from config import settings
from command import (
    start_command,
    help_command,
    status_command,
    progress_command,
    cancel_command,
    sessions_command,
    character_command,
    character_list_command,
    character_pause_command,
    character_resume_command,
    character_stop_command,
    close_command,
    end_command,
    ex_list_command,
    ex_detail_command,
    fwb_request_command,
    fwb_list_command,
    fwb_pause_command,
    fwb_resume_command,
    fwb_end_command,
    hts_list_command,
    hts_call_handler,
    hts_detail_command,
    threesome_command,
    threesome_list_command,
    threesome_status_command,
    threesome_pattern_command,
    threesome_cancel_command,
    explore_command,
    locations_command,
    risk_command,
    go_command,
    memory_command,
    flashback_command,
    top_hts_command,
    my_climax_command,
    climax_history_command,
    admin_command,
    stats_command,
    db_stats_command,
    backup_command,
    recover_command,
    debug_command,
)
from command.start import SELECTING_ROLE, role_callback, agree_18_callback, help_callback, continue_current_callback, new_character_callback, cancel_callback as start_cancel_callback
from command.sessions import end_confirm_callback, end_cancel_callback
from command.character import stop_confirm_callback, stop_cancel_callback
from command.ex_fwb import fwb_end_confirm_callback, fwb_end_cancel_callback
from command.hts import hts_intim_yes_callback, hts_intim_no_callback
from command.threesome import (
    threesome_select_callback,
    threesome_start_callback,
    threesome_pattern_callback,
    threesome_cancel_confirm_callback,
    threesome_cancel_callback
)
from command.public import explore_random_callback, go_callback, risk_callback
from command.memory import (
    memory_chat_callback,
    memory_milestone_callback,
    memory_promises_callback,
    memory_preferences_callback,
    memory_weighted_callback,
    flashback_random_callback,
    memory_back_callback
)
from command.ranking import climax_history_callback, climax_back_callback
from command.admin import (
    admin_stats_callback,
    admin_db_stats_callback,
    admin_debug_callback,
    admin_backup_callback,
    admin_recover_callback,
    admin_cleanup_callback,
    admin_back_callback,
    admin_close_callback,
    backup_confirm_callback,
    backup_cancel_callback,
    recover_select_callback,
    recover_confirm_callback,
    recover_cancel_callback,
    cleanup_confirm_callback
)
from command.cancel import cancel_confirm_callback, cancel_fallback
from bot.handlers import message_handler, error_handler

logger = logging.getLogger(__name__)


def create_application() -> Application:
    """
    Create and configure telegram application untuk AMORIA 9.9
    
    Returns:
        Application: PTB Application yang sudah dikonfigurasi
    """
    logger.info("=" * 60)
    logger.info("🔧 Creating PTB application for AMORIA 9.9...")
    logger.info("=" * 60)
    
    # Custom request dengan timeout besar untuk AI response
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
    
    # =========================================================================
    # CONVERSATION HANDLERS
    # =========================================================================
    
    # Start conversation (role selection)
    start_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            SELECTING_ROLE: [
                CallbackQueryHandler(agree_18_callback, pattern='^agree_18$'),
                CallbackQueryHandler(help_callback, pattern='^help$'),
                CallbackQueryHandler(continue_current_callback, pattern='^continue_current$'),
                CallbackQueryHandler(new_character_callback, pattern='^new_character$'),
                CallbackQueryHandler(start_cancel_callback, pattern='^cancel$'),
                CallbackQueryHandler(role_callback, pattern='^role_ipar$'),
                CallbackQueryHandler(role_callback, pattern='^role_teman_kantor$'),
                CallbackQueryHandler(role_callback, pattern='^role_janda$'),
                CallbackQueryHandler(role_callback, pattern='^role_pelakor$'),
                CallbackQueryHandler(role_callback, pattern='^role_istri_orang$'),
                CallbackQueryHandler(role_callback, pattern='^role_pdkt$'),
                CallbackQueryHandler(role_callback, pattern='^role_sepupu$'),
                CallbackQueryHandler(role_callback, pattern='^role_teman_sma$'),
                CallbackQueryHandler(role_callback, pattern='^role_mantan$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        name="start_conversation",
        persistent=False,
        per_user=True,
    )
    
    app.add_handler(start_conv)
    
    # Cancel conversation handler
    cancel_conv = ConversationHandler(
        entry_points=[CommandHandler('cancel', cancel_command)],
        states={
            1: [  # CANCEL_CONFIRM state
                CallbackQueryHandler(cancel_confirm_callback, pattern='^cancel_'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_fallback)],
        name="cancel_conversation",
        persistent=False,
        per_user=True,
    )
    
    app.add_handler(cancel_conv)
    
    # =========================================================================
    # COMMAND HANDLERS
    # =========================================================================
    
    logger.info("  • Registering command handlers...")
    
    # Basic commands
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("progress", progress_command))
    
    # Session commands
    app.add_handler(CommandHandler("sessions", sessions_command))
    app.add_handler(CommandHandler("close", close_command))
    app.add_handler(CommandHandler("end", end_command))
    
    # Character commands
    app.add_handler(CommandHandler("character", character_command))
    app.add_handler(CommandHandler("character-list", character_list_command))
    app.add_handler(CommandHandler("character-pause", character_pause_command))
    app.add_handler(CommandHandler("character-resume", character_resume_command))
    app.add_handler(CommandHandler("character-stop", character_stop_command))
    
    # Ex & FWB commands
    app.add_handler(CommandHandler("ex-list", ex_list_command))
    app.add_handler(CommandHandler("ex", ex_detail_command))
    app.add_handler(CommandHandler("fwb-request", fwb_request_command))
    app.add_handler(CommandHandler("fwb-list", fwb_list_command))
    app.add_handler(CommandHandler("fwb-pause", fwb_pause_command))
    app.add_handler(CommandHandler("fwb-resume", fwb_resume_command))
    app.add_handler(CommandHandler("fwb-end", fwb_end_command))
    
    # HTS commands
    app.add_handler(CommandHandler("hts-list", hts_list_command))
    app.add_handler(CommandHandler("hts-detail", hts_detail_command))
    app.add_handler(MessageHandler(filters.Regex(r'^/hts-'), hts_call_handler))
    
    # Threesome commands
    app.add_handler(CommandHandler("threesome", threesome_command))
    app.add_handler(CommandHandler("threesome-list", threesome_list_command))
    app.add_handler(CommandHandler("threesome-status", threesome_status_command))
    app.add_handler(CommandHandler("threesome-pattern", threesome_pattern_command))
    app.add_handler(CommandHandler("threesome-cancel", threesome_cancel_command))
    
    # Public commands
    app.add_handler(CommandHandler("explore", explore_command))
    app.add_handler(CommandHandler("locations", locations_command))
    app.add_handler(CommandHandler("risk", risk_command))
    app.add_handler(CommandHandler("go", go_command))
    
    # Memory commands
    app.add_handler(CommandHandler("memory", memory_command))
    app.add_handler(CommandHandler("flashback", flashback_command))
    
    # Ranking commands
    app.add_handler(CommandHandler("top-hts", top_hts_command))
    app.add_handler(CommandHandler("my-climax", my_climax_command))
    app.add_handler(CommandHandler("climax-history", climax_history_command))
    
    # Admin commands
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("db-stats", db_stats_command))
    app.add_handler(CommandHandler("backup", backup_command))
    app.add_handler(CommandHandler("recover", recover_command))
    app.add_handler(CommandHandler("debug", debug_command))
    
    # =========================================================================
    # CALLBACK HANDLERS
    # =========================================================================
    
    logger.info("  • Registering callback handlers...")
    
    # Session callbacks
    app.add_handler(CallbackQueryHandler(end_confirm_callback, pattern='^end_confirm_'))
    app.add_handler(CallbackQueryHandler(end_cancel_callback, pattern='^end_cancel$'))
    
    # Character callbacks
    app.add_handler(CallbackQueryHandler(stop_confirm_callback, pattern='^stop_confirm_'))
    app.add_handler(CallbackQueryHandler(stop_cancel_callback, pattern='^stop_cancel$'))
    
    # FWB callbacks
    app.add_handler(CallbackQueryHandler(fwb_end_confirm_callback, pattern='^fwb_end_confirm_'))
    app.add_handler(CallbackQueryHandler(fwb_end_cancel_callback, pattern='^fwb_end_cancel$'))
    
    # HTS callbacks
    app.add_handler(CallbackQueryHandler(hts_intim_yes_callback, pattern='^hts_intim_yes_'))
    app.add_handler(CallbackQueryHandler(hts_intim_no_callback, pattern='^hts_intim_no$'))
    
    # Threesome callbacks
    app.add_handler(CallbackQueryHandler(threesome_select_callback, pattern='^threesome_select_'))
    app.add_handler(CallbackQueryHandler(threesome_start_callback, pattern='^threesome_start_'))
    app.add_handler(CallbackQueryHandler(threesome_pattern_callback, pattern='^threesome_pattern_'))
    app.add_handler(CallbackQueryHandler(threesome_cancel_confirm_callback, pattern='^threesome_cancel_confirm$'))
    app.add_handler(CallbackQueryHandler(threesome_cancel_callback, pattern='^threesome_cancel$'))
    
    # Public callbacks
    app.add_handler(CallbackQueryHandler(explore_random_callback, pattern='^explore_random$'))
    app.add_handler(CallbackQueryHandler(go_callback, pattern='^go_'))
    app.add_handler(CallbackQueryHandler(risk_callback, pattern='^risk_'))
    
    # Memory callbacks
    app.add_handler(CallbackQueryHandler(memory_chat_callback, pattern='^memory_chat$'))
    app.add_handler(CallbackQueryHandler(memory_milestone_callback, pattern='^memory_milestone$'))
    app.add_handler(CallbackQueryHandler(memory_promises_callback, pattern='^memory_promises$'))
    app.add_handler(CallbackQueryHandler(memory_preferences_callback, pattern='^memory_preferences$'))
    app.add_handler(CallbackQueryHandler(memory_weighted_callback, pattern='^memory_weighted$'))
    app.add_handler(CallbackQueryHandler(flashback_random_callback, pattern='^flashback_random$'))
    app.add_handler(CallbackQueryHandler(memory_back_callback, pattern='^memory_back$'))
    
    # Ranking callbacks
    app.add_handler(CallbackQueryHandler(climax_history_callback, pattern='^climax_history$'))
    app.add_handler(CallbackQueryHandler(climax_back_callback, pattern='^climax_back$'))
    
    # Admin callbacks
    app.add_handler(CallbackQueryHandler(admin_stats_callback, pattern='^admin_stats$'))
    app.add_handler(CallbackQueryHandler(admin_db_stats_callback, pattern='^admin_db_stats$'))
    app.add_handler(CallbackQueryHandler(admin_debug_callback, pattern='^admin_debug$'))
    app.add_handler(CallbackQueryHandler(admin_backup_callback, pattern='^admin_backup$'))
    app.add_handler(CallbackQueryHandler(admin_recover_callback, pattern='^admin_recover$'))
    app.add_handler(CallbackQueryHandler(admin_cleanup_callback, pattern='^admin_cleanup$'))
    app.add_handler(CallbackQueryHandler(admin_back_callback, pattern='^admin_back$'))
    app.add_handler(CallbackQueryHandler(admin_close_callback, pattern='^admin_close$'))
    app.add_handler(CallbackQueryHandler(backup_confirm_callback, pattern='^backup_confirm$'))
    app.add_handler(CallbackQueryHandler(backup_cancel_callback, pattern='^backup_cancel$'))
    app.add_handler(CallbackQueryHandler(recover_select_callback, pattern='^recover_select_'))
    app.add_handler(CallbackQueryHandler(recover_confirm_callback, pattern='^recover_confirm_'))
    app.add_handler(CallbackQueryHandler(recover_cancel_callback, pattern='^recover_cancel$'))
    app.add_handler(CallbackQueryHandler(cleanup_confirm_callback, pattern='^cleanup_confirm$'))
    
    # =========================================================================
    # MESSAGE HANDLER (HARUS PALING AKHIR)
    # =========================================================================
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # =========================================================================
    # ERROR HANDLER
    # =========================================================================
    app.add_error_handler(error_handler)
    
    # Log jumlah handlers
    handler_count = sum(len(h) for h in app.handlers.values())
    logger.info(f"✅ All handlers registered: {handler_count} handlers")
    logger.info("=" * 60)
    
    return app


__all__ = ['create_application']
