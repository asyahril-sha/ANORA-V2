# anora/intimacy.py
"""
ANORA Intimacy - Main Module
Menyatukan semua sistem intimacy menjadi satu API sederhana.
Untuk dipanggil oleh roleplay_integration.py dan file lainnya.
"""

import logging
from typing import Dict, Optional, Tuple

from .intimacy_flow import get_anora_intimacy, anora_intimacy, IntimacyFlow
from .intimacy_core import (
    IntimacyPhase, StaminaSystem, ArousalSystem,
    PositionDatabase, ClimaxLocationDatabase, MoansDatabase, FlashbackDatabase
)

logger = logging.getLogger(__name__)

# =============================================================================
# MAIN INTIMACY CLASS (Wrapper)
# =============================================================================

class AnoraIntimacy:
    """
    Wrapper untuk IntimacyFlow.
    Menyediakan API sederhana untuk dipanggil dari luar.
    """
    
    def __init__(self):
        self._flow = None
    
    @property
    def flow(self) -> IntimacyFlow:
        """Dapatkan IntimacyFlow instance"""
        if self._flow is None:
            self._flow = get_anora_intimacy()
        return self._flow
    
    def can_start_intimacy(self, level: int) -> Tuple[bool, str]:
        """
        Cek apakah bisa mulai intim
        Returns: (can_start, message)
        """
        return self.flow.can_start_intimacy(level)
    
    def start_intimacy(self) -> str:
        """Mulai sesi intim"""
        return self.flow.start_intimacy()
    
    def process_intimacy_message(self, pesan_mas: str, level: int) -> Optional[str]:
        """
        Proses pesan intim
        Returns: respons Nova atau None jika bukan pesan intim
        """
        return self.flow.process_intimacy_message(pesan_mas, level)
    
    def update_from_pesan(self, pesan_mas: str, level: int):
        """Update arousal dan desire dari pesan Mas"""
        self.flow.update_from_pesan(pesan_mas, level)
    
    def get_status(self) -> str:
        """Dapatkan status intimacy lengkap"""
        return self.flow.get_status()
    
    def get_stamina_status(self) -> Tuple[int, int, str, str]:
        """Dapatkan status stamina (nova, mas, nova_status, mas_status)"""
        return (
            self.flow.stamina.nova_current,
            self.flow.stamina.mas_current,
            self.flow.stamina.get_nova_status(),
            self.flow.stamina.get_mas_status()
        )
    
    def get_arousal_state(self) -> Dict:
        """Dapatkan state arousal"""
        return self.flow.arousal.get_state()
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Dict:
        """Rekam climax manual"""
        return self.flow.stamina.record_climax(who, is_heavy)
    
    def end_intimacy(self) -> str:
        """Akhiri sesi intim"""
        return self.flow.session.end()
    
    def is_active(self) -> bool:
        """Cek apakah sesi intim aktif"""
        return self.flow.session.is_active
    
    def get_current_phase(self) -> str:
        """Dapatkan fase intim saat ini"""
        return self.flow.session.phase.value if self.flow.session.phase else "waiting"
    
    def change_position(self, position: str = None) -> Tuple[str, str, str]:
        """Ganti posisi"""
        return self.flow.session.change_position(position)
    
    def get_climax_request(self, location: str = None) -> str:
        """Dapatkan request climax"""
        return self.flow.session.get_climax_request(location)
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return self.flow.to_dict()
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        self.flow.from_dict(data)


# =============================================================================
# SINGLETON
# =============================================================================

_anora_intimacy_instance: Optional[AnoraIntimacy] = None


def get_anora_intimacy() -> AnoraIntimacy:
    """
    Dapatkan instance AnoraIntimacy (singleton)
    """
    global _anora_intimacy_instance
    if _anora_intimacy_instance is None:
        _anora_intimacy_instance = AnoraIntimacy()
        logger.info("💕 ANORA Intimacy initialized")
    return _anora_intimacy_instance


# =============================================================================
# EXPORTED FUNCTIONS (untuk kemudahan import)
# =============================================================================

def can_start_intimacy(level: int) -> Tuple[bool, str]:
    """Cek apakah bisa mulai intim"""
    return get_anora_intimacy().can_start_intimacy(level)


def start_intimacy() -> str:
    """Mulai sesi intim"""
    return get_anora_intimacy().start_intimacy()


def process_intimacy_message(pesan_mas: str, level: int) -> Optional[str]:
    """Proses pesan intim"""
    return get_anora_intimacy().process_intimacy_message(pesan_mas, level)


def get_intimacy_status() -> str:
    """Dapatkan status intimacy"""
    return get_anora_intimacy().get_status()


def end_intimacy() -> str:
    """Akhiri sesi intim"""
    return get_anora_intimacy().end_intimacy()


def is_intimacy_active() -> bool:
    """Cek apakah sesi intim aktif"""
    return get_anora_intimacy().is_active()


def get_stamina_status() -> Tuple[int, int, str, str]:
    """Dapatkan status stamina"""
    return get_anora_intimacy().get_stamina_status()


# =============================================================================
# DIRECT ACCESS (untuk kompatibilitas dengan kode lama)
# =============================================================================

# Re-export untuk kemudahan import
__all__ = [
    # Classes
    'AnoraIntimacy',
    'IntimacyFlow',
    'IntimacyPhase',
    'StaminaSystem',
    'ArousalSystem',
    'PositionDatabase',
    'ClimaxLocationDatabase',
    'MoansDatabase',
    'FlashbackDatabase',
    
    # Functions
    'get_anora_intimacy',
    'can_start_intimacy',
    'start_intimacy',
    'process_intimacy_message',
    'get_intimacy_status',
    'end_intimacy',
    'is_intimacy_active',
    'get_stamina_status',
    
    # Singleton instance
    'anora_intimacy',
]

# Singleton instance untuk kemudahan import
anora_intimacy = get_anora_intimacy()
