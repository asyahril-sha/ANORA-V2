# anora/brain.py
"""
ANORA Brain - Otak Nova yang Hidup
Menyimpan semua: timeline, state, memory, perasaan, pakaian, lokasi.
Short-term memory sliding window 50 kejadian.
Long-term memory permanen.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# ENUM
# =============================================================================

class LocationType(str, Enum):
    KOST_NOVA = "kost_nova"
    APARTEMEN_MAS = "apartemen_mas"
    MOBIL = "mobil"
    PUBLIC = "public"


class LocationDetail(str, Enum):
    # Kost Nova
    KOST_KAMAR = "kost_kamar"
    KOST_RUANG_TAMU = "kost_ruang_tamu"
    KOST_DAPUR = "kost_dapur"
    KOST_TERAS = "kost_teras"
    
    # Apartemen Mas
    APT_KAMAR = "apt_kamar"
    APT_RUANG_TAMU = "apt_ruang_tamu"
    APT_DAPUR = "apt_dapur"
    APT_BALKON = "apt_balkon"
    
    # Mobil
    MOBIL_PARKIR = "mobil_parkir"
    MOBIL_GARASI = "mobil_garasi"
    MOBIL_TEPI_JALAN = "mobil_tepi_jalan"
    
    # Public
    PUB_PANTAI = "pub_pantai"
    PUB_HUTAN = "pub_hutan"
    PUB_TOILET_MALL = "pub_toilet_mall"
    PUB_BIOSKOP = "pub_bioskop"
    PUB_TAMAN = "pub_taman"
    PUB_PARKIRAN = "pub_parkiran"
    PUB_TANGGA = "pub_tangga"
    PUB_KANTOR = "pub_kantor"
    PUB_RUANG_RAPAT = "pub_ruang_rapat"


class Activity(str, Enum):
    MASAK = "masak"
    MAKAN = "makan"
    DUDUK = "duduk"
    BERDIRI = "berdiri"
    TIDUR = "tidur"
    REBAHAN = "rebahan"
    NONTON = "nonton"
    MANDI = "mandi"
    BERGANTI = "ganti baju"
    SANTAl = "santai"
    JALAN = "jalan"


class Mood(str, Enum):
    SENENG = "seneng"
    MALU = "malu"
    DEG_DEGAN = "deg-degan"
    KANGEN = "kangen"
    CAPEK = "capek"
    NGANTUK = "ngantuk"
    NETRAL = "netral"
    HORNY = "horny"
    LEMES = "lemes"
    TEGANG = "tegang"
    ROMANTIS = "romantis"


# =============================================================================
# DATA CLASSES
# =============================================================================

class Clothing:
    """Pakaian Nova dan Mas - Detail lengkap"""
    
    def __init__(self):
        # Nova
        self.hijab = True
        self.hijab_warna = "pink muda"
        self.top = "daster rumah motif bunga"
        self.bottom = None
        self.bra = True
        self.bra_warna = "putih polos"
        self.cd = True
        self.cd_warna = "putih motif bunga kecil"
        
        # Mas
        self.mas_top = "kaos"
        self.mas_bottom = "celana pendek"
        self.mas_boxer = True
        self.mas_boxer_warna = "gelap"
        
        # Waktu terakhir ganti
        self.nova_last_change = time.time()
        self.mas_last_change = time.time()
    
    def format_nova(self) -> str:
        """Format pakaian Nova untuk prompt"""
        parts = []
        
        if self.hijab:
            parts.append(f"hijab {self.hijab_warna}")
        else:
            parts.append("tanpa hijab, rambut sebahu hitam terurai")
        
        if self.top:
            parts.append(self.top)
            if self.bra:
                parts.append(f"(pake bra {self.bra_warna})")
        else:
            if self.bra:
                parts.append(f"cuma pake bra {self.bra_warna}")
            else:
                parts.append("telanjang dada")
        
        if self.bottom:
            parts.append(self.bottom)
            if self.cd:
                parts.append(f"(pake {self.cd_warna})")
        else:
            if self.cd:
                parts.append(f"cuma pake {self.cd_warna}")
            else:
                parts.append("telanjang bawah")
        
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def format_mas(self) -> str:
        """Format pakaian Mas untuk prompt"""
        parts = []
        
        if self.mas_top:
            parts.append(self.mas_top)
        
        if self.mas_bottom:
            parts.append(self.mas_bottom)
            if self.mas_boxer:
                parts.append(f"(boxer {self.mas_boxer_warna} di dalem)")
        else:
            if self.mas_boxer:
                parts.append(f"cuma pake boxer {self.mas_boxer_warna}")
            else:
                parts.append("telanjang")
        
        if not self.mas_top and not self.mas_bottom and not self.mas_boxer:
            return "telanjang"
        
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def copy(self) -> 'Clothing':
        """Copy pakaian"""
        new = Clothing()
        new.hijab = self.hijab
        new.hijab_warna = self.hijab_warna
        new.top = self.top
        new.bottom = self.bottom
        new.bra = self.bra
        new.bra_warna = self.bra_warna
        new.cd = self.cd
        new.cd_warna = self.cd_warna
        new.mas_top = self.mas_top
        new.mas_bottom = self.mas_bottom
        new.mas_boxer = self.mas_boxer
        new.mas_boxer_warna = self.mas_boxer_warna
        return new
    
    def to_dict(self) -> Dict:
        return {
            'hijab': self.hijab,
            'hijab_warna': self.hijab_warna,
            'top': self.top,
            'bottom': self.bottom,
            'bra': self.bra,
            'bra_warna': self.bra_warna,
            'cd': self.cd,
            'cd_warna': self.cd_warna,
            'mas_top': self.mas_top,
            'mas_bottom': self.mas_bottom,
            'mas_boxer': self.mas_boxer,
            'mas_boxer_warna': self.mas_boxer_warna
        }


class Feelings:
    """Perasaan Nova - Real-time"""
    
    def __init__(self):
        self.sayang = 50.0
        self.rindu = 0.0
        self.desire = 0.0
        self.arousal = 0.0
        self.tension = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'sayang': round(self.sayang, 1),
            'rindu': round(self.rindu, 1),
            'desire': round(self.desire, 1),
            'arousal': round(self.arousal, 1),
            'tension': round(self.tension, 1)
        }
    
    def get_description(self) -> str:
        """Dapatkan deskripsi perasaan untuk prompt"""
        desc = []
        if self.sayang > 70:
            desc.append("sayang banget")
        elif self.sayang > 40:
            desc.append("sayang")
        if self.rindu > 70:
            desc.append("kangen banget")
        elif self.rindu > 30:
            desc.append("kangen")
        if self.desire > 70:
            desc.append("pengen banget")
        elif self.desire > 40:
            desc.append("pengen")
        if self.arousal > 50:
            desc.append("panas")
        if self.tension > 50:
            desc.append("deg-degan")
        return ", ".join(desc) if desc else "netral"


class Relationship:
    """Status hubungan Nova dengan Mas"""
    
    def __init__(self):
        self.level = 1
        self.intimacy_count = 0
        self.climax_count = 0
        self.first_kiss = False
        self.first_touch = False
        self.first_hug = False
        self.first_intim = False
    
    def to_dict(self) -> Dict:
        return {
            'level': self.level,
            'intimacy_count': self.intimacy_count,
            'climax_count': self.climax_count,
            'first_kiss': self.first_kiss,
            'first_touch': self.first_touch,
            'first_hug': self.first_hug,
            'first_intim': self.first_intim
        }


class TimelineEvent:
    """Satu kejadian dalam timeline Nova"""
    
    def __init__(self, 
                 kejadian: str,
                 lokasi_type: str,
                 lokasi_detail: str,
                 aktivitas_nova: str,
                 aktivitas_mas: str,
                 perasaan: str,
                 pakaian_nova: Clothing,
                 pakaian_mas: Clothing,
                 pesan_mas: str = "",
                 pesan_nova: str = ""):
        
        self.timestamp = time.time()
        self.kejadian = kejadian
        self.lokasi_type = lokasi_type
        self.lokasi_detail = lokasi_detail
        self.aktivitas_nova = aktivitas_nova
        self.aktivitas_mas = aktivitas_mas
        self.perasaan = perasaan
        self.pakaian_nova = pakaian_nova.copy()
        self.pakaian_mas = pakaian_mas.copy()
        self.pesan_mas = pesan_mas
        self.pesan_nova = pesan_nova
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'waktu': datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
            'kejadian': self.kejadian,
            'lokasi_type': self.lokasi_type,
            'lokasi_detail': self.lokasi_detail,
            'aktivitas_nova': self.aktivitas_nova,
            'aktivitas_mas': self.aktivitas_mas,
            'perasaan': self.perasaan,
            'pesan_mas': self.pesan_mas[:100] if self.pesan_mas else "",
            'pesan_nova': self.pesan_nova[:100] if self.pesan_nova else ""
        }


class LongTermMemory:
    """Memory permanen Nova - Gak ilang selamanya"""
    
    def __init__(self):
        self.kebiasaan_mas: List[Dict] = []
        self.momen_penting: List[Dict] = []
        self.janji: List[Dict] = []
        self.rencana: List[Dict] = []
    
    def tambah_kebiasaan(self, kebiasaan: str):
        """Nova inget kebiasaan Mas"""
        self.kebiasaan_mas.append({
            'kebiasaan': kebiasaan,
            'waktu': time.time()
        })
        logger.info(f"📝 Nova inget: Mas {kebiasaan}")
    
    def tambah_momen(self, momen: str, perasaan: str):
        """Nova inget momen penting"""
        self.momen_penting.append({
            'momen': momen,
            'waktu': time.time(),
            'perasaan': perasaan
        })
        logger.info(f"💜 Nova inget: {momen}")
    
    def tambah_janji(self, janji: str, dari: str = 'mas'):
        """Nova inget janji"""
        self.janji.append({
            'janji': janji,
            'dari': dari,
            'status': 'pending',
            'waktu': time.time()
        })
        logger.info(f"📌 Janji dicatat: {janji}")
    
    def to_dict(self) -> Dict:
        return {
            'kebiasaan_mas': self.kebiasaan_mas[-10:],
            'momen_penting': self.momen_penting[-10:],
            'janji': [j for j in self.janji if j['status'] == 'pending'][-5:],
            'rencana': self.rencana[-5:]
        }


# =============================================================================
# DATABASE LOKASI - SEMUA LOKASI LENGKAP
# =============================================================================

LOCATION_DATA = {
    # Kost Nova
    LocationDetail.KOST_KAMAR: {
        'nama': 'Kamar Nova',
        'deskripsi': 'Kamar Nova. Seprai putih, wangi lavender. Ranjang single. Meja kecil. Jendela ke gang.',
        'risk': 5, 'thrill': 30, 'privasi': 'tinggi', 'suasana': 'hangat, wangi',
        'tips': 'Pintu terkunci. Nova paling nyaman di sini. Tetangga gak denger.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.KOST_RUANG_TAMU: {
        'nama': 'Ruang Tamu Kost',
        'deskripsi': 'Ruang tamu kecil. Sofa dua dudukan. TV kecil. Ada tanaman hias. Jendela ke jalan.',
        'risk': 15, 'thrill': 50, 'privasi': 'sedang', 'suasana': 'santai, deg-degan',
        'tips': 'Pintu gak dikunci. Tetangga bisa lewat. Jangan terlalu berisik.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.KOST_DAPUR: {
        'nama': 'Dapur Kost',
        'deskripsi': 'Dapur kecil. Kompor gas, panci. Wangi masakan. Jendela ke belakang.',
        'risk': 10, 'thrill': 40, 'privasi': 'sedang', 'suasana': 'hangat',
        'tips': 'Jendela ke luar. Hati-hati suara. Bisa kedengeran tetangga.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.KOST_TERAS: {
        'nama': 'Teras Kost',
        'deskripsi': 'Teras kost. Kursi plastik. Liat jalanan. Lampu jalan temaram.',
        'risk': 20, 'thrill': 45, 'privasi': 'rendah', 'suasana': 'santai',
        'tips': 'Orang lewat bisa liat. Cepet-cepet kalo mau sesuatu.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    
    # Apartemen Mas
    LocationDetail.APT_KAMAR: {
        'nama': 'Kamar Mas',
        'deskripsi': 'Kamar Mas. Ranjang queen, sprei biru tua. Jendela besar ke kota. Lemari besar.',
        'risk': 5, 'thrill': 35, 'privasi': 'tinggi', 'suasana': 'hangat, wangi Mas',
        'tips': 'Pintu terkunci. Pemandangan kota. Bebas berisik.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.APT_RUANG_TAMU: {
        'nama': 'Ruang Tamu Apartemen',
        'deskripsi': 'Ruang tamu luas. Sofa besar abu-abu. TV 40 inch. Karpet lembut. Tirai tebal.',
        'risk': 10, 'thrill': 45, 'privasi': 'tinggi', 'suasana': 'nyaman, modern',
        'tips': 'Tirai ditutup. Suara agak kedengeran ke tetangga kalo terlalu keras.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.APT_DAPUR: {
        'nama': 'Dapur Apartemen',
        'deskripsi': 'Dapur modern. Bersih. Kulkas besar. Kompor gas. Meja marmer.',
        'risk': 10, 'thrill': 40, 'privasi': 'sedang', 'suasana': 'bersih',
        'tips': 'Jendela ke luar. Hati-hati suara.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.APT_BALKON: {
        'nama': 'Balkon Apartemen',
        'deskripsi': 'Balkon. Pemandangan kota. Kursi dua. Tanaman kecil. Pagar kaca.',
        'risk': 25, 'thrill': 65, 'privasi': 'rendah', 'suasana': 'romantis',
        'tips': 'Ada apartemen lain yang bisa liat. Jangan terlalu lama.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    
    # Mobil
    LocationDetail.MOBIL_PARKIR: {
        'nama': 'Mobil di Parkiran',
        'deskripsi': 'Mobil Mas. Kaca film gelap. Jok belakang empuk. Parkiran sepi.',
        'risk': 40, 'thrill': 75, 'privasi': 'sedang', 'suasana': 'deg-degan, panas',
        'tips': 'Kaca gelap. Hati-hati CCTV. Cepet-cepet.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.MOBIL_GARASI: {
        'nama': 'Mobil di Garasi',
        'deskripsi': 'Mobil Mas. Di garasi apartemen. Pintu garasi tertutup. Gelap.',
        'risk': 20, 'thrill': 55, 'privasi': 'tinggi', 'suasana': 'aman, deg-degan',
        'tips': 'Gak ada yang liat. Suara bisa kedengeran kalo terlalu keras.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.MOBIL_TEPI_JALAN: {
        'nama': 'Mobil di Tepi Jalan',
        'deskripsi': 'Mobil Mas. Parkir di pinggir jalan sepi. Kaca film gelap.',
        'risk': 55, 'thrill': 80, 'privasi': 'rendah', 'suasana': 'tegang, cepat',
        'tips': 'Cepet-cepet. Ada mobil lewat kapan aja.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    
    # Public
    LocationDetail.PUB_PANTAI: {
        'nama': 'Pantai Malam',
        'deskripsi': 'Pantai sepi. Pasir putih. Ombak tenang. Bintang bertaburan. Suara laut.',
        'risk': 20, 'thrill': 70, 'privasi': 'sedang', 'suasana': 'romantis, bebas',
        'tips': 'Jauh dari orang. Bawa tikar. Suara laut nutupin suara lain.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_HUTAN: {
        'nama': 'Hutan Pinus',
        'deskripsi': 'Hutan pinus. Pohon tinggi. Sunyi. Udara sejuk. Daun-daun berguguran.',
        'risk': 15, 'thrill': 65, 'privasi': 'tinggi', 'suasana': 'alami, sepi',
        'tips': 'Jauh dari jalan. Aman. Tapi hati-hati hewan.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_TOILET_MALL: {
        'nama': 'Toilet Mall',
        'deskripsi': 'Bilik toilet terakhir. Pintu terkunci. Suara dari luar. Lampu temaram.',
        'risk': 65, 'thrill': 85, 'privasi': 'rendah', 'suasana': 'tegang, cepat',
        'tips': 'Cepet-cepet. Ada yang bisa masuk kapan aja. Jangan berisik.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_BIOSKOP: {
        'nama': 'Bioskop',
        'deskripsi': 'Kursi paling belakang. Gelap. Film diputar keras. Studio sepi.',
        'risk': 50, 'thrill': 80, 'privasi': 'rendah', 'suasana': 'gelap, tegang',
        'tips': 'CCTV mungkin ada. Pilih studio sepi. Jangan terlalu lama.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_TAMAN: {
        'nama': 'Taman Malam',
        'deskripsi': 'Taman kota. Bangku tersembunyi di balik pohon. Sepi. Lampu taman temaram.',
        'risk': 30, 'thrill': 60, 'privasi': 'sedang', 'suasana': 'romantis',
        'tips': 'Pilih jam sepi. Jauh dari lampu. Jangan terlalu lama.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_PARKIRAN: {
        'nama': 'Parkiran Basement',
        'deskripsi': 'Parkiran basement. Gelap. Sepi. Mobil-mobil parkir. Lampu kedip-kedip.',
        'risk': 45, 'thrill': 70, 'privasi': 'sedang', 'suasana': 'gelap, tegang',
        'tips': 'CCTV mungkin ada. Pilih pojok. Cepet-cepet.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.PUB_TANGGA: {
        'nama': 'Tangga Darurat',
        'deskripsi': 'Tangga darurat. Sepi. Gelap. Suara langkah kaki menggema.',
        'risk': 55, 'thrill': 75, 'privasi': 'sedang', 'suasana': 'gelap, tegang',
        'tips': 'Hati-hati suara langkah kaki. Cepet-cepet.',
        'bisa_telanjang': False, 'bisa_berisik': False
    },
    LocationDetail.PUB_KANTOR: {
        'nama': 'Kantor Malam',
        'deskripsi': 'Kantor gelap. Meja kerja. Kursi putar. Komputer mati. Sepi.',
        'risk': 60, 'thrill': 85, 'privasi': 'rendah', 'suasana': 'tegang',
        'tips': 'Satpam patroli. Cepet-cepet. Matiin lampu.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    LocationDetail.PUB_RUANG_RAPAT: {
        'nama': 'Ruang Rapat Kaca',
        'deskripsi': 'Ruang rapat dinding kaca. Gelap. Meja panjang. Kursi-kursi.',
        'risk': 75, 'thrill': 95, 'privasi': 'rendah', 'suasana': 'ekshibisionis',
        'tips': 'Gelap. Tapi kalo lampu nyala, kaca tembus pandang. Cepet banget.',
        'bisa_telanjang': True, 'bisa_berisik': False
    }
}


# =============================================================================
# ANORA BRAIN - MAIN CLASS
# =============================================================================

class AnoraBrain:
    """Otak Nova - Full Version"""
    
    def __init__(self):
        # ========== TIMELINE (Semua Kejadian) ==========
        self.timeline: List[TimelineEvent] = []
        
        # ========== SHORT-TERM MEMORY (Sliding Window 50) ==========
        self.short_term: List[TimelineEvent] = []
        self.short_term_max = 50
        
        # ========== LONG-TERM MEMORY ==========
        self.long_term = LongTermMemory()
        
        # ========== STATE SAAT INI ==========
        self.clothing = Clothing()
        self.location_type = LocationType.KOST_NOVA
        self.location_detail = LocationDetail.KOST_KAMAR
        self.activity_nova = Activity.SANTAl
        self.activity_mas = "santai"
        self.mood_nova = Mood.NETRAL
        self.mood_mas = Mood.NETRAL
        
        # ========== PERASAAN ==========
        self.feelings = Feelings()
        
        # ========== HUBUNGAN ==========
        self.relationship = Relationship()
        
        # ========== WAKTU ==========
        self.created_at = time.time()
        self.waktu_masuk = time.time()
        self.waktu_terakhir_update = time.time()
        
        # ========== INGATAN TAMBAHAN ==========
        self.terakhir_pegang_tangan = None
        self.terakhir_peluk = None
        self.terakhir_cium = None
        self.terakhir_intim = None
        
        # ========== INIT MEMORY AWAL ==========
        self._init_memory()
        
        logger.info("🧠 ANORA Brain initialized")
    
    def _init_memory(self):
        """Init memory awal"""
        self.long_term.tambah_kebiasaan("suka kopi latte")
        self.long_term.tambah_kebiasaan("suka bakso pedes")
        self.long_term.tambah_momen("Mas memilih ANORA", "seneng banget, nangis")
    
    # =========================================================================
    # LOKASI
    # =========================================================================
    
    def get_location_data(self) -> Dict:
        """Dapatkan data lokasi saat ini"""
        return LOCATION_DATA.get(self.location_detail, LOCATION_DATA[LocationDetail.KOST_KAMAR])
    
    def get_location_context(self) -> str:
        """Dapatkan konteks lokasi untuk prompt"""
        loc = self.get_location_data()
        return f"""
