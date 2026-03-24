# database/state_tracker.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
State Tracker - FOKUS LOKASI, POSISI, PAKAIAN
=============================================================================
"""

import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .models import ClothingState, FamilyStatus, FamilyLocation


@dataclass
class StateTracker:
    """
    State tracker untuk registrasi - FOKUS LOKASI & POSISI SAJA
    Semua data emosi ada di BotIdentity
    """
    
    registration_id: str
    
    # Location & Position
    location_bot: str = "ruang tamu"
    location_user: str = "ruang tamu"
    position_bot: str = "duduk"
    position_user: str = "duduk"
    position_relative: str = "bersebelahan"
    
    # Clothing
    clothing_state: ClothingState = field(default_factory=ClothingState)
    
    # Family State (khusus IPAR & PELAKOR)
    family_status: Optional[FamilyStatus] = None
    family_location: Optional[FamilyLocation] = None
    family_activity: Optional[str] = None
    family_estimate_return: Optional[str] = None
    
    # Activity
    activity_bot: Optional[str] = None
    activity_user: Optional[str] = None
    
    # Time
    current_time: Optional[str] = None
    time_override_history: List[Dict] = field(default_factory=list)
    
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database"""
        clothing_dict = self.clothing_state.to_dict()
        
        return {
            'registration_id': self.registration_id,
            'location_bot': self.location_bot,
            'location_user': self.location_user,
            'position_bot': self.position_bot,
            'position_user': self.position_user,
            'position_relative': self.position_relative,
            'clothing_bot_outer': clothing_dict['bot_outer_top'],
            'clothing_bot_outer_bottom': clothing_dict['bot_outer_bottom'],
            'clothing_bot_inner_top': clothing_dict['bot_inner_top'],
            'clothing_bot_inner_bottom': clothing_dict['bot_inner_bottom'],
            'clothing_user_outer': clothing_dict['user_outer_top'],
            'clothing_user_outer_bottom': clothing_dict['user_outer_bottom'],
            'clothing_user_inner_bottom': clothing_dict['user_inner_bottom'],
            'clothing_history': json.dumps(clothing_dict['history']),
            'family_status': self.family_status.value if self.family_status else None,
            'family_location': self.family_location.value if self.family_location else None,
            'family_activity': self.family_activity,
            'family_estimate_return': self.family_estimate_return,
            'activity_bot': self.activity_bot,
            'activity_user': self.activity_user,
            'current_time': self.current_time,
            'time_override_history': json.dumps(self.time_override_history),
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StateTracker':
        """Create from dictionary"""
        clothing_state = ClothingState.from_dict({
            'bot_outer_top': data.get('clothing_bot_outer'),
            'bot_outer_bottom': data.get('clothing_bot_outer_bottom'),
            'bot_inner_top': data.get('clothing_bot_inner_top'),
            'bot_inner_bottom': data.get('clothing_bot_inner_bottom'),
            'user_outer_top': data.get('clothing_user_outer'),
            'user_outer_bottom': data.get('clothing_user_outer_bottom'),
            'user_inner_bottom': data.get('clothing_user_inner_bottom'),
            'history': json.loads(data.get('clothing_history', '[]'))
        })
        
        # Parse family status
        family_status = None
        if data.get('family_status'):
            family_status = FamilyStatus(data['family_status'])
        
        family_location = None
        if data.get('family_location'):
            family_location = FamilyLocation(data['family_location'])
        
        return cls(
            registration_id=data['registration_id'],
            location_bot=data.get('location_bot', 'ruang tamu'),
            location_user=data.get('location_user', 'ruang tamu'),
            position_bot=data.get('position_bot', 'duduk'),
            position_user=data.get('position_user', 'duduk'),
            position_relative=data.get('position_relative', 'bersebelahan'),
            clothing_state=clothing_state,
            family_status=family_status,
            family_location=family_location,
            family_activity=data.get('family_activity'),
            family_estimate_return=data.get('family_estimate_return'),
            activity_bot=data.get('activity_bot'),
            activity_user=data.get('activity_user'),
            current_time=data.get('current_time'),
            time_override_history=json.loads(data.get('time_override_history', '[]')),
            updated_at=data.get('updated_at', time.time())
        )


__all__ = ['StateTracker']
