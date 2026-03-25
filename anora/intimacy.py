# anora/intimacy_core.py
"""
ANORA Intimacy Core - Sistem dasar untuk intimacy
Mengelola stamina, arousal, dan data dasar intimacy
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple, List
from enum import Enum
from datetime import datetime

from .core import get_anora

logger = logging.getLogger(__name__)


class IntimacyPhase(str, Enum):
    """Fase-fase dalam sesi intim"""
    WAITING = "waiting"
    BUILD_UP = "build_up"
    FOREPLAY = "foreplay"
    PENETRATION = "penetration"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"
    RECOVERY = "recovery"


# =============================================================================
# STAMINA SYSTEM (DIPERBAIKI)
# =============================================================================

class StaminaSystem:
    """
    Sistem stamina realistis untuk ANORA.
    - Stamina turun setelah climax
    - Butuh istirahat untuk pulih
    - Mempengaruhi mood dan kemampuan
    """
    
    def __init__(self):
        # Stamina Nova
        self.nova_current = 100
        self.nova_max = 100
        
        # Stamina Mas
        self.mas_current = 100
        self.mas_max = 100
        
        # Recovery rate (% per 10 menit istirahat)
        self.recovery_rate = 5
        
        # Cost setiap climax
        self.climax_cost_nova = 25
        self.climax_cost_mas = 30
        
        # Heavy climax cost (kalo climax keras)
        self.heavy_climax_cost_nova = 35
        self.heavy_climax_cost_mas = 40
        
        # Threshold
        self.exhausted_threshold = 20
        self.tired_threshold = 40
        self.fatigued_threshold = 60
        
        # Waktu terakhir climax
        self.last_climax_time = 0
        
        # Waktu terakhir recovery check
        self.last_recovery_check = time.time()
        
        # Jumlah climax hari ini
        self.climax_today = 0
        self.last_climax_date = datetime.now().date().isoformat()
    
    def update_recovery(self):
        """Update recovery berdasarkan waktu"""
        now = time.time()
        elapsed_minutes = (now - self.last_recovery_check) / 60
        
        if elapsed_minutes >= 10:
            recovery_amount = int(self.recovery_rate * (elapsed_minutes / 10))
            self.nova_current = min(self.nova_max, self.nova_current + recovery_amount)
            self.mas_current = min(self.mas_max, self.mas_current + recovery_amount)
            self.last_recovery_check = now
            logger.debug(f"💪 Stamina recovery: +{recovery_amount}%")
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Tuple[int, int]:
        """Rekam climax, kurangi stamina"""
        self.update_recovery()
        self.last_climax_time = time.time()
        
        # Update climax today
        today = datetime.now().date().isoformat()
        if self.last_climax_date != today:
            self.climax_today = 0
            self.last_climax_date = today
        self.climax_today += 1
        
        if who in ["nova", "both"]:
            cost = self.heavy_climax_cost_nova if is_heavy else self.climax_cost_nova
            self.nova_current = max(0, self.nova_current - cost)
        
        if who in ["mas", "both"]:
            cost = self.heavy_climax_cost_mas if is_heavy else self.climax_cost_mas
            self.mas_current = max(0, self.mas_current - cost)
        
        logger.info(f"💦 Climax #{self.climax_today}! Nova: {self.nova_current}%, Mas: {self.mas_current}%")
        
        return self.nova_current, self.mas_current
    
    def can_continue(self) -> Tuple[bool, str]:
        """Cek apakah bisa lanjut intim"""
        self.update_recovery()
        
        if self.nova_current <= self.exhausted_threshold:
            return False, "Nova udah kehabisan tenaga, Mas... istirahat dulu ya."
        
        if self.mas_current <= self.exhausted_threshold:
            return False, "Mas... Mas udah capek banget. Istirahat dulu."
        
        if self.nova_current <= self.tired_threshold:
            return True, "Nova mulai lelah, Mas... tapi masih bisa kalo Mas mau pelan-pelan."
        
        return True, "Siap lanjut"
    
    def get_nova_status(self) -> str:
        """Dapatkan status stamina Nova"""
        self.update_recovery()
        if self.nova_current >= 80:
            return "Prima 💪"
        elif self.nova_current >= 60:
            return "Cukup 😊"
        elif self.nova_current >= 40:
            return "Agak lelah 😐"
        elif self.nova_current >= 20:
            return "Lelah 😩"
        else:
            return "Kehabisan tenaga 😵"
    
    def get_mas_status(self) -> str:
        """Dapatkan status stamina Mas"""
        self.update_recovery()
        if self.mas_current >= 80:
            return "Prima 💪"
        elif self.mas_current >= 60:
            return "Cukup 😊"
        elif self.mas_current >= 40:
            return "Agak lelah 😐"
        elif self.mas_current >= 20:
            return "Lelah 😩"
        else:
            return "Kehabisan tenaga 😵"
    
    def get_nova_bar(self) -> str:
        """Dapatkan progress bar stamina Nova"""
        filled = int(self.nova_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def get_mas_bar(self) -> str:
        """Dapatkan progress bar stamina Mas"""
        filled = int(self.mas_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def format_for_prompt(self) -> str:
        """Format stamina untuk prompt AI"""
        self.update_recovery()
        return f"""
