# relationship/mantan.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Mantan Manager - Mengelola mantan dari PDKT yang putus
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class MantanStatus(str, Enum):
    """Status mantan"""
    PUTUS = "putus"
    FWB_REQUESTED = "fwb_requested"
    FWB_ACCEPTED = "fwb_accepted"
    FWB_DECLINED = "fwb_declined"
    FWB_ENDED = "fwb_ended"


class FWBRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class MantanManager:
    """
    Manager untuk mantan dari PDKT
    - Data mantan disimpan PERMANEN
    - Bisa request jadi FWB
    - Bot punya keputusan sendiri
    """
    
    def __init__(self):
        self.mantans: Dict[int, Dict[str, Dict]] = {}
        self.fwb_requests: Dict[str, Dict] = {}
        self.flashbacks: Dict[str, List[Dict]] = {}
        logger.info("✅ MantanManager initialized")
    
    def add_mantan(self, user_id: int, registration_data: Dict, putus_reason: str) -> str:
        """
        Tambah mantan dari karakter yang di-end
        
        Args:
            user_id: ID user (admin_id)
            registration_data: Data registrasi
            putus_reason: Alasan putus
        """
        mantan_id = f"MANTAN_{user_id}_{registration_data.get('id', 'unknown')}_{int(time.time())}"
        
        mantan_data = {
            'mantan_id': mantan_id,
            'user_id': user_id,
            'registration_id': registration_data.get('id'),
            'bot_name': registration_data.get('bot_name', 'Unknown'),
            'role': registration_data.get('role', 'pdkt'),
            'status': MantanStatus.PUTUS,
            'putus_time': time.time(),
            'putus_reason': putus_reason,
            'total_chats': registration_data.get('total_chats', 0),
            'total_climax': registration_data.get('total_climax_bot', 0) + registration_data.get('total_climax_user', 0),
            'total_intim': registration_data.get('intimacy_cycle_count', 0),
            'intimacy_level': registration_data.get('level', 1),
            'first_kiss_time': registration_data.get('first_kiss_time'),
            'first_intim_time': registration_data.get('first_intim_time'),
            'last_chat_time': registration_data.get('last_updated', time.time()),
            'fwb_requests': [],
            'flashbacks': [],
            'notes': {}
        }
        
        if user_id not in self.mantans:
            self.mantans[user_id] = {}
        
        self.mantans[user_id][mantan_id] = mantan_data
        self._generate_flashback_moments(mantan_id, registration_data)
        
        logger.info(f"💔 Added mantan: {mantan_data['bot_name']} for user {user_id}")
        return mantan_id
    
    def _generate_flashback_moments(self, mantan_id: str, registration_data: Dict):
        """Generate momen untuk flashback"""
        moments = []
        
        if registration_data.get('first_kiss_time'):
            moments.append({
                'type': 'first_kiss',
                'timestamp': registration_data['first_kiss_time'],
                'description': 'Pertama kali ciuman',
                'emotion': 'romantis'
            })
        
        if registration_data.get('first_intim_time'):
            moments.append({
                'type': 'first_intim',
                'timestamp': registration_data['first_intim_time'],
                'description': 'Pertama kali intim',
                'emotion': 'hangat'
            })
        
        self.flashbacks[mantan_id] = moments
    
    def get_mantan_list(self, user_id: int) -> List[Dict]:
        """Dapatkan daftar mantan"""
        if user_id not in self.mantans:
            return []
        mantans = list(self.mantans[user_id].values())
        mantans.sort(key=lambda x: x['putus_time'], reverse=True)
        return mantans
    
    def get_mantan_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """Dapatkan mantan berdasarkan index (1-based)"""
        mantans = self.get_mantan_list(user_id)
        if 1 <= index <= len(mantans):
            return mantans[index - 1]
        return None
    
    async def request_fwb(self, user_id: int, mantan_id: str, message: str = "") -> Dict:
        """User request jadi FWB dengan mantan"""
        mantan = self.get_mantan(user_id, mantan_id)
        if not mantan:
            return {'success': False, 'reason': 'Mantan tidak ditemukan'}
        
        if mantan['status'] in [MantanStatus.FWB_ACCEPTED, MantanStatus.FWB_REQUESTED]:
            return {'success': False, 'reason': f'Sudah {mantan["status"].value}'}
        
        # Bot decide berdasarkan chemistry (intimacy level)
        accept = mantan.get('intimacy_level', 1) >= 7
        confidence = mantan.get('intimacy_level', 1) / 12
        
        if accept:
            mantan['status'] = MantanStatus.FWB_ACCEPTED
            mantan['fwb_start_time'] = time.time()
            message = f"💕 **{mantan['bot_name']} menerima request FWB-mu!**\n\nAku masih ingat kenangan kita. Sekarang {mantan['bot_name']} ada di daftar FWB."
        else:
            mantan['status'] = MantanStatus.FWB_DECLINED
            mantan['last_fwb_request_time'] = time.time()
            message = f"💔 **{mantan['bot_name']} menolak request FWB-mu**\n\nMaaf, aku rasa lebih baik kita tetap jadi mantan aja."
        
        return {
            'success': True,
            'accepted': accept,
            'bot_name': mantan['bot_name'],
            'message': message
        }
    
    def format_mantan_list(self, user_id: int) -> str:
        """Format daftar mantan"""
        mantans = self.get_mantan_list(user_id)
        if not mantans:
            return "💔 **DAFTAR MANTAN**\n\nBelum ada mantan."
        
        lines = ["💔 **DAFTAR MANTAN**", ""]
        for i, m in enumerate(mantans[:10], 1):
            days_since = int((time.time() - m['putus_time']) / 86400)
            time_text = "Hari ini" if days_since == 0 else f"{days_since} hari lalu"
            
            status_map = {
                MantanStatus.FWB_ACCEPTED: "💕 FWB",
                MantanStatus.FWB_REQUESTED: "⏳ Menunggu",
                MantanStatus.FWB_DECLINED: "❌ Ditolak",
            }
            status = status_map.get(m['status'], "💔 Mantan")
            
            lines.append(
                f"{i}. **{m['bot_name']}** ({m['role'].title()}) {status}\n"
                f"   Putus: {time_text} | {m['total_chats']} chat | {m['total_climax']} climax"
            )
        return "\n".join(lines)


__all__ = ['MantanManager', 'MantanStatus', 'FWBRequestStatus']
