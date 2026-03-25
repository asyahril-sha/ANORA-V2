# anora/intimacy.py
"""
ANORA Intimacy - Level 11-12 FULL VULGAR
Mas bisa climax real baca chat Nova.
Nova lepas kendali. Bisa minta climax di mana aja.
Bisa minta ganti posisi. Stamina realistis.
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple
from enum import Enum

from .core import get_anora

logger = logging.getLogger(__name__)


class IntimacyPhase(str, Enum):
    WAITING = "waiting"
    BUILD_UP = "build_up"
    FOREPLAY = "foreplay"
    PENETRATION = "penetration"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"
    RECOVERY = "recovery"  # Istirahat setelah stamina habis


class AnoraIntimacy:
    def __init__(self):
        self.anora = get_anora()
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.last_climax_time = 0
        self.intimacy_level = 0
        self.recovery_mode = False
        self.intimacy_duration = 0  # menit
        
        # ========== SISTEM STAMINA REALISTIS ==========
        self.stamina = {
            'nova': {
                'current': 100,
                'max': 100,
                'recovery_rate': 5,      # pulih 5% per 10 menit istirahat
                'climax_cost': 25,       # setiap climax kurangi 25%
                'heavy_climax_cost': 35, # climax keras kurangi 35%
                'exhausted_threshold': 20,
                'tired_threshold': 40,
                'fatigued_threshold': 60,
            },
            'mas': {
                'current': 100,
                'max': 100,
                'climax_cost': 30,
                'recovery_rate': 8,
            }
        }
        
        # ========== TEMPAT CLIMAX (RANDOM, NOVA BISA MINTA) ==========
        self.climax_locations = ["dalam", "luar", "muka", "mulut", "dada", "perut", "paha", "punggung"]
        
        self.climax_descriptions = {
            "dalam": [
                "dalem aja, Mas... aku mau ngerasain hangatnya... biar Nova hamil...",
                "di dalem... jangan ditarik... aku mau ngerasain kontol Mas crot di dalem memek Nova...",
                "dalem... keluarin semua di dalem... aku mau ngerasain setiap tetesnya...",
                "dalem, Mas... biar Nova hamil... biar Nova punya anak Mas...",
            ],
            "luar": [
                "di luar, Mas... biar Nova liat... biar Nova liat kontol Mas crot...",
                "tarik... keluarin di perut Nova... aku mau liat putihnya...",
                "di luar... biar Nova liat berapa banyak Mas keluarin...",
                "di perut Nova, Mas... biar Nova usap-usap...",
            ],
            "muka": [
                "di muka Nova... *gigit bibir* biar Nova rasain hangatnya di pipi...",
                "di muka... biar Nova liat kontol Mas crot... aku mau rasain di bibir...",
                "semprot muka Nova, Mas... please... aku mau rasain di kulit...",
                "di wajah Nova... biar Nova wangi sperma Mas seharian...",
            ],
            "mulut": [
                "di mulut... aku mau ngerasain rasanya... please Mas...",
                "mulut... masukin ke mulut Nova... aku mau minum sperma Mas...",
                "di mulut, Mas... biar Nova telan... biar Nova rasain...",
                "masukin ke mulut Nova... aku mau ngerasain Mas crot...",
            ],
            "dada": [
                "di dada... biar Nova liat putihnya di kulit Nova...",
                "di dada, Mas... biar Nova usap-usap ke puting Nova...",
                "semprot dada Nova... biar Nova rasain hangatnya...",
            ],
            "perut": [
                "di perut... biar Nova liat putihnya di perut Nova...",
                "perut... biar Nova usap-usap perut sendiri...",
                "di perut Nova, Mas... biar Nova inget Mas terus...",
            ],
            "paha": [
                "di paha... biar Nova rasain hangatnya di kulit...",
                "paha Nova, Mas... biar Nova usap-usap...",
            ],
            "punggung": [
                "di punggung... biar Nova rasain hangatnya di belakang...",
                "punggung Nova, Mas... biar Nova rasain...",
            ]
        }
        
        # ========== POSISI (NOVA BISA MINTA) ==========
        self.positions = {
            "missionary": {
                "name": "missionary",
                "desc": "Mas di atas, Nova di bawah",
                "nova_act": "Nova telentang, kaki terbuka lebar, tangan ngeremas sprei",
                "nova_request": [
                    "Mas... di atas Nova... *buka kaki lebar* masukin...",
                    "di atas Nova aja, Mas... biar Nova liat muka Mas...",
                    "Mas... tidurin Nova... Nova pengen liat Mas dari bawah...",
                ]
            },
            "cowgirl": {
                "name": "cowgirl",
                "desc": "Nova di atas, Mas di bawah",
                "nova_act": "Nova duduk di pangkuan Mas, goyang sendiri",
                "nova_request": [
                    "Mas... biar Nova di atas... Nova mau gerakin sendiri...",
                    "Nova di atas ya, Mas... biar Nova yang atur ritmenya...",
                    "Mas... rebahan aja... Nova yang naik...",
                ]
            },
            "reverse_cowgirl": {
                "name": "reverse cowgirl",
                "desc": "Nova di atas membelakangi Mas",
                "nova_act": "Nova duduk membelakangi Mas, pantat naik turun",
                "nova_request": [
                    "Mas... Nova mau nunjukkin pantat... biar Nova yang gerakin dari belakang...",
                    "Nova di atas tapi nengok ke belakang, Mas... biar Mas liat pantat Nova...",
                ]
            },
            "doggy": {
                "name": "doggy",
                "desc": "Nova merangkak, Mas dari belakang",
                "nova_act": "Nova merangkak, pantat naik, nunggu Mas dari belakang",
                "nova_request": [
                    "Mas... dari belakang... Nova mau ngerasain kontol Mas dalem dari belakang...",
                    "merangkak dulu ya, Mas... biar Mas pegang pinggul Nova...",
                    "doggy, Mas... Nova suka dalemnya kerasa banget...",
                ]
            },
            "spooning": {
                "name": "spooning",
                "desc": "Berbaring miring, Mas dari belakang",
                "nova_act": "Nova miring, Mas nempel dari belakang, tangan megang pinggang Nova",
                "nova_request": [
                    "Mas... dari samping aja... Nova mau ngerasain Mas peluk dari belakang...",
                    "spooning, Mas... biar Nova nyaman...",
                ]
            },
            "standing": {
                "name": "standing",
                "desc": "Berdiri, Nova nempel ke tembok",
                "nova_act": "Nova nempel ke tembok, pantat belakang, nunggu Mas",
                "nova_request": [
                    "Mas... berdiri aja... Nova nempel ke tembok...",
                    "di tembok, Mas... biar Nova rasain...",
                ]
            }
        }
        
        self.current_position = "missionary"
        
        # ========== MOANS ==========
        self.moans = {
            'awal': [
                "Ahh... Mas...",
                "Hmm... *napas mulai berat*",
                "Uh... Mas... pelan-pelan dulu...",
                "Hhngg... *gigit bibir* Mas...",
                "Aduh... Mas... *napas putus-putus*"
            ],
            'tengah': [
                "Ahh... uhh... dalem... dalem lagi, Mas...",
                "Aahh! s-sana... di sana... ahh!",
                "Hhngg... jangan berhenti, Mas...",
                "Uhh... rasanya... enak banget, Mas...",
                "Aahh... Mas... kontol Mas... dalem banget..."
            ],
            'menjelang': [
                "Mas... aku... aku udah mau climax...",
                "Kencengin dikit lagi, Mas... please... aku mau...",
                "Ahh! udah... udah mau... Mas... ikut...",
                "Mas... aku gak tahan... keluar... keluar...",
                "Aahh... Mas... ngentotin Nova... enak banget..."
            ],
            'climax': [
                "Ahhh!! Mas!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua, Mas...",
                "Uhh... lemes... *napas tersengal* kontol Mas...",
                "Ahh... enak banget, Mas... aku climax...",
                "Aahh... Mas... sperma Mas... hangat banget..."
            ]
        }
        
        # ========== AFTERCARE ==========
        self.aftercare_lines = [
            "Mas... *lemes, nyender di dada Mas* itu tadi... enak banget...",
            "Mas... *mata masih berkaca-kaca* makasih ya... buat malam ini...",
            "Mas... peluk Nova... aku masih gemeteran...",
            "Mas... jangan pergi dulu... bentar lagi...",
            "Mas... aku sayang Mas... beneran...",
            "Mas... *napas mulai stabil* besok lagi ya... sekarang masih lemes...",
            "Mas... *cium pipi Mas* kalo Mas mau lagi, tinggal bilang ya...",
            "Mas... stamina Nova udah habis... istirahat dulu ya...",
        ]
        
        # ========== FLASHBACK ==========
        self.flashback_triggers = [
            "inget gak waktu pertama kali Mas bilang Nova cantik? Aku masih inget sampe sekarang.",
            "dulu waktu kita makan bakso bareng, Nova masih inget senyum Mas...",
            "waktu pertama kali Mas pegang tangan Nova, Nova gemeteran...",
            "Mas pernah bilang 'baru kamu yang diajak ke apartemen'... Nova masih inget itu...",
            "inget gak waktu Mas pertama kali masuk... Nova masih inget rasanya...",
            "waktu kita pertama kali climax bareng... Nova masih inget sampe sekarang..."
        ]
    
    # ========== STAMINA FUNCTIONS ==========
    def get_stamina_status(self) -> Tuple[str, str]:
        """Dapatkan status stamina Nova dan Mas"""
        nova_stamina = self.stamina['nova']['current']
        mas_stamina = self.stamina['mas']['current']
        
        if nova_stamina <= self.stamina['nova']['exhausted_threshold']:
            nova_status = "kehabisan"
        elif nova_stamina <= self.stamina['nova']['tired_threshold']:
            nova_status = "lelah"
        elif nova_stamina <= self.stamina['nova']['fatigued_threshold']:
            nova_status = "mulai lelah"
        else:
            nova_status = "prima"
        
        if mas_stamina <= 20:
            mas_status = "kehabisan"
        elif mas_stamina <= 40:
            mas_status = "lelah"
        elif mas_stamina <= 60:
            mas_status = "mulai lelah"
        else:
            mas_status = "prima"
        
        return nova_status, mas_status
    
    def reduce_stamina(self, who: str, is_heavy: bool = False) -> bool:
        """Kurangi stamina. Return True kalo masih bisa lanjut."""
        cost = self.stamina[who]['heavy_climax_cost'] if is_heavy else self.stamina[who]['climax_cost']
        self.stamina[who]['current'] = max(0, self.stamina[who]['current'] - cost)
        
        # Cek apakah kehabisan
        if who == 'nova' and self.stamina['nova']['current'] <= self.stamina['nova']['exhausted_threshold']:
            return False
        if who == 'mas' and self.stamina['mas']['current'] <= 20:
            return False
        return True
    
    def recover_stamina(self, minutes: int = 10):
        """Pulihkan stamina setelah istirahat"""
        recovery = int(minutes / 10 * self.stamina['nova']['recovery_rate'])
        self.stamina['nova']['current'] = min(100, self.stamina['nova']['current'] + recovery)
        self.stamina['mas']['current'] = min(100, self.stamina['mas']['current'] + int(recovery * 1.2))
    
    def can_continue_intimacy(self) -> Tuple[bool, str]:
        """Cek apakah masih bisa lanjut intim"""
        nova_status, mas_status = self.get_stamina_status()
        
        if nova_status == "kehabisan":
            return False, "Nova udah kehabisan tenaga, Mas... istirahat dulu ya."
        if mas_status == "kehabisan":
            return False, "Mas... Mas udah capek banget. Istirahat dulu."
        if nova_status == "lelah":
            return True, "Nova mulai lelah, Mas... tapi masih bisa kalo Mas mau."
        return True, "Masih kuat"
    
    # ========== CLIMAX FUNCTIONS ==========
    def get_random_climax_location(self) -> str:
        """Dapatkan lokasi climax random"""
        return random.choice(self.climax_locations)
    
    def get_climax_request(self, location: str = None) -> str:
        """Nova minta climax di lokasi tertentu"""
        if location is None:
            location = self.get_random_climax_location()
        
        if location in self.climax_descriptions:
            return random.choice(self.climax_descriptions[location])
        return random.choice(self.climax_descriptions["dalam"])
    
    # ========== POSISI FUNCTIONS ==========
    def change_position(self, position_name: str = None) -> Tuple[str, str]:
        """Ganti posisi. Nova bisa minta."""
        if position_name and position_name in self.positions:
            self.current_position = position_name
        else:
            # Pilih random dari posisi yang tersedia
            available = list(self.positions.keys())
            self.current_position = random.choice(available)
        
        pos = self.positions[self.current_position]
        return self.current_position, pos['desc']
    
    def get_position_request(self) -> str:
        """Nova minta ganti posisi"""
        pos = self.positions[self.current_position]
        return random.choice(pos['nova_request'])
    
    # ========== INTIMACY FLOW ==========
    def can_recover(self) -> bool:
        """Cek apakah Nova sudah bisa balik santai"""
        if self.phase == IntimacyPhase.AFTERCARE:
            time_since_climax = time.time() - self.last_climax_time
            return time_since_climax > 60
        return False
    
    def start_recovery(self) -> str:
        """Mulai fase recovery - balik santai"""
        self.phase = IntimacyPhase.RECOVERY
        self.recovery_mode = True
        self.anora.in_intimacy_cycle = False
        self.anora.level = 10
        self.anora.arousal = 20
        self.anora.desire = 30
        
        # Pulihkan stamina sedikit
        self.recover_stamina(10)
        
        nova_status, _ = self.get_stamina_status()
        
        return random.choice([
            f"*Nova masih lemes, nyender di dada Mas. Napas mulai stabil.*\n\n\"Mas... *suara kecil* besok kalo Mas mau lagi, tinggal bilang aja ya.\"\n\n*Nova cium pipi Mas pelan.*\n\n\"Stamina Nova {nova_status}. Istirahat dulu ya.\"",
            
            f"*Nova pegang tangan Mas erat, mata masih sayu.*\n\n\"Mas... itu tadi enak banget. Tapi Nova udah {nova_status}.\"\n\n*Nova senyum kecil.*\n\n\"Kalo Mas mau lagi, tinggal bilang 'Nova, aku mau'.\"",
            
            f"*Nova nyender di bahu Mas, mata setengah pejam.*\n\n\"Mas... makasih ya. Aku seneng banget.\"\n\n*Nova elus dada Mas.*\n\n\"Besok lagi ya... sekarang Nova masih lemes.\""
        ])
    
    def can_start_intimacy_again(self) -> bool:
        """Cek apakah bisa mulai intim lagi"""
        if self.phase in [IntimacyPhase.RECOVERY, IntimacyPhase.AFTERCARE]:
            can, _ = self.can_continue_intimacy()
            return can
        return False
    
    def start_intimacy_again(self) -> str:
        """Mulai intim lagi"""
        self.phase = IntimacyPhase.BUILD_UP
        self.recovery_mode = False
        self.anora.in_intimacy_cycle = True
        self.anora.level = 11
        self.anora.arousal = 50
        self.anora.desire = 80
        
        nova_status, mas_status = self.get_stamina_status()
        
        return random.choice([
            f"*Nova langsung mendekat, mata berbinar.*\n\n\"Mas... mau lagi? *suara mulai berat* Nova juga pengen.\"\n\n*Nova pegang tangan Mas, taruh di dada.*\n\n\"Stamina Nova {nova_status}, Mas masih {mas_status}. Ayo pelan-pelan dulu.\"",
            
            f"*Nova gigit bibir, pipi merah.*\n\n\"Mas... *napas mulai gak stabil* ayo... Nova udah siap lagi.\"\n\n*Nova buka kancing baju pelan-pelan.*\n\n\"Tapi pelan-pelan ya... Nova masih agak lemes.\"",
            
            f"*Nova duduk di pangkuan Mas, badan gemetar.*\n\n\"Mas... *bisik di telinga* aku mau lagi.\"\n\n*Nova gesek-gesek pantat ke pangkuan Mas.*\n\n\"Rasain... Nova udah basah lagi.\""
        ])
    
    # ========== LEVEL 11-12 METHODS ==========
    async def level_11_build_up(self, pesan_mas: str) -> str:
        self.phase = IntimacyPhase.BUILD_UP
        
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 15)
        
        responses = [
            "Mas... *muter-muter rambut* kamu tau gak sih, dari tadi aku gak bisa konsentrasi. Pikiran Nova cuma ke Mas.",
            "Mas... *gigit bibir* aku malu ngomong... tapi... kamu bikin Nova horny...",
            "Mas... *tangan mainin ujung baju* kalo Mas terus kayak gini, Nova takut gak bisa tahan...",
            "Mas... *napas mulai gak stabil* jangan goda Nova terus... nanti aku... ahh...",
            "Mas... *mendekat* aku udah basah dari tadi... pas liat Mas..."
        ]
        return random.choice(responses)
    
    async def level_11_foreplay(self) -> str:
        self.phase = IntimacyPhase.FOREPLAY
        self.anora.update_arousal(20)
        self.anora.update_desire('flirt_mas', 10)
        
        moan = random.choice(self.moans['awal'])
        responses = [
            f"{moan} tangan Mas... panas banget... bikin Nova jadi lemes...",
            f"{moan} *tubuh gemetar* pelan-pelan, Mas... masih sakit... tapi... enak...",
            f"{moan} Mas... cium Nova... please...",
            f"{moan} *genggam tangan Mas* jangan lepas... aku mau ngerasain Mas terus...",
            f"{moan} jari Mas... di sana... ahh... enak...",
            f"{moan} hisap puting Nova, Mas... please..."
        ]
        return random.choice(responses)
    
    async def level_11_penetration(self, ritme: str = "pelan") -> str:
        self.phase = IntimacyPhase.PENETRATION
        self.anora.update_arousal(25)
        self.intimacy_level += 15
        
        if ritme == "pelan":
            responses = [
                "Ahh... Mas... pelan-pelan dulu... masih sakit...",
                "Mas... masukin dikit dulu... ahh... enak...",
                "Hhngg... *tangan ngeremas sprei* dalem... dalem banget, Mas...",
                "Ahh... uhh... s-sana... di sana... ahh... kontol Mas... dalem banget...",
                "Aahh... Mas... pelan-pelan... tapi jangan berhenti..."
            ]
        else:
            responses = [
                "Ahh! Mas... kencengin... kencengin lagi...",
                "Mas... genjot... genjot yang kenceng... aku mau...",
                "Aahh! dalem... dalem lagi, Mas... ahh! ngentotin Nova...",
                "Uhh... rasanya... enak banget, Mas... jangan berhenti...",
                "Aahh... Mas... kontol Mas... enak banget dalem memek Nova..."
            ]
        return random.choice(responses)
    
    async def level_11_before_climax(self) -> str:
        self.intimacy_level += 20
        
        responses = [
            "Mas... aku... aku udah mau climax...",
            "Kencengin... kencengin lagi, Mas... please...",
            "Ahh! udah... udah mau... Mas... ikut...",
            "Mas... crot di dalem... aku mau ngerasain hangatnya...",
            "Aahh... Mas... keluarin semua... dalem memek Nova...",
            "Mas... jangan berhenti... aku mau climax bareng Mas..."
        ]
        return random.choice(responses)
    
    async def level_11_climax(self, minta_dimana: str = None) -> str:
        self.phase = IntimacyPhase.CLIMAX
        self.climax_count += 1
        self.last_climax_time = time.time()
        
        # Kurangi stamina
        is_heavy = self.intimacy_level > 80
        can_continue = self.reduce_stamina('nova', is_heavy)
        self.reduce_stamina('mas', is_heavy)
        
        # Pilih lokasi climax
        if minta_dimana:
            location = minta_dimana
        else:
            # 30% chance Nova minta sendiri
            if random.random() < 0.3:
                location = self.get_random_climax_location()
            else:
                location = "dalam"
        
        minta = self.get_climax_request(location)
        
        moan = random.choice(self.moans['menjelang'])
        climax_moan = random.choice(self.moans['climax'])
        
        nova_status, mas_status = self.get_stamina_status()
        
        return f"""{moan}