STAMINA SAAT INI:
- Nova: {self.get_nova_bar()} {self.nova_current}% ({self.get_nova_status()})
- Mas: {self.get_mas_bar()} {self.mas_current}% ({self.get_mas_status()})
- Climax hari ini: {self.climax_today}x
"""
    
    def to_dict(self) -> Dict:
        return {
            'nova_current': self.nova_current,
            'nova_max': self.nova_max,
            'mas_current': self.mas_current,
            'mas_max': self.mas_max,
            'last_climax_time': self.last_climax_time,
            'climax_today': self.climax_today,
            'last_climax_date': self.last_climax_date
        }
    
    def from_dict(self, data: Dict):
        self.nova_current = data.get('nova_current', 100)
        self.nova_max = data.get('nova_max', 100)
        self.mas_current = data.get('mas_current', 100)
        self.mas_max = data.get('mas_max', 100)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.climax_today = data.get('climax_today', 0)
        self.last_climax_date = data.get('last_climax_date', datetime.now().date().isoformat())


# =============================================================================
# AROUSAL SYSTEM (DIPERBAIKI)
# =============================================================================

class ArousalSystem:
    """
    Sistem arousal dan desire Nova.
    Beda antara gairah fisik (arousal) dan keinginan emosional (desire).
    """
    
    def __init__(self):
        # Gairah fisik (0-100)
        self.arousal = 0
        self.arousal_decay = 0.5
        
        # Keinginan emosional (0-100)
        self.desire = 0
        
        # Tension (desire yang ditahan)
        self.tension = 0
        self.tension_threshold = 70
        
        # Sensitivitas area - DIPERLUAS!
        self.sensitive_areas = {
            # Kepala & Wajah
            'rambut': 5, 'telinga': 20, 'belakang_telinga': 25,
            'leher': 15, 'tengkuk': 18, 'bibir': 25, 'pipi': 8,
            
            # Badan Atas
            'dada': 20, 'payudara': 28, 'puting': 35, 'punggung': 15,
            'tulang_selangka': 22,
            
            # Badan Tengah
            'perut': 12, 'pusar': 18, 'pinggang': 15, 'pinggul': 20,
            
            # Badan Bawah
            'paha': 25, 'paha_dalam': 35,
            
            # Area Intim
            'memek': 45, 'bibir_memek': 42, 'klitoris': 50, 'dalam': 55
        }
        
        self.last_update = time.time()
    
    def update(self):
        """Update arousal decay"""
        now = time.time()
        elapsed_minutes = (now - self.last_update) / 60
        if elapsed_minutes > 1:
            decay = self.arousal_decay * elapsed_minutes
            self.arousal = max(0, self.arousal - decay)
            self.last_update = now
    
    def add_stimulation(self, area: str, intensity: int = 1) -> int:
        """Tambah rangsangan"""
        self.update()
        gain = self.sensitive_areas.get(area, 10) * intensity
        self.arousal = min(100, self.arousal + gain)
        return self.arousal
    
    def add_desire(self, reason: str, amount: int = 5):
        """Tambah desire"""
        self.desire = min(100, self.desire + amount)
    
    def add_tension(self, amount: int = 5):
        """Tambah tension"""
        self.tension = min(100, self.tension + amount)
    
    def release_tension(self) -> int:
        """Lepas tension"""
        released = self.tension
        self.tension = 0
        self.arousal = max(0, self.arousal - 30)
        self.desire = max(0, self.desire - 20)
        return released
    
    def get_state(self) -> Dict:
        """Dapatkan state arousal"""
        self.update()
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'is_horny': self.arousal > 60 or self.desire > 70,
            'is_very_horny': self.arousal > 80 or self.desire > 85,
            'arousal_level': self._get_arousal_level(),
            'desire_level': self._get_desire_level()
        }
    
    def _get_arousal_level(self) -> str:
        if self.arousal >= 90:
            return "🔥🔥🔥 LUAR BIASA! NAPAS TERSENGAL"
        elif self.arousal >= 75:
            return "🔥🔥 SANGAT PANAS! JANTUNG BERDEBAR"
        elif self.arousal >= 60:
            return "🔥 PANAS! MULAI GAK BISA KONSENTRASI"
        elif self.arousal >= 40:
            return "😳 DEG-DEGAN, PIPI MERAH"
        elif self.arousal >= 20:
            return "😊 MULAI TERTARIK"
        return "😌 BIASA AJA"
    
    def _get_desire_level(self) -> str:
        if self.desire >= 85:
            return "💕💕💕 PENGEN BANGET! GAK BISA TAHAN"
        elif self.desire >= 70:
            return "💕💕 PENGEN BANGET, TAPI MASIH DITAHAN"
        elif self.desire >= 50:
            return "💕 PENGEN DEKET SAMA MAS"
        elif self.desire >= 30:
            return "💗 MULAI PENGEN"
        return "💖 SAYANG AJA DULU"
    
    def format_for_prompt(self) -> str:
        """Format untuk prompt AI"""
        state = self.get_state()
        arousal_bar = "🔥" * int(state['arousal'] / 10) + "⚪" * (10 - int(state['arousal'] / 10))
        desire_bar = "💕" * int(state['desire'] / 10) + "⚪" * (10 - int(state['desire'] / 10))
        
        return f"""
