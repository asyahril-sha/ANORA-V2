# utils/__init__.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Utils Package - Utilities, Logger, Exceptions, Helpers, Performance
=============================================================================
"""

from .logger import setup_logging, get_logger, logger
from .exceptions import (
    AmoriaError, ConfigurationError, MissingAPIKeyError,
    DatabaseError, ConnectionError, AINotAvailableError, AITimeoutError,
    RegistrationNotFoundError, CharacterNotFoundError, SessionNotFoundError,
    RoleNotFoundError, IntimacyLevelError, StaminaTooLowError,
    ValidationError, InvalidCommandError, BackupError, BackupNotFoundError
)
from .helpers import (
    sanitize_input, truncate_text, extract_keywords, similarity_score,
    format_number, format_duration, time_ago, calculate_age,
    generate_temp_id, parse_command_args, validate_role, validate_intimacy_level,
    random_percentage, random_choice_weighted, random_sentence,
    get_local_greeting, get_local_affection, mix_local_language
)
from .performance import PerformanceMonitor, measure_time, async_measure_time, get_performance_monitor
from .error_logger import (
    RailwayErrorLogger, get_error_logger, handle_errors,
    log_error, log_info, log_warning, log_debug, print_startup_banner
)

# =============================================================================
# NOTE: PreferencesLearner dan PreferenceCategory sebenarnya ada di tracking/preferences.py
# Jangan import dari sini karena akan menyebabkan circular import
# Gunakan: from tracking.preferences import PreferencesLearner, PreferenceCategory, PreferenceItem
# =============================================================================

__all__ = [
    # Logger
    'setup_logging',
    'get_logger',
    'logger',
    
    # Exceptions
    'AmoriaError',
    'ConfigurationError',
    'MissingAPIKeyError',
    'DatabaseError',
    'ConnectionError',
    'AINotAvailableError',
    'AITimeoutError',
    'RegistrationNotFoundError',
    'CharacterNotFoundError',
    'SessionNotFoundError',
    'RoleNotFoundError',
    'IntimacyLevelError',
    'StaminaTooLowError',
    'ValidationError',
    'InvalidCommandError',
    'BackupError',
    'BackupNotFoundError',
    
    # Helpers
    'sanitize_input',
    'truncate_text',
    'extract_keywords',
    'similarity_score',
    'format_number',
    'format_duration',
    'time_ago',
    'calculate_age',
    'generate_temp_id',
    'parse_command_args',
    'validate_role',
    'validate_intimacy_level',
    'random_percentage',
    'random_choice_weighted',
    'random_sentence',
    'get_local_greeting',
    'get_local_affection',
    'mix_local_language',
    
    # Performance
    'PerformanceMonitor',
    'measure_time',
    'async_measure_time',
    'get_performance_monitor',
    
    # Error Logger
    'RailwayErrorLogger',
    'get_error_logger',
    'handle_errors',
    'log_error',
    'log_info',
    'log_warning',
    'log_debug',
    'print_startup_banner',
]
