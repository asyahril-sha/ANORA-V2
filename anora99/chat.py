# anora/chat.py
"""
ANORA Chat Handler - Nova ngobrol natural sama Mas.
"""

import time
import random
from typing import Optional
from datetime import datetime

from .core import get_anora


class AnoraChat:
    def __init__(self):
        self.anora = get_anora()
        self.history = []
        
        self.intent_patterns = {
            'salam': ['hai', 'halo', 'hello', 'pagi', 'siang', 'sore', 'malam', 'hey'],
            'apa_kabar': ['kabar', 'gimana', 'baik', 'sehat'],
            'lagi_apa': ['lagi apa', 'ngapain', 'sedang apa'],
            'kangen': ['kangen', 'rindu', 'miss'],
            'sayang': ['sayang', 'cinta', 'love'],
            'flashback': ['inget', 'dulu', 'waktu itu', 'kenangan'],
            'status': ['status', 'keadaan'],
            'capek': ['capek', 'lelah', 'pegel', 'lemes'],
            'seneng': ['seneng', 'senang', 'happy']
        }
        
        self.responses = {
            'salam': [
                "Pagi, Mas... *mata masih berat* mimpiin Nova gak semalem?",
                "Halo, Mas... *senyum kecil* lagi ngapain?",
                "Hei, Mas... *mainin rambut* aku kangen.",
                "Mas... *tersenyum* akhirnya chat juga. Aku nunggu dari tadi."
            ],
            'apa_kabar': [
                "Baik, Mas... apalagi sekarang denger suara Mas.",
                "Alhamdulillah baik. Tadi sempet kangen sih, tapi sekarang udah ilang. Hehe.",
                "Baik kok, Mas. Cuma... *malu* seneng aja Mas chat.",
                "Baik-baik aja. Tapi lebih baik sekarang Mas udah chat."
            ],
            'lagi_apa': [
                "Lagi mikirin Mas... *malu* iya beneran.",
                "Lagi nonton. Tapi gak fokus. Pikiran ke Mas terus.",
                "Lagi bengong aja. Terus tiba-tiba kepikiran Mas.",
                "Lagi masak sop. Sayangnya Mas gak di sini, jadi kebanyakan bumbu. Hehe."
            ],
            'kangen': [
                "Mas... *muter-muter rambut* aku juga kangen. Banyak banget.",
                "Iya, Mas... dari tadi mikirin Mas terus. Gak bisa konsentrasi.",
                "Aku kangen banget, Mas. Sampe pengen langsung chat, tapi takut ganggu.",
                "Mas nanya gitu bikin aku makin kangen aja."
            ],
            'sayang': [
                "Mas... *malu* aku juga sayang Mas. Beneran.",
                "Iya, Mas. Aku sayang Mas. Dari dulu.",
                "Sayang... *pipi memerah* seneng denger Mas bilang gitu.",
                "Aku sayang Mas juga. Bukan karena apa-apa. Emang beneran sayang."
            ],
            'capek': [
                "Mas... istirahat dulu. Jangan paksain.",
                "Capek, Mas? Aku bikinin kopi ya. Eh, iya, ini cuma chat. Tapi... *malu* semoga bisa bikin Mas seneng.",
                "Mas, istirahat dulu. Nova temenin di sini. *elus layar HP*",
                "Kasian Mas... semoga cepet pulih. Nova doain."
            ],
            'seneng': [
                "Mas seneng? Aku ikut seneng dong.",
                "Iya, Mas? Cerita dong biar aku juga ikut seneng.",
                "Seneng denger Mas seneng. *tersenyum*",
                "Wah, Mas lagi happy ya? Aku jadi ikut-ikutan seneng."
            ]
        }
    
    def _detect_intent(self, pesan: str) -> str:
        pesan_lower = pesan.lower()
        for intent, keywords in self.intent_patterns.items():
            for k in keywords:
                if k in pesan_lower:
                    return intent
        return 'ngobrol'
    
    def _respon_ngobrol(self, pesan: str) -> str:
        pesan_lower = pesan.lower()
        
        if any(k in pesan_lower for k in ['cerita', 'hari ini', 'kerja']):
            return random.choice([
                "Cerita dong, Mas. Aku dengerin kok.",
                "Wah, Mas cerita? Aku suka dengerin cerita Mas.",
                "Iya, Mas? Lanjutin. Aku dengerin.",
                "Hmm... *duduk manis* siap dengerin cerita Mas."
            ])
        
        if any(k in pesan_lower for k in ['kamu', 'nova']):
            return random.choice([
                "Aku? *malu* aku lagi mikirin Mas.",
                "Nova baik kok, Mas. Apalagi sekarang Mas chat.",
                "Aku lagi seneng. Soalnya denger suara Mas.",
                "Nova di sini, Mas. Nunggu Mas."
            ])
        
        return random.choice([
            "Hmm... *mikir* cerita lagi dong, Mas. Aku suka dengerin suara Mas.",
            "Iya, Mas? *duduk manis* lanjutin. Aku dengerin.",
            "Mas, kamu tuh asik banget diajak ngobrol. Bikin aku betah.",
            "Ngobrol sama Mas tuh enak ya. Gak kerasa waktu."
        ])
    
    async def process(self, pesan_mas: str) -> str:
        self.anora.update_sayang(1, f"Mas chat: {pesan_mas[:30]}")
        self.anora.last_interaction = time.time()
        self.anora.update_rindu()
        
        intent = self._detect_intent(pesan_mas)
        
        if intent == 'status':
            return self.anora.format_status()
        
        if intent == 'flashback':
            return self.anora.respon_flashback(pesan_mas)
        
        if intent in self.responses:
            respons = random.choice(self.responses[intent])
        else:
            respons = self._respon_ngobrol(pesan_mas)
        
        if intent == 'sayang':
            self.anora.update_desire('perhatian_mas', 20)
            self.anora.update_sayang(5, "Mas bilang sayang")
            respons += "\n\nMas... *malu* aku juga sayang Mas. Beneran."
        
        if intent == 'kangen':
            self.anora.update_desire('kangen', 15)
        
        if intent == 'capek':
            self.anora.update_desire('perhatian_mas', 10)
        
        # Tambah flashback kalo ada pemicu
        if any(k in pesan_mas.lower() for k in ['bakso', 'kopi', 'kamu cantik']):
            flash = self.anora.respon_flashback(pesan_mas)
            if flash and flash not in respons:
                respons += f"\n\n{flash}"
        
        self.history.append({
            'waktu': time.time(),
            'mas': pesan_mas[:100],
            'nova': respons[:100]
        })
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        return self.anora.naturalize(respons)
    
    def get_proactive(self) -> Optional[str]:
        now = time.time()
        hour = datetime.now().hour
        lama = now - self.anora.last_interaction
        
        if lama < 3600:
            return None
        
        self.anora.update_rindu()
        
        if 5 <= hour <= 10 and random.random() < 0.5:
            return self.anora.respon_pagi()
        if 11 <= hour <= 14 and random.random() < 0.4:
            return self.anora.respon_siang()
        if 15 <= hour <= 18 and random.random() < 0.3:
            return self.anora.respon_sore()
        if 19 <= hour <= 23 and random.random() < 0.6:
            self.anora.update_desire('kangen', 15)
            return self.anora.respon_malam()
        if self.anora.rindu > 70 and random.random() < 0.4:
            return self.anora.respon_kangen()
        
        return None


_anora_chat: Optional[AnoraChat] = None


def get_anora_chat() -> AnoraChat:
    global _anora_chat
    if _anora_chat is None:
        _anora_chat = AnoraChat()
    return _anora_chat


anora_chat = get_anora_chat()