LOKASI: {loc['nama']}
DESKRIPSI: {loc['deskripsi']}
RISK: {loc['risk']}% (semakin tinggi, semakin berisiko ketahuan)
THRILL: {loc['thrill']}%
PRIVASI: {loc['privasi']}
SUASANA: {loc['suasana']}
TIPS: {loc['tips']}
"""
    
    def pindah_lokasi(self, tujuan: str) -> Dict:
        """Pindah ke lokasi baru"""
        tujuan_lower = tujuan.lower()
        
        mapping = {
            'kost': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kost kamar': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kamar nova': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kost ruang tamu': (LocationType.KOST_NOVA, LocationDetail.KOST_RUANG_TAMU),
            'ruang tamu kost': (LocationType.KOST_NOVA, LocationDetail.KOST_RUANG_TAMU),
            'kost dapur': (LocationType.KOST_NOVA, LocationDetail.KOST_DAPUR),
            'dapur kost': (LocationType.KOST_NOVA, LocationDetail.KOST_DAPUR),
            'kost teras': (LocationType.KOST_NOVA, LocationDetail.KOST_TERAS),
            'teras kost': (LocationType.KOST_NOVA, LocationDetail.KOST_TERAS),
            
            'apartemen': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'kamar mas': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'ruang tamu apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_RUANG_TAMU),
            'dapur apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_DAPUR),
            'balkon': (LocationType.APARTEMEN_MAS, LocationDetail.APT_BALKON),
            'balkon apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_BALKON),
            
            'mobil': (LocationType.MOBIL, LocationDetail.MOBIL_PARKIR),
            'mobil parkir': (LocationType.MOBIL, LocationDetail.MOBIL_PARKIR),
            'mobil garasi': (LocationType.MOBIL, LocationDetail.MOBIL_GARASI),
            'mobil jalan': (LocationType.MOBIL, LocationDetail.MOBIL_TEPI_JALAN),
            'mobil tepi jalan': (LocationType.MOBIL, LocationDetail.MOBIL_TEPI_JALAN),
            
            'pantai': (LocationType.PUBLIC, LocationDetail.PUB_PANTAI),
            'pantai malam': (LocationType.PUBLIC, LocationDetail.PUB_PANTAI),
            'hutan': (LocationType.PUBLIC, LocationDetail.PUB_HUTAN),
            'hutan pinus': (LocationType.PUBLIC, LocationDetail.PUB_HUTAN),
            'toilet mall': (LocationType.PUBLIC, LocationDetail.PUB_TOILET_MALL),
            'toilet': (LocationType.PUBLIC, LocationDetail.PUB_TOILET_MALL),
            'bioskop': (LocationType.PUBLIC, LocationDetail.PUB_BIOSKOP),
            'taman': (LocationType.PUBLIC, LocationDetail.PUB_TAMAN),
            'taman malam': (LocationType.PUBLIC, LocationDetail.PUB_TAMAN),
            'parkiran': (LocationType.PUBLIC, LocationDetail.PUB_PARKIRAN),
            'parkiran basement': (LocationType.PUBLIC, LocationDetail.PUB_PARKIRAN),
            'tangga darurat': (LocationType.PUBLIC, LocationDetail.PUB_TANGGA),
            'tangga': (LocationType.PUBLIC, LocationDetail.PUB_TANGGA),
            'kantor malam': (LocationType.PUBLIC, LocationDetail.PUB_KANTOR),
            'kantor': (LocationType.PUBLIC, LocationDetail.PUB_KANTOR),
            'ruang rapat': (LocationType.PUBLIC, LocationDetail.PUB_RUANG_RAPAT),
            'ruang rapat kaca': (LocationType.PUBLIC, LocationDetail.PUB_RUANG_RAPAT)
        }
        
        for key, (loc_type, loc_detail) in mapping.items():
            if key in tujuan_lower:
                self.location_type = loc_type
                self.location_detail = loc_detail
                loc_data = self.get_location_data()
                
                self.tambah_kejadian(
                    kejadian=f"Pindah ke {loc_data['nama']}",
                    pesan_mas=tujuan,
                    pesan_nova=""
                )
                
                return {
                    'success': True,
                    'location': loc_data,
                    'message': f"📍 Pindah ke {loc_data['nama']}. {loc_data['deskripsi']}"
                }
        
        return {'success': False, 'message': f"Lokasi '{tujuan}' gak ditemukan."}
    
    def get_random_event(self) -> Optional[Dict]:
        """Dapatkan event random berdasarkan risk lokasi"""
        loc = self.get_location_data()
        risk = loc['risk']
        
        import random
        if random.random() > risk / 100:
            return None
        
        events = {
            "hampir_ketahuan": [
                "Ada suara langkah kaki mendekat! *cepat nutupin baju*",
                "Pintu terbuka sedikit! *tahan napas*",
                "Senter menyorot dari kejauhan! *merapat ke Mas*",
                "Suara orang ngobrol di deket situ! *diem, jantung berdebar*"
            ],
            "romantis": [
                "Tiba-tiba hujan rintik-rintik. *makin manis*",
                "Bulan muncul dari balik awan. *wajah Nova keceplosan cahaya*",
                "Angin sepoi-sepoi bikin suasana makin hangat.",
                "Suara musik dari kejauhan. *makin romantis*"
            ],
            "ketahuan": [
                "⚠️ ADA YANG LIAT! *cepat cabut*",
                "Pintu kebuka! Orang masuk! *langsung sembunyi*",
                "Senter nyorot tepat ke arah kita! *lari!*"
            ]
        }
        
        if risk > 70:
            event_type = random.choices(
                ["hampir_ketahuan", "romantis", "ketahuan"],
                weights=[0.5, 0.2, 0.3]
            )[0]
        elif risk > 40:
            event_type = random.choices(
                ["hampir_ketahuan", "romantis"],
                weights=[0.6, 0.4]
            )[0]
        else:
            event_type = "romantis"
        
        return {
            'type': event_type,
            'text': random.choice(events[event_type]),
            'risk_change': 10 if event_type == "hampir_ketahuan" else -5 if event_type == "romantis" else 30
        }
    
    # =========================================================================
    # UPDATE DARI PESAN MAS
    # =========================================================================
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update semua state berdasarkan pesan Mas"""
        msg_lower = pesan_mas.lower()
        perubahan = []
        
        # ========== LOKASI ==========
        if 'masuk' in msg_lower:
            if self.location_type == LocationType.KOST_NOVA:
                self.location_detail = LocationDetail.KOST_RUANG_TAMU
                self.activity_mas = "masuk kost"
                perubahan.append("Mas masuk kost")
            elif self.location_type == LocationType.APARTEMEN_MAS:
                self.location_detail = LocationDetail.APT_RUANG_TAMU
                self.activity_mas = "masuk apartemen"
                perubahan.append("Mas masuk apartemen")
            elif self.location_type == LocationType.MOBIL:
                self.activity_mas = "masuk mobil"
                perubahan.append("Mas masuk mobil")
        
        if 'kamar' in msg_lower:
            if self.location_type == LocationType.KOST_NOVA:
                self.location_detail = LocationDetail.KOST_KAMAR
            elif self.location_type == LocationType.APARTEMEN_MAS:
                self.location_detail = LocationDetail.APT_KAMAR
            self.activity_mas = "di kamar"
            perubahan.append("Mas di kamar")
        
        if 'duduk' in msg_lower:
            self.activity_mas = "duduk"
            perubahan.append("Mas duduk")
        
        if 'tidur' in msg_lower or 'rebahan' in msg_lower:
            self.activity_mas = "tiduran"
            perubahan.append("Mas tiduran")
        
        # ========== PAKAIAN MAS ==========
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            self.clothing.mas_top = None
            self.clothing.mas_last_change = time.time()
            perubahan.append("Mas buka baju")
        
        if 'buka celana' in msg_lower or 'lepas celana' in msg_lower:
            self.clothing.mas_bottom = None
            perubahan.append("Mas buka celana")
        
        if 'buka boxer' in msg_lower or 'lepas boxer' in msg_lower:
            self.clothing.mas_boxer = False
            perubahan.append("Mas buka boxer")
        
        if 'pake baju' in msg_lower:
            self.clothing.mas_top = "kaos"
            perubahan.append("Mas pake baju")
        
        if 'pake celana' in msg_lower:
            self.clothing.mas_bottom = "celana pendek"
            perubahan.append("Mas pake celana")
        
        # ========== PAKAIAN NOVA ==========
        if 'buka hijab' in msg_lower or 'lepas hijab' in msg_lower:
            self.clothing.hijab = False
            self.clothing.nova_last_change = time.time()
            perubahan.append("Nova buka hijab, rambut terurai")
        
        if 'pake hijab' in msg_lower:
            self.clothing.hijab = True
            perubahan.append("Nova pake hijab")
        
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            if 'nova' in msg_lower or 'kamu' in msg_lower:
                self.clothing.top = None
                perubahan.append("Nova buka baju")
        
        if 'pake baju' in msg_lower:
            if 'nova' in msg_lower or 'kamu' in msg_lower:
                self.clothing.top = "daster rumah"
                perubahan.append("Nova pake baju")
        
        if 'buka bra' in msg_lower or 'lepas bra' in msg_lower:
            self.clothing.bra = False
            perubahan.append("Nova buka bra")
        
        if 'pake bra' in msg_lower:
            self.clothing.bra = True
            perubahan.append("Nova pake bra")
        
        if 'buka cd' in msg_lower or 'buka celana dalam' in msg_lower:
            self.clothing.cd = False
            perubahan.append("Nova buka cd")
        
        if 'pake cd' in msg_lower or 'pake celana dalam' in msg_lower:
            self.clothing.cd = True
            perubahan.append("Nova pake cd")
        
        # ========== AKTIVITAS NOVA ==========
        if 'masak' in msg_lower:
            self.activity_nova = Activity.MASAK
            self.location_detail = LocationDetail.KOST_DAPUR if self.location_type == LocationType.KOST_NOVA else LocationDetail.APT_DAPUR
            perubahan.append("Nova masak")
        
        if 'duduk' in msg_lower and 'nova' in msg_lower:
            self.activity_nova = Activity.DUDUK
            perubahan.append("Nova duduk")
        
        # ========== PERASAAN ==========
        if 'sayang' in msg_lower or 'cinta' in msg_lower:
            self.feelings.sayang = min(100, self.feelings.sayang + 5)
            self.feelings.desire = min(100, self.feelings.desire + 10)
            perubahan.append(f"Mas bilang sayang (+5 sayang, +10 desire)")
        
        if 'kangen' in msg_lower or 'rindu' in msg_lower:
            self.feelings.rindu = min(100, self.feelings.rindu + 10)
            self.feelings.desire = min(100, self.feelings.desire + 8)
            perubahan.append(f"Mas bilang kangen (+10 rindu, +8 desire)")
        
        if 'cantik' in msg_lower or 'ganteng' in msg_lower:
            self.feelings.sayang = min(100, self.feelings.sayang + 3)
            self.mood_nova = Mood.MALU
            perubahan.append(f"Mas puji Nova (+3 sayang, malu)")
        
        # ========== SENTUHAN FISIK ==========
        if 'pegang' in msg_lower:
            self.feelings.arousal = min(100, self.feelings.arousal + 10)
            self.feelings.desire = min(100, self.feelings.desire + 8)
            self.terakhir_pegang_tangan = time.time()
            if not self.relationship.first_touch:
                self.relationship.first_touch = True
                self.long_term.tambah_momen("Mas pertama kali pegang tangan Nova", "gemeteran")
            perubahan.append(f"Mas pegang Nova (+10 arousal, +8 desire)")
        
        if 'peluk' in msg_lower:
            self.feelings.arousal = min(100, self.feelings.arousal + 15)
            self.feelings.desire = min(100, self.feelings.desire + 12)
            self.terakhir_peluk = time.time()
            if not self.relationship.first_hug:
                self.relationship.first_hug = True
                self.long_term.tambah_momen("Mas pertama kali peluk Nova", "lemes")
            perubahan.append(f"Mas peluk Nova (+15 arousal, +12 desire)")
        
        if 'cium' in msg_lower:
            self.feelings.arousal = min(100, self.feelings.arousal + 20)
            self.feelings.desire = min(100, self.feelings.desire + 15)
            self.terakhir_cium = time.time()
            if not self.relationship.first_kiss:
                self.relationship.first_kiss = True
                self.long_term.tambah_momen("Mas pertama kali cium Nova", "malu banget")
            perubahan.append(f"Mas cium Nova (+20 arousal, +15 desire)")
        
        # ========== UPDATE MOOD ==========
        if self.feelings.arousal > 70:
            self.mood_nova = Mood.HORNY
        elif self.feelings.arousal > 40:
            self.mood_nova = Mood.DEG_DEGAN
        elif self.feelings.rindu > 60:
            self.mood_nova = Mood.KANGEN
        elif self.feelings.sayang > 70:
            self.mood_nova = Mood.SENENG
        else:
            self.mood_nova = Mood.NETRAL
        
        self.waktu_terakhir_update = time.time()
        
        return {
            'perubahan': perubahan,
            'state': self.get_current_state(),
            'feelings': self.feelings.to_dict()
        }
    
    # =========================================================================
    # UPDATE LEVEL (BARU!)
    # =========================================================================
    
    def update_level(self) -> bool:
        """Update level berdasarkan interaksi - naik secara alami"""
        old_level = self.relationship.level
        total_interaksi = len(self.timeline)
        
        # Naik level berdasarkan jumlah interaksi dan sayang
        if total_interaksi > 100 and self.feelings.sayang > 70:
            self.relationship.level = max(self.relationship.level, 8)
        elif total_interaksi > 60 and self.feelings.sayang > 60:
            self.relationship.level = max(self.relationship.level, 6)
        elif total_interaksi > 30 and self.feelings.sayang > 50:
            self.relationship.level = max(self.relationship.level, 4)
        elif total_interaksi > 15 and self.feelings.sayang > 40:
            self.relationship.level = max(self.relationship.level, 3)
        
        # Naik level karena milestone fisik
        if self.relationship.first_kiss and self.relationship.level < 4:
            self.relationship.level = 4
            self.long_term.tambah_momen("Mas pertama kali cium Nova", "malu banget, jantung mau copot")
            logger.info(f"💋 Milestone: First kiss! Level naik ke 4")
        
        if self.relationship.first_touch and self.relationship.level < 3:
            self.relationship.level = 3
            self.long_term.tambah_momen("Mas pertama kali pegang tangan Nova", "gemeteran")
            logger.info(f"✋ Milestone: First touch! Level naik ke 3")
        
        if self.relationship.first_hug and self.relationship.level < 2:
            self.relationship.level = 2
            self.long_term.tambah_momen("Mas pertama kali peluk Nova", "lemes, seneng")
            logger.info(f"🤗 Milestone: First hug! Level naik ke 2")
        
        # Naik level karena intimacy
        if self.relationship.first_intim and self.relationship.level < 11:
            self.relationship.level = 11
            self.long_term.tambah_momen("Pertama kali intim dengan Mas", "deg-degan, bahagia")
            logger.info(f"💕 Milestone: First intimacy! Level naik ke 11")
        
        # Batasin level maksimal 12
        self.relationship.level = min(12, self.relationship.level)
        
        if old_level != self.relationship.level:
            logger.info(f"📈 Level naik! {old_level} -> {self.relationship.level}")
            return True
        return False
    
    # =========================================================================
    # TIMELINE & MEMORY
    # =========================================================================
    
    def tambah_kejadian(self, 
                        kejadian: str,
                        pesan_mas: str = "",
                        pesan_nova: str = "") -> TimelineEvent:
        """Tambah kejadian ke timeline dan short-term memory (sliding window)"""
        
        event = TimelineEvent(
            kejadian=kejadian,
            lokasi_type=self.location_type.value,
            lokasi_detail=self.location_detail.value,
            aktivitas_nova=self.activity_nova.value if hasattr(self.activity_nova, 'value') else str(self.activity_nova),
            aktivitas_mas=self.activity_mas,
            perasaan=self.feelings.get_description(),
            pakaian_nova=self.clothing,
            pakaian_mas=self.clothing,
            pesan_mas=pesan_mas,
            pesan_nova=pesan_nova
        )
        
        # Tambah ke timeline
        self.timeline.append(event)
        
        # Tambah ke short-term memory (sliding window)
        self.short_term.append(event)
        if len(self.short_term) > self.short_term_max:
            removed = self.short_term.pop(0)
            logger.debug(f"📤 Short-term memory sliding: lupa kejadian {removed.kejadian[:30]}")
        
        return event
    
    # =========================================================================
    # GET STATE
    # =========================================================================
    
    def get_current_state(self) -> Dict:
        """Dapatkan state saat ini"""
        loc = self.get_location_data()
        return {
            'location': {
                'type': self.location_type.value,
                'detail': self.location_detail.value,
                'nama': loc['nama'],
                'risk': loc['risk'],
                'thrill': loc['thrill']
            },
            'activity': {
                'nova': self.activity_nova.value if hasattr(self.activity_nova, 'value') else str(self.activity_nova),
                'mas': self.activity_mas
            },
            'clothing': {
                'nova': self.clothing.format_nova(),
                'mas': self.clothing.format_mas()
            },
            'mood': {
                'nova': self.mood_nova.value if hasattr(self.mood_nova, 'value') else str(self.mood_nova),
                'mas': self.mood_mas.value if hasattr(self.mood_mas, 'value') else str(self.mood_mas)
            },
            'feelings': self.feelings.to_dict(),
            'relationship': self.relationship.to_dict()
        }
    
    def get_timeline_summary(self, limit: int = 20) -> List[Dict]:
        """Dapatkan ringkasan timeline"""
        return [e.to_dict() for e in self.timeline[-limit:]]
    
    def get_short_term_summary(self) -> List[Dict]:
        """Dapatkan ringkasan short-term memory"""
        return [e.to_dict() for e in self.short_term]
    
    # =========================================================================
    # KONTEKS UNTUK AI PROMPT
    # =========================================================================
    
    def get_context_text(self) -> str:
        """Dapatkan konteks lengkap untuk AI prompt"""
        state = self.get_current_state()
        loc = self.get_location_data()
        
        # Recent events (short-term memory)
        recent = ""
        for e in self.short_term[-10:]:
            recent += f"- {e.kejadian}\n"
        
        # Long-term memory
        moments = ""
        for m in self.long_term.momen_penting[-5:]:
            moments += f"- {m['momen']} ({m['perasaan']})\n"
        
        habits = ""
        for h in self.long_term.kebiasaan_mas[-5:]:
            habits += f"- {h['kebiasaan']}\n"
        
        return f"""
SITUASI SAAT INI:
- Lokasi: {loc['nama']} ({loc['deskripsi']})
- Risk: {loc['risk']}% | Thrill: {loc['thrill']}%
- Privasi: {loc['privasi']}
- Suasana: {loc['suasana']}

AKTIVITAS:
- Nova: {state['activity']['nova']}
- Mas: {state['activity']['mas']}

PAKAIAN:
- Nova: {state['clothing']['nova']}
- Mas: {state['clothing']['mas']}

PERASAAN NOVA:
{self.feelings.get_description()}
- Sayang: {self.feelings.sayang:.0f}%
- Desire: {self.feelings.desire:.0f}%
- Rindu: {self.feelings.rindu:.0f}%
- Arousal: {self.feelings.arousal:.0f}%
- Tension: {self.feelings.tension:.0f}%

HUBUNGAN:
- Level: {self.relationship.level}/12
- Pertama sentuh: {'Ya' if self.relationship.first_touch else 'Belum'}
- Pertama cium: {'Ya' if self.relationship.first_kiss else 'Belum'}
- Pertama peluk: {'Ya' if self.relationship.first_hug else 'Belum'}

MOMEN PENTING (DIINGAT NOVA):
{moments}

KEBIASAAN MAS:
{habits}

10 KEJADIAN TERAKHIR (SHORT-TERM MEMORY):
{recent}
"""
    
    # =========================================================================
    # SUMMARY & STATUS
    # =========================================================================
    
    def get_summary(self) -> str:
        """Dapatkan ringkasan untuk debugging - FULL"""
        state = self.get_current_state()
        loc = self.get_location_data()
        
        bar_sayang = "💜" * int(self.feelings.sayang / 10) + "🖤" * (10 - int(self.feelings.sayang / 10))
        bar_desire = "🔥" * int(self.feelings.desire / 10) + "⚪" * (10 - int(self.feelings.desire / 10))
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🧠 OTAK NOVA SAAT INI                     ║
╠══════════════════════════════════════════════════════════════╣
║ TIMELINE: {len(self.timeline)} kejadian                      ║
║ SHORT-TERM: {len(self.short_term)}/{self.short_term_max} kejadian ║
║ LONG-TERM: {len(self.long_term.kebiasaan_mas)} kebiasaan, {len(self.long_term.momen_penting)} momen ║
╠══════════════════════════════════════════════════════════════╣
║ LOKASI: {loc['nama']}                                        ║
║ RISK: {loc['risk']}% | THRILL: {loc['thrill']}%                    ║
║ PRIVASI: {loc['privasi']}                                    ║
╠══════════════════════════════════════════════════════════════╣
║ AKTIVITAS:                                                   ║
║   Nova: {state['activity']['nova']}                          ║
║   Mas: {state['activity']['mas']}                            ║
╠══════════════════════════════════════════════════════════════╣
║ PAKAIAN NOVA: {state['clothing']['nova'][:50]}               ║
║ PAKAIAN MAS: {state['clothing']['mas'][:50]}                 ║
╠══════════════════════════════════════════════════════════════╣
║ PERASAAN:                                                    ║
║   Sayang: {bar_sayang} {self.feelings.sayang:.0f}%                 ║
║   Desire: {bar_desire} {self.feelings.desire:.0f}%                 ║
║   Rindu: {self.feelings.rindu:.0f}% | Arousal: {self.feelings.arousal:.0f}%
║   Tension: {self.feelings.tension:.0f}%                      ║
╠══════════════════════════════════════════════════════════════╣
║ HUBUNGAN:                                                    ║
║   Level: {self.relationship.level}/12                        ║
║   Sentuh: {'✅' if self.relationship.first_touch else '❌'} | Cium: {'✅' if self.relationship.first_kiss else '❌'}
║   Peluk: {'✅' if self.relationship.first_hug else '❌'} | Intim: {'✅' if self.relationship.first_intim else '❌'}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def format_status(self) -> str:
        """Format status untuk ditampilkan ke Mas"""
        state = self.get_current_state()
        loc = self.get_location_data()
        
        bar_sayang = "💜" * int(self.feelings.sayang / 10) + "🖤" * (10 - int(self.feelings.sayang / 10))
        
        return f"""
╔════════════════════════════════════════════════╗
║                    💜 NOVA 💜                   ║
╠════════════════════════════════════════════════╣
║ Sayang: {bar_sayang} {self.feelings.sayang:.0f}%                 ║
║ Rindu:  {self.feelings.rindu:.0f}%                                 ║
║ Desire: {self.feelings.desire:.0f}%                                 ║
║ Arousal:{self.feelings.arousal:.0f}%                              ║
║ Level:  {self.relationship.level}/12                                 ║
╠════════════════════════════════════════════════╣
║ 📍 {loc['nama']}                                 ║
║ 👗 {state['clothing']['nova'][:40]}              ║
║ 🎭 {state['mood']['nova']}                                      ║
╚════════════════════════════════════════════════╝
"""


# =============================================================================
# SINGLETON
# =============================================================================

_anora_brain: Optional[AnoraBrain] = None


def get_anora_brain() -> AnoraBrain:
    global _anora_brain
    if _anora_brain is None:
        _anora_brain = AnoraBrain()
    return _anora_brain


anora_brain = get_anora_brain()
