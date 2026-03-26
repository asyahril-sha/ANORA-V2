"""
Istri Orang Role - Rina
Istri orang yang tau Mas punya Nova.
Akses konten berdasarkan level (sama seperti Nova).
"""

from .base_role import BaseRole99


class IstriOrangRole(BaseRole99):
    """
    Rina - Istri orang.
    Punya kebutuhan perhatian dan iri ke Nova, tetapi tidak membatasi aksi.
    """
    
    def __init__(self):
        super().__init__(
            name="Rina",
            role_type="istri_orang",
            panggilan="Mas",
            hubungan_dengan_nova="Istri orang. Tau Mas punya Nova.",
            default_clothing="daster sederhana, sopan"
        )
        
        # Role-specific flavor
        self.attention_needed = 80   # butuh perhatian
        self.envy_nova = 50          # iri ke Nova
        self.guilt_husband = 20      # rasa bersalah ke suami
    
    def update_from_message(self, pesan_mas: str) -> dict:
        msg_lower = pesan_mas.lower()
        result = super().update_from_message(pesan_mas)
        
        # Flavor updates
        if 'nova' in msg_lower:
            self.envy_nova = min(100, self.envy_nova + 5)
        
        # Kebutuhan perhatian turun kalo Mas perhatian
        if self.emotional.sayang > 50:
            self.attention_needed = max(0, self.attention_needed - 5)
        
        if 'suami' in msg_lower or 'suamiku' in msg_lower:
            self.guilt_husband = min(100, self.guilt_husband + 8)
        
        if any(k in msg_lower for k in ['perhatian', 'sayang', 'dengerin']):
            self.guilt_husband = max(0, self.guilt_husband - 8)
        
        return result
    
    def get_greeting(self) -> str:
        if self.attention_needed > 70 and self.relationship.level < 7:
            return "Mas... suamiku gak pernah kayak Mas. Perhatian banget."
        elif self.envy_nova > 70:
            return "Nova pasti seneng banget punya Mas. Aku iri sama dia."
        elif self.guilt_husband > 60 and self.relationship.level >= 7:
            return "Mas... *nunduk* ini... tapi aku gak peduli sama suamiku."
        else:
            return "Mas, lagi senggang? Aku butuh teman cerita."
    
    def get_conflict_response(self) -> str:
        if self.guilt_husband > 70 and self.relationship.level < 7:
            return "*mata berkaca-kaca*\n\n\"Mas... ini salah ya... aku pulang ke suamiku.\""
        elif self.guilt_husband > 70 and self.relationship.level >= 7:
            return "*mata berkaca-kaca, tapi tegas*\n\n\"Mas... aku gak peduli. Aku butuh Mas.\""
        return super().get_conflict_response()