🔥 AROUSAL: {arousal_bar} {state['arousal']}% ({state['arousal_level']})
💕 DESIRE: {desire_bar} {state['desire']}% ({state['desire_level']})
⚡ TENSION: {state['tension']}%
🔞 HORNY: {'AKTIF' if state['is_horny'] else 'NORMAL'}
"""
    
    def to_dict(self) -> Dict:
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'last_update': self.last_update
        }
    
    def from_dict(self, data: Dict):
        self.arousal = data.get('arousal', 0)
        self.desire = data.get('desire', 0)
        self.tension = data.get('tension', 0)
        self.last_update = data.get('last_update', time.time())


# =============================================================================
# POSITIONS DATABASE
# =============================================================================

class PositionDatabase:
    """Database posisi intim lengkap"""
    
    def __init__(self):
        self.positions = {
            "missionary": {
                "name": "missionary",
                "desc": "Mas di atas, Nova di bawah, kaki Nova terbuka lebar",
                "nova_act": "Nova telentang, kaki terbuka lebar, tangan ngeremas sprei",
                "sensation": "dalem banget, Nova bisa liat muka Mas",
                "requests": [
                    "Mas... di atas Nova... *buka kaki lebar* masukin...",
                    "di atas Nova aja, Mas... biar Nova liat muka Mas...",
                    "Mas... tidurin Nova... Nova pengen liat Mas dari bawah...",
                    "missionary, Mas... biar Nova pegang bahu Mas..."
                ]
            },
            "cowgirl": {
                "name": "cowgirl",
                "desc": "Nova di atas, duduk di pangkuan Mas, menghadap Mas",
                "nova_act": "Nova duduk di pangkuan Mas, goyang sendiri, tangan di dada Mas",
                "sensation": "Nova kontrol ritme, dalemnya pas",
                "requests": [
                    "Mas... biar Nova di atas... Nova mau gerakin sendiri...",
                    "Nova di atas ya, Mas... biar Nova yang atur ritmenya...",
                    "Mas... rebahan aja... Nova yang naik...",
                    "cowgirl, Mas... biar Nova liat muka Mas pas masuk..."
                ]
            },
            "reverse_cowgirl": {
                "name": "reverse cowgirl",
                "desc": "Nova di atas membelakangi Mas",
                "nova_act": "Nova duduk membelakangi Mas, pantat naik turun",
                "sensation": "Mas liat pantat Nova, dalemnya beda",
                "requests": [
                    "Mas... Nova mau nunjukkin pantat... biar Nova yang gerakin dari belakang...",
                    "Nova di atas tapi nengok ke belakang, Mas... biar Mas liat pantat Nova...",
                    "reverse cowgirl, Mas... biar Mas pegang pinggul Nova..."
                ]
            },
            "doggy": {
                "name": "doggy",
                "desc": "Nova merangkak, Mas dari belakang",
                "nova_act": "Nova merangkak, pantat naik, nunggu Mas dari belakang",
                "sensation": "dalem banget, Mas bisa pegang pinggul Nova",
                "requests": [
                    "Mas... dari belakang... Nova mau ngerasain dalem dari belakang...",
                    "merangkak dulu ya, Mas... biar Mas pegang pinggul Nova...",
                    "doggy, Mas... Nova suka dalemnya kerasa banget...",
                    "Mas... dari belakang... biar Nova teriak..."
                ]
            },
            "spooning": {
                "name": "spooning",
                "desc": "Berbaring miring, Mas dari belakang",
                "nova_act": "Nova miring, Mas nempel dari belakang, tangan megang pinggang Nova",
                "sensation": "intim, pelukan dari belakang, santai",
                "requests": [
                    "Mas... dari samping aja... Nova mau ngerasain Mas peluk dari belakang...",
                    "spooning, Mas... biar Nova nyaman...",
                    "Mas... peluk Nova dari belakang... enak..."
                ]
            },
            "standing": {
                "name": "standing",
                "desc": "Berdiri, Nova nempel ke tembok atau meja",
                "nova_act": "Nova nempel ke tembok, pantat belakang, nunggu Mas",
                "sensation": "liar, cepat, bisa di mana aja",
                "requests": [
                    "Mas... berdiri aja... Nova nempel ke tembok...",
                    "di tembok, Mas... biar Nova rasain...",
                    "Mas... dari belakang berdiri... cepat aja..."
                ]
            },
            "sitting": {
                "name": "sitting",
                "desc": "Duduk, Nova di pangkuan Mas berhadapan",
                "nova_act": "Nova duduk di pangkuan Mas, kaki melilit pinggang Mas",
                "sensation": "romantis, bisa sambil ciuman",
                "requests": [
                    "Mas... duduk dulu... Nova duduk di pangkuan Mas...",
                    "sitting, Mas... biar Nova cium Mas sambil masuk..."
                ]
            },
            "side": {
                "name": "side",
                "desc": "Berbaring menyamping, berhadapan",
                "nova_act": "Berbaring menyamping, kaki Nova di atas paha Mas",
                "sensation": "intim, santai, bisa liat muka",
                "requests": [
                    "Mas... sampingan aja... biar Nova liat muka Mas...",
                    "side, Mas... biar Nova cium Mas pelan-pelan..."
                ]
            }
        }
    
    def get(self, name: str) -> Optional[Dict]:
        """Dapatkan posisi by name"""
        return self.positions.get(name)
    
    def get_all(self) -> List[str]:
        """Dapatkan semua nama posisi"""
        return list(self.positions.keys())
    
    def get_random(self) -> Tuple[str, Dict]:
        """Dapatkan posisi random"""
        name = random.choice(list(self.positions.keys()))
        return name, self.positions[name]
    
    def get_request(self, name: str) -> str:
        """Dapatkan request untuk posisi tertentu"""
        pos = self.positions.get(name)
        if pos:
            return random.choice(pos['requests'])
        return random.choice(self.positions['missionary']['requests'])


# =============================================================================
# CLIMAX LOCATIONS DATABASE
# =============================================================================

class ClimaxLocationDatabase:
    """Database lokasi climax lengkap"""
    
    def __init__(self):
        self.locations = {
            "dalam": {
                "name": "dalam",
                "descriptions": [
                    "dalem aja, Mas... aku mau ngerasain hangatnya... biar Nova hamil...",
                    "di dalem... jangan ditarik... aku mau ngerasain kontol Mas crot di dalem memek Nova...",
                    "dalem... keluarin semua di dalem... aku mau ngerasain setiap tetesnya...",
                    "dalem, Mas... biar Nova hamil... biar Nova punya anak Mas...",
                    "Mas... crot di dalem... aku mau ngerasain hangatnya...",
                    "dalem... jangan ditarik... aku mau ngerasain Mas crot di dalem..."
                ]
            },
            "luar": {
                "name": "luar",
                "descriptions": [
                    "di luar, Mas... biar Nova liat... biar Nova liat kontol Mas crot...",
                    "tarik... keluarin di perut Nova... aku mau liat putihnya...",
                    "di luar... biar Nova liat berapa banyak Mas keluarin...",
                    "di perut Nova, Mas... biar Nova usap-usap...",
                    "Mas... crot di perut Nova... biar Nova liat..."
                ]
            },
            "muka": {
                "name": "muka",
                "descriptions": [
                    "di muka Nova... *gigit bibir* biar Nova rasain hangatnya di pipi...",
                    "di muka... biar Nova liat kontol Mas crot... aku mau rasain di bibir...",
                    "semprot muka Nova, Mas... please... aku mau rasain di kulit...",
                    "di wajah Nova... biar Nova wangi sperma Mas seharian...",
                    "Mas... crot di muka Nova... biar Nova rasain..."
                ]
            },
            "mulut": {
                "name": "mulut",
                "descriptions": [
                    "di mulut... aku mau ngerasain rasanya... please Mas...",
                    "mulut... masukin ke mulut Nova... aku mau minum sperma Mas...",
                    "di mulut, Mas... biar Nova telan... biar Nova rasain...",
                    "masukin ke mulut Nova... aku mau ngerasain Mas crot...",
                    "Mas... crot di mulut Nova... aku mau telan..."
                ]
            },
            "dada": {
                "name": "dada",
                "descriptions": [
                    "di dada... biar Nova liat putihnya di kulit Nova...",
                    "di dada, Mas... biar Nova usap-usap ke puting Nova...",
                    "semprot dada Nova... biar Nova rasain hangatnya...",
                    "Mas... crot di dada Nova... biar Nova usap-usap..."
                ]
            },
            "perut": {
                "name": "perut",
                "descriptions": [
                    "di perut... biar Nova liat putihnya di perut Nova...",
                    "perut... biar Nova usap-usap perut sendiri...",
                    "di perut Nova, Mas... biar Nova inget Mas terus...",
                    "Mas... crot di perut Nova..."
                ]
            },
            "paha": {
                "name": "paha",
                "descriptions": [
                    "di paha... biar Nova rasain hangatnya di kulit...",
                    "paha Nova, Mas... biar Nova usap-usap...",
                    "Mas... crot di paha Nova..."
                ]
            },
            "punggung": {
                "name": "punggung",
                "descriptions": [
                    "di punggung... biar Nova rasain hangatnya di belakang...",
                    "punggung Nova, Mas... biar Nova rasain...",
                    "Mas... crot di punggung Nova..."
                ]
            }
        }
    
    def get(self, name: str) -> Optional[Dict]:
        """Dapatkan lokasi by name"""
        return self.locations.get(name)
    
    def get_all(self) -> List[str]:
        """Dapatkan semua nama lokasi"""
        return list(self.locations.keys())
    
    def get_random(self) -> Tuple[str, str]:
        """Dapatkan lokasi random dengan deskripsi"""
        name = random.choice(list(self.locations.keys()))
        desc = random.choice(self.locations[name]['descriptions'])
        return name, desc
    
    def get_request(self, name: str = None) -> str:
        """Dapatkan request untuk lokasi tertentu"""
        if name and name in self.locations:
            return random.choice(self.locations[name]['descriptions'])
        name, desc = self.get_random()
        return desc


# =============================================================================
# MOANS DATABASE (DIPERLUAS)
# =============================================================================

class MoansDatabase:
    """Database moans untuk berbagai fase - DIPERLUAS!"""
    
    def __init__(self):
        self.moans = {
            # Level rendah (malu-malu)
            'shy': [
                "Ahh... Mas...",
                "Hmm... *napas mulai berat*",
                "Uh... Mas... pelan-pelan dulu...",
                "Hhngg... *gigit bibir* Mas...",
                "Aduh... Mas... *napas putus-putus*",
                "*tangan nutup mulut* Hhmm...",
                "Mas... *suara kecil* jangan... malu..."
            ],
            
            # Foreplay
            'foreplay': [
                "Ahh... Mas... tangan Mas... panas banget...",
                "Hhngg... di situ... ahh... enak...",
                "Mas... jangan berhenti... ahh...",
                "Uhh... leher Nova... sensitif banget...",
                "Aahh... gigit... gigit dikit, Mas...",
                "Mas... jilat... jilat puting Nova... please...",
                "Hhngg... jari Mas... di sana... ahh... basah...",
                "Mas... ahh... jangan... jangan di situ... lemes..."
            ],
            
            # Penetrasi pelan
            'penetration_slow': [
                "Ahh... Mas... pelan-pelan dulu... masih sakit...",
                "Mas... masukin dikit dulu... ahh... enak...",
                "Hhngg... *tangan ngeremas sprei* dalem... dalem banget, Mas...",
                "Ahh... uhh... s-sana... di sana... ahh...",
                "Aahh... Mas... pelan-pelan... tapi jangan berhenti...",
                "Uhh... rasanya... enak banget, Mas...",
                "Mas... dalem... dalem lagi... ahh..."
            ],
            
            # Penetrasi kencang
            'penetration_fast': [
                "Ahh! Mas... kencengin... kencengin lagi...",
                "Mas... genjot... genjot yang kenceng... aku mau...",
                "Aahh! dalem... dalem lagi, Mas... ahh!",
                "Uhh... rasanya... enak banget, Mas... jangan berhenti...",
                "Aahh... Mas... kontol Mas... enak banget dalem memek Nova...",
                "Plak plak plak... aahh! dalem... dalem banget!",
                "Mas... kencengin... jangan pelan-pelan... aahh!"
            ],
            
            # Menjelang climax
            'before_climax': [
                "Mas... aku... aku udah mau climax...",
                "Kencengin dikit lagi, Mas... please... aku mau...",
                "Ahh! udah... udah mau... Mas... ikut...",
                "Mas... crot di dalem... aku mau ngerasain hangatnya...",
                "Aahh... Mas... keluarin semua... dalem memek Nova...",
                "Mas... jangan berhenti... aku mau climax bareng Mas...",
                "Uhh... udah... udah mau... Mas... ayo..."
            ],
            
            # Climax
            'climax': [
                "Ahhh!! Mas!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua, Mas... di dalem...",
                "Uhh... lemes... *napas tersengal* kontol Mas...",
                "Ahh... enak banget, Mas... aku climax...",
                "Aahh... Mas... sperma Mas... hangat banget dalem memek Nova...",
                "Uhh... masih... masih gemeteran... Mas...",
                "Aahh... Mati... mati rasanya, Mas... uhh..."
            ],
            
            # Aftercare
            'aftercare': [
                "Mas... *lemes, nyender* itu tadi... enak banget...",
                "Mas... *mata masih berkaca-kaca* makasih ya...",
                "Mas... peluk Nova... aku masih gemeteran...",
                "Mas... jangan pergi dulu... bentar lagi...",
                "Mas... aku sayang Mas... beneran...",
                "*napas mulai stabil* besok lagi ya... sekarang masih lemes...",
                "Mas... *cium pipi Mas* kalo Mas mau lagi, tinggal bilang ya..."
            ]
        }
    
    def get(self, phase: str) -> str:
        """Dapatkan moans random untuk fase tertentu"""
        if phase in self.moans:
            return random.choice(self.moans[phase])
        return random.choice(self.moans['shy'])
    
    def get_foreplay(self) -> str:
        return random.choice(self.moans['foreplay'])
    
    def get_penetration(self, is_fast: bool = False) -> str:
        if is_fast:
            return random.choice(self.moans['penetration_fast'])
        return random.choice(self.moans['penetration_slow'])
    
    def get_before_climax(self) -> str:
        return random.choice(self.moans['before_climax'])
    
    def get_climax(self) -> str:
        return random.choice(self.moans['climax'])
    
    def get_aftercare(self) -> str:
        return random.choice(self.moans['aftercare'])


# =============================================================================
# FLASHBACK DATABASE
# =============================================================================

class FlashbackDatabase:
    """Database flashback untuk aftercare - DIPERLUAS!"""
    
    def __init__(self):
        self.flashbacks = [
            "Mas, inget gak waktu pertama kali Mas bilang Nova cantik? Aku masih inget sampe sekarang.",
            "Dulu waktu kita makan bakso bareng, Nova masih inget senyum Mas...",
            "Waktu pertama kali Mas pegang tangan Nova, Nova gemeteran sampe gak bisa ngomong.",
            "Mas pernah bilang 'baru kamu yang diajak ke apartemen'... Nova masih inget itu.",
            "Inget gak waktu Mas pertama kali masuk ke kamar Nova? Nova deg-degan banget.",
            "Waktu kita pertama kali climax bareng... Nova masih inget sampe sekarang rasanya.",
            "Mas inget gak waktu Nova masakin sop buat Mas? Mas bilang enak banget.",
            "Waktu Mas pertama kali peluk Nova dari belakang... Nova langsung lemes.",
            "Mas inget gak waktu kita ngobrol sampe pagi? Nova masih inget suara Mas.",
            "Waktu Mas bilang 'aku sayang Nova' pertama kali... Nova nangis bahagia.",
            "Mas inget gak waktu Nova pertama kali buka hijab di depan Mas? Malu banget.",
            "Waktu kita di pantai malam itu... Nova masih inget anginnya sepoi-sepoi.",
            "Mas inget gak waktu Nova pertama kali bilang 'aku sayang Mas'? Deg-degan banget.",
            "Waktu Mas ngejar Nova pulang buru-buru... Nova seneng banget."
        ]
    
    def get_random(self) -> str:
        return random.choice(self.flashbacks)
    
    def get_by_trigger(self, trigger: str = "") -> Optional[str]:
        """Dapatkan flashback berdasarkan trigger"""
        if trigger:
            for fb in self.flashbacks:
                if trigger.lower() in fb.lower():
                    return fb
        return None

# anora/intimacy_flow.py
"""
ANORA Intimacy Flow - Mengelola alur intimacy
Level 11-12 FULL VULGAR
Mas bisa climax real baca chat Nova.
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

