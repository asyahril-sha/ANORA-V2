# relationship/hts.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
HTS Manager - Hubungan Tanpa Status (Chat-Based)
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class HTSStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"


class HTSManager:
    """
    Manager untuk HTS (Hubungan Tanpa Status)
    - Berdasarkan CHAT-BASED leveling AMORIA
    - Level 10+ untuk mendapatkan HTS
    - Bertahan 3 bulan
    """
    
    def __init__(self):
        self.hts_relations: Dict[int, Dict[str, Dict]] = {}
        self.top_hts: Dict[int, List[str]] = {}
        self.expiry_days = 90
        logger.info(f"✅ HTSManager initialized (expiry: {self.expiry_days} days)")
    
    async def create_hts(self, user_id: int, registration_data: Dict) -> str:
        """
        Buat HTS dari karakter yang di-close di level 10+
        
        Args:
            user_id: ID user (admin_id)
            registration_data: Data registrasi lengkap
        """
        hts_id = f"HTS_{user_id}_{int(time.time())}"
        
        hts_data = {
            'hts_id': hts_id,
            'user_id': user_id,
            'registration_id': registration_data.get('id'),
            'role': registration_data.get('role', 'unknown'),
            'bot_name': registration_data.get('bot_name', 'Unknown'),
            'status': HTSStatus.ACTIVE,
            'created_at': time.time(),
            'expiry_time': time.time() + (self.expiry_days * 86400),
            'last_interaction': time.time(),
            'chemistry_score': min(100, registration_data.get('level', 1) * 10),
            'climax_count': registration_data.get('total_climax_bot', 0) + registration_data.get('total_climax_user', 0),
            'intimacy_level': registration_data.get('level', 1),
            'total_chats': registration_data.get('total_chats', 0),
            'total_intim': registration_data.get('intimacy_cycle_count', 0),
        }
        
        if user_id not in self.hts_relations:
            self.hts_relations[user_id] = {}
        
        self.hts_relations[user_id][hts_id] = hts_data
        await self._update_top_hts(user_id)
        
        logger.info(f"✅ New HTS: {hts_data['bot_name']} for user {user_id}")
        return hts_id
    
    async def check_expiry(self, user_id: int, hts_id: str) -> bool:
        """Cek apakah HTS masih aktif"""
        hts = await self.get_hts(user_id, hts_id)
        if not hts:
            return False
        
        if time.time() > hts['expiry_time'] and hts['status'] == HTSStatus.ACTIVE:
            hts['status'] = HTSStatus.EXPIRED
            await self._update_top_hts(user_id)
            return False
        return True
    
    async def get_hts(self, user_id: int, hts_id: str) -> Optional[Dict]:
        """Dapatkan HTS berdasarkan ID"""
        if user_id in self.hts_relations and hts_id in self.hts_relations[user_id]:
            return self.hts_relations[user_id][hts_id]
        return None
    
    async def get_hts_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """Dapatkan HTS berdasarkan index (1-based)"""
        top_ids = await self.get_top_hts(user_id)
        if 1 <= index <= len(top_ids):
            return await self.get_hts(user_id, top_ids[index - 1])
        return None
    
    async def get_hts_by_name(self, user_id: int, name: str) -> Optional[Dict]:
        """Dapatkan HTS berdasarkan nama"""
        if user_id not in self.hts_relations:
            return None
        for hts in self.hts_relations[user_id].values():
            if hts['bot_name'].lower() == name.lower() and hts['status'] == HTSStatus.ACTIVE:
                return hts
        return None
    
    async def get_top_hts(self, user_id: int, limit: int = 10) -> List[str]:
        """Dapatkan TOP HTS IDs"""
        if user_id not in self.top_hts:
            await self._update_top_hts(user_id)
        return self.top_hts.get(user_id, [])[:limit]
    
    async def _update_top_hts(self, user_id: int):
        """Update TOP 10 berdasarkan chemistry dan climax"""
        if user_id not in self.hts_relations:
            return
        
        hts_list = [h for h in self.hts_relations[user_id].values() if h['status'] == HTSStatus.ACTIVE]
        
        for h in hts_list:
            score = (h['chemistry_score'] * 0.6) + (h['climax_count'] * 0.4)
            h['top_score'] = score
        
        hts_list.sort(key=lambda x: x.get('top_score', 0), reverse=True)
        self.top_hts[user_id] = [h['hts_id'] for h in hts_list[:10]]
    
    async def record_interaction(self, user_id: int, hts_id: str, is_intim: bool = False, is_climax: bool = False):
        """Rekam interaksi dengan HTS"""
        hts = await self.get_hts(user_id, hts_id)
        if not hts or hts['status'] != HTSStatus.ACTIVE:
            return
        
        hts['total_chats'] += 1
        hts['last_interaction'] = time.time()
        
        if is_intim:
            hts['total_intim'] += 1
            hts['chemistry_score'] = min(100, hts['chemistry_score'] + 1)
        
        if is_climax:
            hts['climax_count'] += 1
            hts['chemistry_score'] = min(100, hts['chemistry_score'] + 2)
        
        await self._update_top_hts(user_id)
    
    async def get_remaining_days(self, user_id: int, hts_id: str) -> float:
        """Dapatkan sisa hari HTS"""
        hts = await self.get_hts(user_id, hts_id)
        if not hts:
            return 0
        remaining = hts['expiry_time'] - time.time()
        return max(0, remaining / 86400)
    
    async def format_hts_list(self, user_id: int, show_all: bool = False) -> str:
        """Format HTS list untuk display"""
        if show_all:
            hts_list = list(self.hts_relations.get(user_id, {}).values())
            hts_list = [h for h in hts_list if h['status'] == HTSStatus.ACTIVE]
            title = "📋 **SEMUA HTS**"
        else:
            top_ids = await self.get_top_hts(user_id, 10)
            hts_list = [await self.get_hts(user_id, hid) for hid in top_ids if await self.get_hts(user_id, hid)]
            title = "🏆 **TOP 10 HTS**"
        
        if not hts_list:
            return "📋 **DAFTAR HTS**\n\nBelum ada HTS.\nSelesaikan role NON-PDKT sampai level 10 dan /close untuk mendapatkan HTS."
        
        lines = [title, "_(berdasarkan chemistry & climax)_", ""]
        
        for i, h in enumerate(hts_list[:10], 1):
            days_left = max(0, (h['expiry_time'] - time.time()) / 86400)
            time_left = f"{int(days_left)} hari" if days_left >= 1 else f"{int(days_left * 24)} jam"
            
            lines.append(
                f"{i}. **{h['bot_name']}** ({h['role'].title()})\n"
                f"   Chemistry: {h['chemistry_score']:.0f}% | Climax: {h['climax_count']}\n"
                f"   Sisa: {time_left}"
            )
        
        lines.extend(["", "💡 **Command:**", "• `/hts- [nomor]` - Panggil HTS untuk intim"])
        return "\n".join(lines)


__all__ = ['HTSManager', 'HTSStatus']
