# identity/bot_identity.py
# -*- coding: utf-8 -*-
"""
AMORIA - Virtual Human dengan Jiwa
Bot Identity - SINGLE SOURCE OF TRUTH
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from database.models import CharacterRole


class BotPersonalityType(str, Enum):
    """Tipe kepribadian bot"""
    GENIT = "genit"
    PENASARAN = "penasaran"
    BERANI = "berani"
    MALUMALU = "malu-malu"
    MANIS = "manis"
    POLOS = "polos"
    HANGAT = "hangat"
    INTENS = "intens"


@dataclass
class BotPhysicalProfile:
    """Profil fisik bot"""
    name: str = ""
    age: int = 22
    height: int = 165
    weight: int = 52
    chest: str = "34B"
    hijab: bool = False
    hair_color: str = "hitam"
    eye_color: str = "coklat"
    skin_tone: str = "sawo matang"
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'chest': self.chest,
            'hijab': self.hijab,
            'hair_color': self.hair_color,
            'eye_color': self.eye_color,
            'skin_tone': self.skin_tone
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BotPhysicalProfile':
        return cls(
            name=data.get('name', ''),
            age=data.get('age', 22),
            height=data.get('height', 165),
            weight=data.get('weight', 52),
            chest=data.get('chest', '34B'),
            hijab=data.get('hijab', False),
            hair_color=data.get('hair_color', 'hitam'),
            eye_color=data.get('eye_color', 'coklat'),
            skin_tone=data.get('skin_tone', 'sawo matang')
        )


@dataclass
class BotPersonality:
    """Kepribadian bot"""
    type: BotPersonalityType = BotPersonalityType.MANIS
    traits: List[str] = field(default_factory=lambda: ["manis", "ramah"])
    speaking_style: str = "santai"
    intimacy_style: str = "lembut"
    response_length: str = "sedang"
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type.value,
            'traits': self.traits,
            'speaking_style': self.speaking_style,
            'intimacy_style': self.intimacy_style,
            'response_length': self.response_length
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BotPersonality':
        return cls(
            type=BotPersonalityType(data.get('type', 'manis')),
            traits=data.get('traits', ["manis", "ramah"]),
            speaking_style=data.get('speaking_style', 'santai'),
            intimacy_style=data.get('intimacy_style', 'lembut'),
            response_length=data.get('response_length', 'sedang')
        )


@dataclass
class BotFamilyRelation:
    """Hubungan keluarga bot (khusus IPAR)"""
    has_older_sister: bool = False
    sister_name: Optional[str] = None
    sister_panggilan: Optional[str] = None
    lives_with_sister: bool = False
    user_is_sister_husband: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'has_older_sister': self.has_older_sister,
            'sister_name': self.sister_name,
            'sister_panggilan': self.sister_panggilan,
            'lives_with_sister': self.lives_with_sister,
            'user_is_sister_husband': self.user_is_sister_husband
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BotFamilyRelation':
        return cls(
            has_older_sister=data.get('has_older_sister', False),
            sister_name=data.get('sister_name'),
            sister_panggilan=data.get('sister_panggilan'),
            lives_with_sister=data.get('lives_with_sister', False),
            user_is_sister_husband=data.get('user_is_sister_husband', False)
        )


@dataclass
class BotIdentity:
    """
    IDENTITAS BOT - SINGLE SOURCE OF TRUTH
    Digunakan oleh semua module (registration, AI, handler)
    """
    
    # Core identity
    name: str
    role: CharacterRole
    
    # Components
    physical: BotPhysicalProfile = field(default_factory=BotPhysicalProfile)
    personality: BotPersonality = field(default_factory=BotPersonality)
    family: BotFamilyRelation = field(default_factory=BotFamilyRelation)
    
    # State (dinamis)
    emotion: str = "netral"
    arousal: int = 0
    mood: str = "normal"
    
    # Statistics
    total_climax: int = 0
    stamina: int = 100
    
    def __post_init__(self):
        """Set nama di physical jika belum di-set"""
        if not self.physical.name:
            self.physical.name = self.name
    
    @classmethod
    def create_for_role(cls, role: CharacterRole, bot_name: str) -> 'BotIdentity':
        """Factory method untuk membuat BotIdentity berdasarkan role"""
        
        # Generate physical berdasarkan role
        role_physical = {
            CharacterRole.IPAR: {'age': (20, 23), 'height': (158, 165), 'weight': (48, 55), 'chest': '34B', 'hijab': False},
            CharacterRole.TEMAN_KANTOR: {'age': (22, 26), 'height': (158, 165), 'weight': (48, 55), 'chest': '34B', 'hijab': False},
            CharacterRole.JANDA: {'age': (23, 28), 'height': (163, 170), 'weight': (52, 60), 'chest': '34C', 'hijab': False},
            CharacterRole.PELAKOR: {'age': (24, 28), 'height': (165, 172), 'weight': (55, 62), 'chest': '36C', 'hijab': False},
            CharacterRole.ISTRI_ORANG: {'age': (25, 30), 'height': (160, 168), 'weight': (50, 58), 'chest': '34C', 'hijab': True},
            CharacterRole.PDKT: {'age': (19, 23), 'height': (155, 163), 'weight': (45, 52), 'chest': '32B', 'hijab': False},
            CharacterRole.SEPUPU: {'age': (18, 22), 'height': (155, 162), 'weight': (45, 52), 'chest': '32B', 'hijab': False},
            CharacterRole.TEMAN_SMA: {'age': (18, 21), 'height': (158, 165), 'weight': (48, 55), 'chest': '32B', 'hijab': False},
            CharacterRole.MANTAN: {'age': (23, 27), 'height': (160, 168), 'weight': (50, 58), 'chest': '34B', 'hijab': False},
        }
        
        config = role_physical.get(role, role_physical[CharacterRole.PDKT])
        
        physical = BotPhysicalProfile(
            name=bot_name,
            age=random.randint(config['age'][0], config['age'][1]),
            height=random.randint(config['height'][0], config['height'][1]),
            weight=random.randint(config['weight'][0], config['weight'][1]),
            chest=config['chest'],
            hijab=config['hijab']
        )
        
        # Generate personality berdasarkan role
        personality_map = {
            CharacterRole.IPAR: BotPersonality(BotPersonalityType.GENIT, ["genit", "penasaran"], "gaul, manja", "hangat", "panjang"),
            CharacterRole.TEMAN_KANTOR: BotPersonality(BotPersonalityType.BERANI, ["profesional", "liar"], "profesional", "berani", "sedang"),
            CharacterRole.JANDA: BotPersonality(BotPersonalityType.BERANI, ["berpengalaman", "dewasa"], "dewasa", "intens", "panjang"),
            CharacterRole.PELAKOR: BotPersonality(BotPersonalityType.BERANI, ["agresif", "dominant"], "tegas", "agresif", "pendek"),
            CharacterRole.ISTRI_ORANG: BotPersonality(BotPersonalityType.HANGAT, ["emosional", "butuh perhatian"], "lembut", "hangat", "panjang"),
            CharacterRole.PDKT: BotPersonality(BotPersonalityType.MALUMALU, ["manis", "pemalu"], "santai, malu", "pelan", "sedang"),
            CharacterRole.SEPUPU: BotPersonality(BotPersonalityType.POLOS, ["polos", "penasaran"], "manja", "lembut", "sedang"),
            CharacterRole.TEMAN_SMA: BotPersonality(BotPersonalityType.MANIS, ["nostalgia", "hangat"], "ceria", "manis", "panjang"),
            CharacterRole.MANTAN: BotPersonality(BotPersonalityType.HANGAT, ["berpengalaman", "masih sayang"], "lembut", "intens", "pendek"),
        }
        
        personality = personality_map.get(role, BotPersonality(BotPersonalityType.MANIS))
        
        # Generate family relation untuk IPAR
        family = BotFamilyRelation()
        if role == CharacterRole.IPAR:
            family.has_older_sister = True
            family.sister_name = "Nova"
            family.sister_panggilan = "Kak Nova"
            family.lives_with_sister = True
            family.user_is_sister_husband = True
        
        return cls(
            name=bot_name,
            role=role,
            physical=physical,
            personality=personality,
            family=family
        )
    
    def get_full_prompt(self) -> str:
        """Dapatkan identitas lengkap untuk prompt AI"""
        hijab = "berhijab" if self.physical.hijab else "tidak berhijab"
        
        lines = [
            "🤖 **IDENTITAS BOT:**",
            f"Nama: {self.name}",
            f"Usia: {self.physical.age} tahun",
            f"Tinggi: {self.physical.height}cm | Berat: {self.physical.weight}kg",
            f"Dada: {self.physical.chest} | {hijab}",
            "",
            f"🎭 **KEPRIBADIAN:**",
            f"Tipe: {self.personality.type.value}",
            f"Sifat: {', '.join(self.personality.traits)}",
            f"Gaya bicara: {self.personality.speaking_style}",
            f"Gaya intim: {self.personality.intimacy_style}",
        ]
        
        if self.family.has_older_sister:
            lines.extend([
                "",
                "👨‍👩‍👧 **HUBUNGAN KELUARGA:**",
                f"• Memiliki kakak perempuan bernama {self.family.sister_name}",
                f"• Panggilan untuk kakak: {self.family.sister_panggilan} (WAJIB)",
                f"• Tinggal bersama kakak",
                f"• User adalah suami dari {self.family.sister_name}"
            ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Konversi ke dictionary untuk database"""
        return {
            'name': self.name,
            'role': self.role.value,
            'physical': self.physical.to_dict(),
            'personality': self.personality.to_dict(),
            'family': self.family.to_dict(),
            'state': {
                'emotion': self.emotion,
                'arousal': self.arousal,
                'mood': self.mood,
                'stamina': self.stamina,
                'total_climax': self.total_climax
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BotIdentity':
        """Load dari dictionary"""
        physical = BotPhysicalProfile.from_dict(data.get('physical', {}))
        personality = BotPersonality.from_dict(data.get('personality', {}))
        family = BotFamilyRelation.from_dict(data.get('family', {}))
        state = data.get('state', {})
        
        return cls(
            name=data.get('name', 'Amoria'),
            role=CharacterRole(data.get('role', 'pdkt')),
            physical=physical,
            personality=personality,
            family=family,
            emotion=state.get('emotion', 'netral'),
            arousal=state.get('arousal', 0),
            mood=state.get('mood', 'normal'),
            total_climax=state.get('total_climax', 0),
            stamina=state.get('stamina', 100)
        )


__all__ = [
    'BotPersonalityType',
    'BotPhysicalProfile',
    'BotPersonality',
    'BotFamilyRelation',
    'BotIdentity',
]