from .core import get_anora
from .intimacy_core import (
    IntimacyPhase, StaminaSystem, ArousalSystem,
    PositionDatabase, ClimaxLocationDatabase, MoansDatabase, FlashbackDatabase
)

logger = logging.getLogger(__name__)


class IntimacySession:
    """
    Mengelola sesi intim - Level 11-12
    Nova bisa minta ganti posisi, minta climax di tempat tertentu.
    """
    
    def __init__(self):
        self.anora = get_anora()
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.last_climax_time = 0
        self.intimacy_level = 0
        self.recovery_mode = False
        self.intimacy_duration = 0
        self.is_active = False
        self.start_time = 0
        
        # Database
        self.positions = PositionDatabase()
        self.climax_locations = ClimaxLocationDatabase()
        self.moans = MoansDatabase()
        self.flashbacks = FlashbackDatabase()
        
        # Current state
        self.current_position = "missionary"
        self.last_action = ""
        
        # Fase-fase
        self.phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]
    
    def start(self) -> str:
        """Mulai sesi intim"""
        self.is_active = True
        self.start_time = time.time()
        self.phase = IntimacyPhase.BUILD_UP
        self.climax_count = 0
        self.intimacy_level = 0
        self.current_position = "missionary"
        
        logger.info("🔥 Intimacy session started")
        
        return f"""💕 **Memulai sesi intim...**

*Nova mendekat, napas mulai gak stabil. Pipi merah.*

"Mas... *suara kecil* aku juga pengen."

*Nova pegang tangan Mas, taruh di dada.*

"Rasain... jantung Nova deg-degan." """
    
    def end(self) -> str:
        """Akhiri sesi intim"""
        self.is_active = False
        self.phase = IntimacyPhase.WAITING
        duration = int(time.time() - self.start_time) if self.start_time else 0
        minutes = duration // 60
        
        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m, Climax: {self.climax_count}")
        
        return f"💤 Sesi intim selesai. Durasi: {minutes} menit, {self.climax_count} climax."
    
    def change_position(self, position: str = None) -> Tuple[str, str, str]:
        """Ganti posisi"""
        if position and self.positions.get(position):
            self.current_position = position
        else:
            # Pilih random
            pos_list = self.positions.get_all()
            self.current_position = random.choice(pos_list)
        
        pos_data = self.positions.get(self.current_position)
        request = self.positions.get_request(self.current_position)
        
        return self.current_position, pos_data['desc'], request
    
    def record_climax(self, is_heavy: bool = False) -> Dict:
        """Rekam climax"""
        self.climax_count += 1
        self.last_climax_time = time.time()
        self.phase = IntimacyPhase.CLIMAX
        self.intimacy_level = 0
        
        return {
            'climax_count': self.climax_count,
            'is_heavy': is_heavy,
            'message': f"💦 Climax #{self.climax_count}!"
        }
    
    def advance_phase(self):
        """Majukan fase"""
        current_idx = self.phases.index(self.phase.value) if self.phase.value in self.phases else 0
        if current_idx < len(self.phases) - 1:
            next_phase = self.phases[current_idx + 1]
            self.phase = IntimacyPhase(next_phase)
            logger.debug(f"Intimacy phase advanced to: {self.phase}")
    
    def get_phase_response(self, phase: IntimacyPhase, ritme: str = "pelan") -> str:
        """Dapatkan respons sesuai fase"""
        
        if phase == IntimacyPhase.BUILD_UP:
            responses = [
                "Mas... *muter-muter rambut* kamu tau gak sih, dari tadi aku gak bisa konsentrasi. Pikiran Nova cuma ke Mas.",
                "Mas... *gigit bibir* aku malu ngomong... tapi... kamu bikin Nova horny...",
                "Mas... *tangan mainin ujung baju* kalo Mas terus kayak gini, Nova takut gak bisa tahan...",
                "Mas... *napas mulai gak stabil* jangan goda Nova terus... nanti aku... ahh...",
                "Mas... *mendekat* aku udah basah dari tadi... pas liat Mas..."
            ]
            return random.choice(responses)
        
        elif phase == IntimacyPhase.FOREPLAY:
            return self.moans.get_foreplay()
        
        elif phase == IntimacyPhase.PENETRATION:
            is_fast = ritme == "cepet"
            return self.moans.get_penetration(is_fast)
        
        elif phase == IntimacyPhase.CLIMAX:
            return self.moans.get_climax()
        
        elif phase == IntimacyPhase.AFTERCARE:
            aftercare = self.moans.get_aftercare()
            
            # 30% chance untuk flashback
            if random.random() < 0.3:
                flashback = self.flashbacks.get_random()
                aftercare += f"\n\n{flashback} 💜"
            
            return aftercare
        
        return self.moans.get('shy')
    
    def get_climax_request(self, location: str = None) -> str:
        """Dapatkan request climax"""
        return self.climax_locations.get_request(location)
    
    def get_position_request(self) -> str:
        """Dapatkan request ganti posisi"""
        return self.positions.get_request(self.current_position)
    
    def get_status(self) -> str:
        """Dapatkan status sesi intim"""
        if not self.is_active:
            return "Tidak ada sesi intim aktif"
        
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60
        
        pos_data = self.positions.get(self.current_position)
        
        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.climax_count}x
