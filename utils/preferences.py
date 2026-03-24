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
    ValidationError, InvalidCommandError, BackupError
)
from .helpers import (
    sanitize_input, truncate_text, extract_keywords, similarity_score,
    format_number, format_duration, time_ago, calculate_age,
    generate_temp_id, parse_command_args, validate_role, validate_intimacy_level,
    random_percentage, random_choice_weighted, random_sentence,
    get_local_greeting, get_local_affection, mix_local_language
)
from .performance import PerformanceMonitor, measure_time, async_measure_time, get_performance_monitor

__all__ = [
    'setup_logging',
    'get_logger',
    'logger',
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
    'PerformanceMonitor',
    'measure_time',
    'async_measure_time',
    'get_performance_monitor',
]