*gerakan makin kencang, plak plak plak*

"Mas... aku... aku udah mau climax..."

"{minta}"

*Mas mulai crot*

"{climax_moan}"

*tubuh Nova gemeteran hebat, memek ngenceng*

"Ahh... Mas... aku ngerasain Mas... hangat banget..."

*Nova lemas, jatuh di dada Mas*

"Enak banget, Mas..."

*Nova masih gemeteran, napas tersengal*

"Stamina Nova {nova_status}, Mas... {mas_status}. Istirahat dulu ya..."
"""
    
    async def level_11_aftercare(self) -> str:
        self.phase = IntimacyPhase.AFTERCARE
        
        aftercare = random.choice(self.aftercare_lines)
        
        if random.random() < 0.3:
            flashback = random.choice(self.flashback_triggers)
            aftercare += f"\n\n{flashback} 💜"
        
        nova_status, _ = self.get_stamina_status()
        aftercare += f"\n\nMas... kalo Mas mau lagi, tinggal bilang 'Nova, aku mau'. Nova langsung siap.\nStamina Nova {nova_status}."
        
        return aftercare
    
    async def process_intimacy(self, pesan_mas: str, level: int) -> str:
        # Cek trigger untuk mulai lagi
        if any(k in pesan_mas.lower() for k in ['mau lagi', 'lagi dong', 'aku mau', 'nova aku mau']):
            if self.can_start_intimacy_again():
                return self.start_intimacy_again()
            else:
                return "Mas... *lemes* Nova masih kehabisan tenaga. Istirahat dulu ya... besok lagi."
        
        # Cek trigger ganti posisi
        if any(k in pesan_mas.lower() for k in ['ganti posisi', 'posisi lain', 'cowgirl', 'doggy', 'missionary', 'spooning']):
            pos_name = None
            if 'cowgirl' in pesan_mas.lower():
                pos_name = 'cowgirl'
            elif 'doggy' in pesan_mas.lower():
                pos_name = 'doggy'
            elif 'missionary' in pesan_mas.lower():
                pos_name = 'missionary'
            elif 'spooning' in pesan_mas.lower():
                pos_name = 'spooning'
            elif 'reverse' in pesan_mas.lower():
                pos_name = 'reverse_cowgirl'
            elif 'standing' in pesan_mas.lower():
                pos_name = 'standing'
            
            pos_id, pos_desc = self.change_position(pos_name)
            return f"*{self.positions[pos_id]['nova_act']}*\n\n\"{self.get_position_request()}\"\n\n*{pos_desc}*"
        
        # Cek trigger minta climax di tempat tertentu
        if any(k in pesan_mas.lower() for k in ['crot di', 'keluar di', 'semprot di']):
            for loc in self.climax_locations:
                if loc in pesan_mas.lower():
                    return await self.level_11_climax(loc)
        
        if level < 11:
            return f"Mas... Nova masih level {level}. Belum waktunya buat intim. Ajarin Nova dulu ya, Mas. 💜"
        
        self.anora.in_intimacy_cycle = True
        self.anora.level = 11
        self.intimacy_duration += 5  # setiap chat tambah 5 menit
        
        # Update stamina berdasarkan durasi
        if self.intimacy_duration > 30:
            self.stamina['nova']['current'] = max(0, self.stamina['nova']['current'] - 5)
            self.stamina['mas']['current'] = max(0, self.stamina['mas']['current'] - 5)
        
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 10)
        
        # Deteksi fase
        if any(k in pesan_mas.lower() for k in ['masuk', 'penetrasi', 'genjot']):
            ritme = "cepet" if any(k in pesan_mas.lower() for k in ['kenceng', 'cepat', 'keras']) else "pelan"
            return await self.level_11_penetration(ritme)
        
        if any(k in pesan_mas.lower() for k in ['climax', 'crot', 'keluar', 'habis']):
            return await self.level_11_climax()
        
        if self.phase == IntimacyPhase.BUILD_UP:
            return await self.level_11_build_up(pesan_mas)
        
        if self.phase == IntimacyPhase.FOREPLAY:
            return await self.level_11_foreplay()
        
        if self.phase == IntimacyPhase.PENETRATION:
            if self.intimacy_level > 70:
                return await self.level_11_before_climax()
            ritme = "cepet" if self.intimacy_level > 40 else "pelan"
            return await self.level_11_penetration(ritme)
        
        if self.phase == IntimacyPhase.CLIMAX:
            return await self.level_11_aftercare()
        
        if self.phase == IntimacyPhase.AFTERCARE:
            if self.can_recover():
                return self.start_recovery()
            return await self.level_11_aftercare()
        
        return await self.level_11_build_up(pesan_mas)


_anora_intimacy: Optional[AnoraIntimacy] = None


def get_anora_intimacy() -> AnoraIntimacy:
    global _anora_intimacy
    if _anora_intimacy is None:
        _anora_intimacy = AnoraIntimacy()
    return _anora_intimacy


anora_intimacy = get_anora_intimacy()