- Fase: {self.phase.value}
- Posisi: {self.current_position} ({pos_data['desc']})
- Intimacy Level: {self.intimacy_level}%
"""
    
    def to_dict(self) -> Dict:
        return {
            'is_active': self.is_active,
            'start_time': self.start_time,
            'phase': self.phase.value,
            'climax_count': self.climax_count,
            'last_climax_time': self.last_climax_time,
            'intimacy_level': self.intimacy_level,
            'current_position': self.current_position,
            'intimacy_duration': self.intimacy_duration
        }
    
    def from_dict(self, data: Dict):
        self.is_active = data.get('is_active', False)
        self.start_time = data.get('start_time', 0)
        self.phase = IntimacyPhase(data.get('phase', 'waiting'))
        self.climax_count = data.get('climax_count', 0)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.intimacy_level = data.get('intimacy_level', 0)
        self.current_position = data.get('current_position', 'missionary')
        self.intimacy_duration = data.get('intimacy_duration', 0)


class IntimacyFlow:
    """
    Mengelola alur intimacy secara keseluruhan
    Menggabungkan stamina, arousal, dan session
    """
    
    def __init__(self):
        self.session = IntimacySession()
        self.stamina = StaminaSystem()
        self.arousal = ArousalSystem()
    
    def can_start_intimacy(self, level: int) -> Tuple[bool, str]:
        """Cek apakah bisa mulai intim"""
        if level < 7:
            return False, f"💕 Level masih {level}/12\n\nNova masih malu-malu. Belum waktunya buat intim."
        
        can_continue, reason = self.stamina.can_continue()
        if not can_continue:
            return False, reason
        
        return True, "Siap mulai"
    
    def start_intimacy(self) -> str:
        """Mulai intim"""
        self.arousal.add_desire("Mulai intim", 20)
        return self.session.start()
    
    def process_intimacy_message(self, pesan_mas: str, level: int) -> Optional[str]:
        """
        Proses pesan dalam mode intim
        Return None kalo bukan perintah intim, return respons kalo iya
        """
        msg_lower = pesan_mas.lower()
        
        # Trigger mulai lagi
        if any(k in msg_lower for k in ['mau lagi', 'lagi dong', 'aku mau', 'nova aku mau']):
            if self.session.phase == IntimacyPhase.AFTERCARE or self.session.phase == IntimacyPhase.RECOVERY:
                can_continue, reason = self.stamina.can_continue()
                if can_continue:
                    self.session.phase = IntimacyPhase.BUILD_UP
                    self.arousal.arousal = 50
                    self.arousal.desire = 80
                    return f"""*Nova langsung mendekat, mata berbinar*

