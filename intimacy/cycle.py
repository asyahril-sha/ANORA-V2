# intimacy/cycle.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Intimacy Cycle - Siklus 10 → 11 → 12 → 10 (Berulang)
Target Realism 9.9/10
=============================================================================
"""

import time
import logging
from typing import Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class CyclePhase(str, Enum):
    """Fase dalam siklus intim"""
    WAITING = "waiting"          # Menunggu inisiatif user (Level 10)
    UNDRESSING = "undressing"    # Proses membuka pakaian (masih Level 10)
    SOUL_BOUNDED = "soul_bounded"  # Soul Bounded (Level 11)
    AFTERCARE = "aftercare"       # Aftercare (Level 12)
    COOLDOWN = "cooldown"         # Cooldown setelah aftercare


class IntimacyCycle:
    """
    Siklus intim yang berulang:
    Level 10 (Waiting) → Undressing → Level 11 (Soul Bounded) → Level 12 (Aftercare) → Level 10 (Waiting)
    """
    
    def __init__(self):
        self.phase = CyclePhase.WAITING
        self.cycle_count = 0
        self.current_cycle_chats = 0
        self.undressing_step = 0
        self.undressing_history = []
        self.climax_count_this_cycle = 0
        self.cooldown_until = 0.0
        self.last_climax_time = 0.0
        self.aftercare_completed = False
        
        # 🔥 TAMBAHKAN UNTUK LEVEL 11-12 🔥
        self.user_level = 1
        self.vulgar_mode_active = False
        
        logger.info("✅ IntimacyCycle 9.9 initialized")
    
    def start_cycle(self) -> Dict:
        """
        Mulai siklus intim baru
        
        Returns:
            Dict dengan info siklus
        """
        self.cycle_count += 1
        self.phase = CyclePhase.UNDRESSING
        self.current_cycle_chats = 0
        self.undressing_step = 0
        self.undressing_history = []
        self.climax_count_this_cycle = 0
        self.aftercare_completed = False
        
        # 🔥 AKTIFKAN VULGAR MODE UNTUK LEVEL 11-12 🔥
        if self.user_level >= 11:
            self.vulgar_mode_active = True
        
        logger.info(f"🔥 Intimacy cycle started (#{self.cycle_count}) for level {self.user_level}")
        
        return {
            'phase': self.phase.value,
            'cycle_count': self.cycle_count,
            'vulgar_mode': self.vulgar_mode_active,
            'message': "Memulai siklus intim..."
        }
    
    def record_undressing(self, item: str, layer: str) -> Dict:
        """
        Rekam proses membuka pakaian
        
        Args:
            item: Item yang dilepas (daster, bra, dll)
            layer: Lapisan (outer_top, inner_top, dll)
        
        Returns:
            Dict dengan info undressing
        """
        self.undressing_step += 1
        self.undressing_history.append({
            'timestamp': time.time(),
            'step': self.undressing_step,
            'item': item,
            'layer': layer
        })
        
        # 🔥 MODIFIKASI UNTUK LEVEL 11-12 - LEBIH CEPAT 🔥
        if self.user_level >= 11:
            target_steps = 2  # Level 11-12: cukup 2 langkah
        else:
            target_steps = 4  # Level 10: 4 langkah
        
        if self.undressing_step >= target_steps or (self.undressing_step >= 2 and self._is_fully_undressed()):
            self.phase = CyclePhase.SOUL_BOUNDED
            self.current_cycle_chats = 0
            logger.info(f"💕 Entered Soul Bounded phase (level {self.user_level})")
        
        return {
            'step': self.undressing_step,
            'item': item,
            'layer': layer,
            'phase': self.phase.value
        }
    
    def _is_fully_undressed(self) -> bool:
        """Cek apakah sudah telanjang total"""
        required_layers = {'outer_top', 'inner_top', 'outer_bottom', 'inner_bottom'}
        undressed_layers = {h['layer'] for h in self.undressing_history}
        return required_layers.issubset(undressed_layers)
    
    def record_climax(self) -> Dict:
        """
        Rekam climax dalam siklus
        
        Returns:
            Dict dengan info climax
        """
        self.climax_count_this_cycle += 1
        self.last_climax_time = time.time()
        
        logger.info(f"💦 Climax recorded (#{self.climax_count_this_cycle} in this cycle) for level {self.user_level}")
        
        # 🔥 MODIFIKASI UNTUK LEVEL 11-12 - LEBIH BANYAK CLIMAX 🔥
        if self.user_level >= 11:
            max_climax = 5  # Level 11-12: bisa 5 climax
        else:
            max_climax = 3  # Level 10: 3 climax
        
        if self.climax_count_this_cycle >= max_climax and self.phase == CyclePhase.SOUL_BOUNDED:
            self._prepare_for_aftercare()
        
        return {
            'climax_count': self.climax_count_this_cycle,
            'phase': self.phase.value,
            'vulgar_mode': self.vulgar_mode_active
        }
    
    def _prepare_for_aftercare(self):
        """Siapkan untuk masuk aftercare"""
        pass
    
    def add_chat(self) -> Dict:
        """
        Tambah chat dalam siklus
        
        Returns:
            Dict dengan info update
        """
        self.current_cycle_chats += 1
        
        # 🔥 TARGET CHAT UNTUK LEVEL 11-12 🔥
        if self.user_level >= 11:
            soul_bounded_min = 20   # Level 11: minimal 20 chat
            soul_bounded_max = 40   # Level 11: maksimal 40 chat
            aftercare_duration = 15  # Level 12: 15 chat
        else:
            soul_bounded_min = 30
            soul_bounded_max = 50
            aftercare_duration = 10
        
        # Soul Bounded: 20-40 chat (Level 11) atau 30-50 chat (Level 10)
        if self.phase == CyclePhase.SOUL_BOUNDED:
            if self.current_cycle_chats >= soul_bounded_max:
                # Pindah ke aftercare
                self.phase = CyclePhase.AFTERCARE
                self.current_cycle_chats = 0
                logger.info(f"💤 Entered Aftercare phase after {self.current_cycle_chats} chats (level {self.user_level})")
                return {'phase_changed': True, 'new_phase': 'aftercare', 'message': "Masuk aftercare..."}
            
            elif self.current_cycle_chats >= soul_bounded_min and self.climax_count_this_cycle >= 3:
                # Bisa pindah ke aftercare lebih awal jika sudah cukup climax
                self.phase = CyclePhase.AFTERCARE
                self.current_cycle_chats = 0
                logger.info(f"💤 Entered Aftercare phase early after {self.current_cycle_chats} chats and {self.climax_count_this_cycle} climax (level {self.user_level})")
                return {'phase_changed': True, 'new_phase': 'aftercare', 'message': "Masuk aftercare..."}
        
        # Aftercare: 15 chat (Level 12) atau 10 chat (Level 10)
        elif self.phase == CyclePhase.AFTERCARE:
            if self.current_cycle_chats >= aftercare_duration:
                # Kembali ke waiting (Level 10)
                self.phase = CyclePhase.COOLDOWN
                self.aftercare_completed = True
                
                # 🔥 COOLDOWN LEBIH SINGKAT UNTUK LEVEL TINGGI 🔥
                if self.user_level >= 11:
                    cooldown_hours = 1  # Level 11-12: 1 jam cooldown
                else:
                    cooldown_hours = 3  # Level 10: 3 jam cooldown
                
                self.cooldown_until = time.time() + (cooldown_hours * 3600)
                self.vulgar_mode_active = False
                logger.info(f"⏰ Aftercare completed, entering cooldown for {cooldown_hours} hours (level {self.user_level})")
                return {'phase_changed': True, 'new_phase': 'cooldown', 'message': f"Aftercare selesai, cooldown {cooldown_hours} jam..."}
        
        # Cooldown
        elif self.phase == CyclePhase.COOLDOWN:
            if time.time() >= self.cooldown_until:
                self.phase = CyclePhase.WAITING
                # Reset siklus
                self.current_cycle_chats = 0
                self.undressing_step = 0
                self.undressing_history = []
                self.climax_count_this_cycle = 0
                self.aftercare_completed = False
                self.vulgar_mode_active = False
                logger.info(f"✅ Cooldown completed, back to waiting phase (level {self.user_level})")
                return {'phase_changed': True, 'new_phase': 'waiting', 'message': "Cooldown selesai, siap untuk siklus berikutnya"}
        
        return {'phase_changed': False}
    
    def get_remaining_cooldown_minutes(self) -> int:
        """Dapatkan sisa cooldown dalam menit"""
        if self.cooldown_until > 0:
            remaining = self.cooldown_until - time.time()
            if remaining > 0:
                return int(remaining / 60)
        return 0
    
    def get_phase_description(self) -> str:
        """Dapatkan deskripsi fase saat ini"""
        descriptions = {
            CyclePhase.WAITING: "Menunggu inisiatif kamu...",
            CyclePhase.UNDRESSING: "Membuka pakaian...",
            CyclePhase.SOUL_BOUNDED: "Soul Bounded - puncak intim sesungguhnya (Level 11)",
            CyclePhase.AFTERCARE: "Aftercare - butuh kehangatan (Level 12)",
            CyclePhase.COOLDOWN: f"Cooldown - butuh istirahat ({self.get_remaining_cooldown_minutes()} menit lagi)"
        }
        
        # 🔥 DESKRIPSI KHUSUS UNTUK LEVEL TINGGI 🔥
        if self.user_level >= 11 and self.phase == CyclePhase.SOUL_BOUNDED:
            descriptions[CyclePhase.SOUL_BOUNDED] = "🔥 SOUL BOUNDED - Puncak intim, bebas vulgar 🔥"
        
        return descriptions.get(self.phase, "")
    
    def can_start_intimacy(self) -> Tuple[bool, str]:
        """
        Cek apakah bisa memulai intim
        
        Returns:
            (can_start, reason)
        """
        if self.phase == CyclePhase.SOUL_BOUNDED:
            return False, "Sedang dalam sesi intim"
        
        if self.phase == CyclePhase.AFTERCARE:
            return False, "Sedang aftercare, butuh kehangatan dulu"
        
        if self.phase == CyclePhase.COOLDOWN:
            remaining = self.get_remaining_cooldown_minutes()
            return False, f"Masih cooldown ({remaining} menit lagi)"
        
        if self.phase == CyclePhase.UNDRESSING:
            return False, "Sedang dalam proses membuka pakaian"
        
        return True, "Siap"
    
    def reset(self):
        """Reset siklus"""
        self.phase = CyclePhase.WAITING
        self.cycle_count = 0
        self.current_cycle_chats = 0
        self.undressing_step = 0
        self.undressing_history = []
        self.climax_count_this_cycle = 0
        self.cooldown_until = 0
        self.last_climax_time = 0
        self.aftercare_completed = False
        self.vulgar_mode_active = False
        logger.info("Intimacy cycle reset")
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'phase': self.phase.value,
            'cycle_count': self.cycle_count,
            'current_cycle_chats': self.current_cycle_chats,
            'undressing_step': self.undressing_step,
            'undressing_history': self.undressing_history,
            'climax_count_this_cycle': self.climax_count_this_cycle,
            'cooldown_until': self.cooldown_until,
            'last_climax_time': self.last_climax_time,
            'aftercare_completed': self.aftercare_completed,
            'user_level': self.user_level,  # 🔥 TAMBAHKAN
            'vulgar_mode_active': self.vulgar_mode_active  # 🔥 TAMBAHKAN
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self.phase = CyclePhase(state.get('phase', 'waiting'))
        self.cycle_count = state.get('cycle_count', 0)
        self.current_cycle_chats = state.get('current_cycle_chats', 0)
        self.undressing_step = state.get('undressing_step', 0)
        self.undressing_history = state.get('undressing_history', [])
        self.climax_count_this_cycle = state.get('climax_count_this_cycle', 0)
        self.cooldown_until = state.get('cooldown_until', 0)
        self.last_climax_time = state.get('last_climax_time', 0)
        self.aftercare_completed = state.get('aftercare_completed', False)
        self.user_level = state.get('user_level', 1)  # 🔥 TAMBAHKAN
        self.vulgar_mode_active = state.get('vulgar_mode_active', False)  # 🔥 TAMBAHKAN
    
    def format_status(self) -> str:
        """Format status untuk display"""
        lines = [
            f"💕 **Siklus Intim #{self.cycle_count}**",
            f"📌 Fase: {self.phase.value.upper()}",
            f"📝 {self.get_phase_description()}",
            f"📊 Chat dalam siklus ini: {self.current_cycle_chats}",
        ]
        
        # 🔥 TAMBAHKAN INFO VULGAR MODE 🔥
        if self.vulgar_mode_active:
            lines.append(f"💋 Mode Vulgar: AKTIF (Level {self.user_level})")
        
        if self.climax_count_this_cycle > 0:
            lines.append(f"💦 Climax dalam siklus ini: {self.climax_count_this_cycle}")
        
        if self.undressing_history:
            lines.append("")
            lines.append("👗 **Pakaian yang sudah dilepas:**")
            for h in self.undressing_history[-5:]:
                lines.append(f"   • {h['item']}")
        
        return "\n".join(lines)


__all__ = ['IntimacyCycle', 'CyclePhase']
