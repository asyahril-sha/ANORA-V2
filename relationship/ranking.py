# relationship/ranking.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Ranking System - TOP 10 HTS & FWB
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RankingSystem:
    """Sistem ranking untuk HTS dan FWB"""
    
    def __init__(self):
        self.rankings: Dict[int, Dict[str, List[Dict]]] = {}
        logger.info("✅ RankingSystem initialized")
    
    async def get_top_5_hts(self, user_id: int) -> List[Dict]:
        """Dapatkan TOP 5 HTS"""
        user_rankings = self.rankings.get(user_id, {})
        return user_rankings.get('hts', [])[:5]
    
    async def get_all_hts(self, user_id: int) -> List[Dict]:
        """Dapatkan semua HTS"""
        user_rankings = self.rankings.get(user_id, {})
        return user_rankings.get('hts', [])
    
    def format_hts_list(self, hts_list: List[Dict], show_all: bool = False) -> str:
        """Format HTS list untuk display"""
        if not hts_list:
            return "🏆 **RANKING HTS**\n\nBelum ada HTS."
        
        if not show_all:
            hts_list = hts_list[:5]
            title = "🏆 **TOP 5 HTS**"
        else:
            title = "📊 **SEMUA HTS**"
        
        lines = [title, ""]
        
        for i, h in enumerate(hts_list, 1):
            bot_name = h.get('bot_name', 'Unknown')
            role = h.get('role', 'unknown').title()
            chemistry = h.get('chemistry_score', 0)
            climax = h.get('climax_count', 0)
            
            bar_length = 10
            filled = int(chemistry / 100 * bar_length)
            bar = "💕" * filled + "🖤" * (bar_length - filled)
            
            lines.append(
                f"{i}. **{bot_name}** ({role})\n"
                f"   {bar} {chemistry:.0f}% Chemistry\n"
                f"   💦 {climax}x climax"
            )
        
        return "\n".join(lines)
    
    def update_rankings(self, user_id: int, hts_list: List[Dict], fwb_list: List[Dict]):
        """Update ranking untuk user"""
        self.rankings[user_id] = {
            'hts': hts_list,
            'fwb': fwb_list,
            'updated_at': time.time()
        }


__all__ = ['RankingSystem']