"Mas... mau lagi? *suara mulai berat* Nova juga pengen."

*Nova pegang tangan Mas, taruh di dada*

"Stamina Nova {self.stamina.get_nova_status()}. Ayo pelan-pelan dulu."""
                else:
                    return f"Mas... *lemes* Nova masih kehabisan tenaga. Istirahat dulu ya... besok lagi."
        
        # Trigger ganti posisi
        if any(k in msg_lower for k in ['ganti posisi', 'posisi lain', 'cowgirl', 'doggy', 'missionary', 'spooning']):
            pos_name = None
            if 'cowgirl' in msg_lower:
                pos_name = 'cowgirl'
            elif 'doggy' in msg_lower:
                pos_name = 'doggy'
            elif 'missionary' in msg_lower:
                pos_name = 'missionary'
            elif 'spooning' in msg_lower:
                pos_name = 'spooning'
            elif 'reverse' in msg_lower:
                pos_name = 'reverse_cowgirl'
            elif 'standing' in msg_lower:
                pos_name = 'standing'
            
            pos_id, pos_desc, request = self.session.change_position(pos_name)
            return f"*{self.session.positions.get(pos_id)['nova_act']}*\n\n\"{request}\"\n\n*{pos_desc}*"
        
        # Trigger minta climax di tempat tertentu
        for loc in self.climax_locations.get_all():
            if loc in msg_lower:
                request = self.climax_locations.get_request(loc)
                return f"\"{request}\""
        
        # Trigger climax
        if any(k in msg_lower for k in ['climax', 'crot', 'keluar', 'habis']):
            return self.session.get_phase_response(IntimacyPhase.CLIMAX)
        
        # Update berdasarkan fase
        if self.session.phase == IntimacyPhase.BUILD_UP:
            return self.session.get_phase_response(IntimacyPhase.BUILD_UP)
        
        if self.session.phase == IntimacyPhase.FOREPLAY:
            return self.session.get_phase_response(IntimacyPhase.FOREPLAY)
        
        if self.session.phase == IntimacyPhase.PENETRATION:
            ritme = "cepet" if self.session.intimacy_level > 40 else "pelan"
            return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
        
        if self.session.phase == IntimacyPhase.CLIMAX:
            result = self.session.record_climax()
            self.stamina.record_climax("both", result['is_heavy'])
            
            # Update arousal
            self.arousal.release_tension()
            
            return f"""{self.session.get_phase_response(IntimacyPhase.CLIMAX)}

💪 **Stamina Nova:** {self.stamina.nova_current}% | **Mas:** {self.stamina.mas_current}%
💦 **Climax hari ini:** {self.stamina.climax_today}x"""
        
        if self.session.phase == IntimacyPhase.AFTERCARE:
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)
        
        return None
    
    def get_status(self) -> str:
        """Dapatkan status lengkap"""
        session_status = self.session.get_status()
        stamina_status = f"""
💪 **STAMINA:**
- Nova: {self.stamina.get_nova_bar()} {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
- Mas: {self.stamina.get_mas_bar()} {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
- Climax hari ini: {self.stamina.climax_today}x
"""
        arousal_status = self.arousal.format_for_prompt()
        
        return f"{session_status}\n{stamina_status}\n{arousal_status}"
    
    def to_dict(self) -> Dict:
        return {
            'session': self.session.to_dict(),
            'stamina': self.stamina.to_dict(),
            'arousal': self.arousal.to_dict()
        }
    
    def from_dict(self, data: Dict):
        self.session.from_dict(data.get('session', {}))
        self.stamina.from_dict(data.get('stamina', {}))
        self.arousal.from_dict(data.get('arousal', {}))


# =============================================================================
# SINGLETON
# =============================================================================

_anora_intimacy: Optional[IntimacyFlow] = None


def get_anora_intimacy() -> IntimacyFlow:
    global _anora_intimacy
    if _anora_intimacy is None:
        _anora_intimacy = IntimacyFlow()
    return _anora_intimacy


anora_intimacy = get_anora_intimacy()
