# run_deploy.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Deployment Runner for Railway - With Enhanced Error Logging
=============================================================================
"""

import os
import sys
import asyncio
import traceback
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import error logger first
from utils.error_logger import get_error_logger, log_info, log_error, log_warning, print_startup_banner

# Initialize error logger
error_logger = get_error_logger()
print_startup_banner()

try:
    from config import settings
    from utils.logger import setup_logging
except Exception as e:
    error_logger.log_error(e, {'stage': 'import_modules'}, severity="CRITICAL")
    sys.exit(1)

logger = setup_logging("AMORIA-DEPLOY")


def check_environment() -> bool:
    """Check environment without interactive input"""
    log_info("=" * 60)
    log_info("🔍 CHECKING ENVIRONMENT (DEPLOYMENT MODE)")
    log_info("=" * 60)
    
    errors = []
    warnings = []
    
    # Check Railway environment
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    railway_url = os.getenv('RAILWAY_STATIC_URL')
    
    log_info(f"📡 Railway Environment: {railway_env or 'Not detected'}")
    log_info(f"📡 Railway Domain: {railway_domain or 'Not set'}")
    log_info(f"📡 Railway URL: {railway_url or 'Not set'}")
    
    # Check .env file
    env_path = Path(".env")
    if not env_path.exists():
        log_warning("⚠️ .env file not found! Using environment variables.")
    
    # Check API keys
    try:
        if not settings.deepseek_api_key or settings.deepseek_api_key == "your_deepseek_api_key_here":
            errors.append("DeepSeek API key not configured")
            log_error("DeepSeek API key missing")
        else:
            log_info(f"✅ DeepSeek API Key: {settings.deepseek_api_key[:10]}...")
        
        if not settings.telegram_token or settings.telegram_token == "your_telegram_bot_token_here":
            errors.append("Telegram token not configured")
            log_error("Telegram token missing")
        else:
            log_info(f"✅ Telegram Token: {settings.telegram_token[:10]}...")
        
        if settings.admin_id == 0:
            warnings.append("Admin ID not configured")
            log_warning("⚠️ Admin ID not configured")
        else:
            log_info(f"✅ Admin ID: {settings.admin_id}")
            
    except Exception as e:
        errors.append(f"Failed to load config: {e}")
        error_logger.log_error(e, {'stage': 'config_load'})
    
    # Create directories
    required_dirs = [
        'data', 'data/logs', 'data/backups', 
        'data/sessions', 'data/vector_db', 'data/memory'
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        log_info(f"✅ Directory: {dir_name}")
    
    if errors:
        log_error("\n❌ ERRORS FOUND:")
        for err in errors:
            log_error(f"   - {err}")
        return False
    
    if warnings:
        log_warning("\n⚠️ WARNINGS:")
        for warn in warnings:
            log_warning(f"   - {warn}")
    
    log_info("\n✅ Environment is ready!")
    return True


def run_migration() -> bool:
    """Run database migration"""
    log_info("\n" + "=" * 60)
    log_info("🗄️ RUNNING DATABASE MIGRATION")
    log_info("=" * 60)
    
    try:
        from database.migrate import run_migrations
        import asyncio
        
        success = asyncio.run(run_migrations())
        
        if success:
            log_info("✅ Migration completed")
            return True
        else:
            log_error("❌ Migration failed")
            return False
            
    except Exception as e:
        error_logger.log_error(e, {'stage': 'migration'}, severity="ERROR")
        return False


def start_bot() -> bool:
    """Start the bot with error handling"""
    log_info("\n" + "=" * 60)
    log_info("🚀 STARTING AMORIA ON RAILWAY")
    log_info("=" * 60)
    
    try:
        from main import main
        asyncio.run(main())
        return True
    except KeyboardInterrupt:
        log_info("\n👋 Bot stopped")
        return True
    except Exception as e:
        error_logger.log_error(e, {'stage': 'bot_start'}, severity="CRITICAL")
        return False


def main():
    """Main runner untuk deployment"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     💜 AMORIA 9.9 - Virtual Human dengan Jiwa                   ║
║     Deployment Mode (Railway)                                   ║
║                                                                  ║
║     🔧 Automatic Setup:                                         ║
║     • Checking environment variables                           ║
║     • Creating directories                                      ║
║     • Running database migration                                ║
║     • Starting bot with error logging                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check environment
    if not check_environment():
        log_error("Environment check failed. Please set environment variables.")
        sys.exit(1)
    
    # Step 2: Run migration
    if not run_migration():
        log_warning("Migration failed, but continuing...")
    
    # Step 3: Start bot
    log_info("\n" + "=" * 60)
    log_info("🚀 STARTING BOT ON RAILWAY...")
    log_info("📡 All errors will be logged to Railway console")
    log_info("=" * 60)
    
    success = start_bot()
    
    if not success:
        log_error("Bot failed to start")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_logger = get_error_logger()
        error_logger.log_error(e, {'stage': 'deploy_main'}, severity="CRITICAL")
        sys.exit(1)
