# utils/error_logger.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Centralized Error Logger for Railway Deployment
=============================================================================
"""

import sys
import traceback
import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps

# Setup logging untuk Railway
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Railway capture stdout
        logging.FileHandler('amoria_error.log')  # Local fallback
    ]
)

logger = logging.getLogger("AMORIA")


class RailwayErrorLogger:
    """
    Centralized error logger untuk Railway deployment
    - Menangkap semua exception
    - Format error untuk Railway log
    - JSON format untuk mudah dibaca
    """
    
    def __init__(self):
        self.error_count = 0
        self.error_history = []
        self.start_time = datetime.now()
        
        # Railway environment detection
        self.is_railway = bool(os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PUBLIC_DOMAIN'))
        
        logger.info(f"🚀 RailwayErrorLogger initialized | Railway mode: {self.is_railway}")
        if self.is_railway:
            logger.info("📡 Railway environment detected - enhanced logging enabled")
    
    def log_error(self, error: Exception, context: Optional[Dict] = None, severity: str = "ERROR"):
        """
        Log error dengan detail lengkap untuk Railway
        
        Args:
            error: Exception object
            context: Dictionary dengan konteks error
            severity: ERROR, WARNING, CRITICAL
        """
        self.error_count += 1
        
        # Format error details
        error_details = {
            'timestamp': datetime.now().isoformat(),
            'error_id': self.error_count,
            'severity': severity,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'railway_mode': self.is_railway
        }
        
        # Simpan ke history
        self.error_history.append(error_details)
        if len(self.error_history) > 100:
            self.error_history.pop(0)
        
        # Log dengan format Railway-friendly
        if severity == "CRITICAL":
            logger.critical(self._format_error_for_railway(error_details))
        elif severity == "ERROR":
            logger.error(self._format_error_for_railway(error_details))
        elif severity == "WARNING":
            logger.warning(self._format_error_for_railway(error_details))
        else:
            logger.info(self._format_error_for_railway(error_details))
        
        # Jika di Railway, juga output JSON untuk parsing
        if self.is_railway:
            self._log_json_to_railway(error_details)
        
        return error_details
    
    def _format_error_for_railway(self, error_details: Dict) -> str:
        """Format error untuk Railway log"""
        lines = [
            "=" * 80,
            f"🚨 ERROR #{error_details['error_id']} [{error_details['severity']}]",
            f"📅 Time: {error_details['timestamp']}",
            f"🔍 Type: {error_details['error_type']}",
            f"💬 Message: {error_details['error_message']}",
            "📚 Traceback:",
            error_details['traceback'],
        ]
        
        if error_details['context']:
            lines.append("📌 Context:")
            for key, value in error_details['context'].items():
                lines.append(f"   • {key}: {value}")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _log_json_to_railway(self, error_details: Dict):
        """Log JSON format untuk Railway monitoring"""
        json_output = {
            'type': 'error',
            'error_id': error_details['error_id'],
            'severity': error_details['severity'],
            'error_type': error_details['error_type'],
            'message': error_details['error_message'],
            'timestamp': error_details['timestamp'],
            'railway': self.is_railway
        }
        logger.info(f"JSON_ERROR: {json.dumps(json_output)}")
    
    def log_info(self, message: str, context: Optional[Dict] = None):
        """Log info message"""
        logger.info(self._format_message_for_railway("INFO", message, context))
    
    def log_warning(self, message: str, context: Optional[Dict] = None):
        """Log warning message"""
        logger.warning(self._format_message_for_railway("WARNING", message, context))
    
    def log_debug(self, message: str, context: Optional[Dict] = None):
        """Log debug message"""
        logger.debug(self._format_message_for_railway("DEBUG", message, context))
    
    def _format_message_for_railway(self, level: str, message: str, context: Optional[Dict]) -> str:
        """Format message untuk Railway"""
        if context:
            return f"[{level}] {message} | Context: {json.dumps(context)}"
        return f"[{level}] {message}"
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik error"""
        return {
            'total_errors': self.error_count,
            'recent_errors': self.error_history[-10:],
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'railway_mode': self.is_railway
        }
    
    def print_startup_banner(self):
        """Print startup banner untuk Railway log"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     💜 AMORIA 9.9 - Virtual Human dengan Jiwa                   ║
║     🚀 Starting on Railway                                      ║
║                                                                  ║
║     📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}     ║
║     🌍 Railway Mode: {self.is_railway}                                        ║
║                                                                  ║
║     📡 Logging all errors to Railway console                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        logger.info(banner)


# =============================================================================
# DECORATOR FOR ERROR HANDLING
# =============================================================================

def handle_errors(severity: str = "ERROR", log_context: bool = True):
    """
    Decorator untuk menangkap error di function
    
    Args:
        severity: ERROR, WARNING, CRITICAL
        log_context: Apakah log context dari function
    
    Usage:
        @handle_errors(severity="CRITICAL")
        async def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_logger = get_error_logger()
                
                context = {}
                if log_context:
                    context = {
                        'function': func.__name__,
                        'module': func.__module__,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys())
                    }
                
                error_logger.log_error(e, context, severity)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_logger = get_error_logger()
                
                context = {}
                if log_context:
                    context = {
                        'function': func.__name__,
                        'module': func.__module__,
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys())
                    }
                
                error_logger.log_error(e, context, severity)
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_error_logger = None


def get_error_logger() -> RailwayErrorLogger:
    """Dapatkan instance RailwayErrorLogger"""
    global _error_logger
    if _error_logger is None:
        _error_logger = RailwayErrorLogger()
    return _error_logger


def log_error(error: Exception, context: Optional[Dict] = None, severity: str = "ERROR"):
    """Shortcut function untuk log error"""
    get_error_logger().log_error(error, context, severity)


def log_info(message: str, context: Optional[Dict] = None):
    """Shortcut function untuk log info"""
    get_error_logger().log_info(message, context)


def log_warning(message: str, context: Optional[Dict] = None):
    """Shortcut function untuk log warning"""
    get_error_logger().log_warning(message, context)


def log_debug(message: str, context: Optional[Dict] = None):
    """Shortcut function untuk log debug"""
    get_error_logger().log_debug(message, context)


def print_startup_banner():
    """Print startup banner"""
    get_error_logger().print_startup_banner()


__all__ = [
    'RailwayErrorLogger',
    'get_error_logger',
    'handle_errors',
    'log_error',
    'log_info',
    'log_warning',
    'log_debug',
    'print_startup_banner',
]
