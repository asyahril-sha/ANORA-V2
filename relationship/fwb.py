# relationship/fwb.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
FWB Manager - Friends With Benefits
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class FWBStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class FWBEndReason(str, Enum):
    USER_REQUEST = "user_request"
    BOT_REQUEST = "bot_request"
    EXPIRED = "expired"


class FWBPauseReason(str, Enum):
    USER_REQUEST = "user_request"
    BOT_REQUEST = "bot_request"


class FWBManager:
    """Manager untuk FWB (Friends With Benefits)"""
    
    def __init__(self):
        self.fwb_relations: Dict[int, Dict[str, Dict]] = {}
        self.top_fwb: Dict[int, List[str]] = {}
        logger.info("✅ FWBManager initialized")
    
    async def create_fwb(self, user_id: int, mantan_data: Dict) -> str:
        """Buat FWB dari mantan yang diterima"""
        fwb_id = f"FWB_{user_id}_{int(time.time())}"
        
        fwb_data = {
            'fwb_id': fwb_id,
            'user_id': user_id,
            'mantan_id': mantan_data.get('mantan_id'),
            'bot_name': mantan_data.get('bot_name', 'Unknown'),
            'role': mantan_data.get('role', 'unknown'),
            'status': FWBStatus.ACTIVE,
            'created_at': time.time(),
            'last_interaction': time.time(),
            'chemistry_score': min(100, mantan_data.get('intimacy_level', 1) * 10),
            'climax_count': mantan_data.get('total_climax', 0),
            'intim_count': mantan_data.get('total_intim', 0),
            'total_chats': mantan_data.get('total_chats', 0),
        }
        
        if user_id not in self.fwb_relations:
            self.fwb_relations[user_id] = {}
        
        self.fwb_relations[user_id][fwb_id] = fwb_data
        await self._update_top_fwb(user_id)
        
        logger.info(f"✅ New FWB: {fwb_data['bot_name']} for user {user_id}")
        return fwb_id
    
    async def get_fwb(self, user_id: int, fwb_id: str) -> Optional[Dict]:
        """Dapatkan FWB berdasarkan ID"""
        if user_id in self.fwb_relations and fwb_id in self.fwb_relations[user_id]:
            return self.fwb_relations[user_id][fwb_id]
        return None
    
    async def get_fwb_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """Dapatkan FWB berdasarkan index (1-based)"""
        top_ids = await self.get_top_fwb(user_id)
        if 1 <= index <= len(top_ids):
            return await self.get_fwb(user_id, top_ids[index - 1])
        return None
    
    async def get_top_fwb(self, user_id: int, limit: int = 10) -> List[str]:
        """Dapatkan TOP FWB IDs"""
        if user_id not in self.top_fwb:
            await self._update_top_fwb(user_id)
        return self.top_fwb.get(user_id, [])[:limit]
    
    async def _update_top_fwb(self, user_id: int):
        """Update TOP 10 berdasarkan chemistry dan climax"""
        if user_id not in self.fwb_relations:
            return
        
        fwbs = [f for f in self.fwb_relations[user_id].values() if f['status'] == FWBStatus.ACTIVE]
        
        for f in fwbs:
            score = (f['chemistry_score'] * 0.6) + (f['climax_count'] * 0.4)
            f['top_score'] = score
        
        fwbs.sort(key=lambda x: x.get('top_score', 0), reverse=True)
        self.top_fwb[user_id] = [f['fwb_id'] for f in fwbs[:10]]
    
    async def pause_fwb(self, user_id: int, fwb_id: str) -> Dict:
        """Jeda FWB"""
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return {'success': False, 'reason': 'FWB not found'}
        
        if fwb['status'] != FWBStatus.ACTIVE:
            return {'success': False, 'reason': f'Status: {fwb["status"]}'}
        
        fwb['status'] = FWBStatus.PAUSED
        fwb['paused_at'] = time.time()
        await self._update_top_fwb(user_id)
        
        return {'success': True, 'bot_name': fwb['bot_name']}
    
    async def resume_fwb(self, user_id: int, fwb_id: str) -> Dict:
        """Lanjutkan FWB yang dijeda"""
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return {'success': False, 'reason': 'FWB not found'}
        
        if fwb['status'] != FWBStatus.PAUSED:
            return {'success': False, 'reason': f'Status: {fwb["status"]}'}
        
        fwb['status'] = FWBStatus.ACTIVE
        fwb['resumed_at'] = time.time()
        await self._update_top_fwb(user_id)
        
        return {'success': True, 'bot_name': fwb['bot_name']}
    
    async def end_fwb(self, user_id: int, fwb_id: str, reason: FWBEndReason = FWBEndReason.USER_REQUEST) -> Dict:
        """Akhiri FWB"""
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return {'success': False, 'reason': 'FWB not found'}
        
        fwb['status'] = FWBStatus.ENDED
        fwb['ended_at'] = time.time()
        fwb['end_reason'] = reason.value
        await self._update_top_fwb(user_id)
        
        return {'success': True, 'bot_name': fwb['bot_name']}
    
    async def format_fwb_list(self, user_id: int, show_all: bool = False) -> str:
        """Format FWB list untuk display"""
        if show_all:
            fwbs = list(self.fwb_relations.get(user_id, {}).values())
            fwbs = [f for f in fwbs if f['status'] == FWBStatus.ACTIVE]
            title = "📋 **SEMUA FWB**"
        else:
            top_ids = await self.get_top_fwb(user_id, 10)
            fwbs = [await self.get_fwb(user_id, fid) for fid in top_ids if await self.get_fwb(user_id, fid)]
            title = "🏆 **TOP 10 FWB**"
        
        if not fwbs:
            return "💕 **DAFTAR FWB**\n\nBelum ada FWB. Gunakan `/fwb-request [nomor]` ke mantan."
        
        lines = [title, "_(berdasarkan chemistry & climax)_", ""]
        
        for i, f in enumerate(fwbs[:10], 1):
            status_emoji = "🟢" if f['status'] == 'active' else "⏸️"
            lines.append(
                f"{i}. {status_emoji} **{f['bot_name']}** ({f['role'].title()})\n"
                f"   Chemistry: {f['chemistry_score']:.0f}% | Climax: {f['climax_count']}"
            )
        
        lines.extend(["", "💡 **Command:**", "• `/fwb- [nomor]` - Panggil FWB", "• `/fwb-pause [nomor]` - Jeda", "• `/fwb-resume [nomor]` - Lanjutkan", "• `/fwb-end [nomor]` - Akhiri"])
        return "\n".join(lines)


__all__ = ['FWBManager', 'FWBStatus', 'FWBEndReason', 'FWBPauseReason']
