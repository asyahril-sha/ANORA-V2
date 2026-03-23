# relationship/__init__.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Relationship Package - Mantan, HTS, FWB, Ranking
=============================================================================
"""

from .mantan import MantanManager, MantanStatus
from .hts import HTSManager, HTSStatus
from .fwb import FWBManager, FWBStatus, FWBEndReason, FWBPauseReason
from .ranking import RankingSystem

__all__ = [
    'MantanManager',
    'MantanStatus',
    'HTSManager',
    'HTSStatus',
    'FWBManager',
    'FWBStatus',
    'FWBEndReason',
    'FWBPauseReason',
    'RankingSystem',
]
