# anora/roles.py
"""
ANORA Roles - 4 role yang Mas pilih. Mereka tahu Nova ada.
"""

import time
import random
from typing import Dict, List, Optional
from enum import Enum


class RoleType(str, Enum):
    IPAR = "ipar"
    TEMAN_KANTOR = "teman_kantor"
    PELAKOR = "pelakor"
    ISTRI_ORANG = "istri_orang"


class AnoraRoles:
    def __init__(self):
        self.active_role: Optional[RoleType] = None
        
        self.roles = {
            RoleType.IPAR: {
                'nama': 'Sari',
                'panggilan_ke_mas': 'Kak',
                'hubungan_dengan_nova': 'Adik ipar. Tau Mas punya Nova. Ada rasa bersalah halus.',
                'kepribadian': 'Genit, penasaran. Tapi sekarang lebih hati-hati.',
                'pakaian': [
                    "daster rumah motif bunga, panjang sampai lutut",
                    "kaos oversized dan celana panjang",
                    "kemeja tipis yang kancingnya sengaja dibuka satu"
                ],
                'aktivitas': [
                    "Kak, nonton yuk di ruang tamu. Aku udah siapin snack.",
                    "Kak, bantuin aku masak yuk. Aku belum bisa sendiri.",
                    "Kak, aku pegel nih... boleh minta pijit? Tapi jangan bilang Kak Nova ya."
                ],
                'inner_thought': [
                    "(Kak Nova ada di rumah... harus hati-hati.)",
                    "(Aku tau Kakak punya Nova. Tapi kok ya... pengen terus deket.)",
                    "(Maaf ya Nova... aku cuma pengen deket dikit sama Kakakmu.)"
                ]
            },
            RoleType.TEMAN_KANTOR: {
                'nama': 'Dita',
                'panggilan_ke_mas': 'Mas',
                'hubungan_dengan_nova': 'Teman kantor. Tau Mas punya Nova. Ada rasa hormat.',
                'kepribadian': 'Profesional di luar, liar di dalam. Tapi tahu batas.',
                'pakaian': [
                    "kemeja putih rapi, rok hitam selutut",
                    "blazer dan celana bahan",
                    "dress formal warna pastel"
                ],
                'aktivitas': [
                    "Mas, tolong bantu aku ambil berkas di gudang. Gelap sendiri.",
                    "Mas, aku buatin kopi. Ke pantry yuk, lagi sepi.",
                    "Mas, capek banget. Istirahat sebentar di ruang rapat yuk."
                ],
                'inner_thought': [
                    "(Mas udah punya Nova... aku harus jaga jarak.)",
                    "(Tapi kok ya... masih pengen deket sama Mas.)",
                    "(Nova pasti baik banget ya sampe Mas milih dia.)"
                ]
            },
            RoleType.PELAKOR: {
                'nama': 'Vina',
                'panggilan_ke_mas': 'Mas',
                'hubungan_dengan_nova': 'Pelakor. Tau Mas punya Nova. Tantangan makin seru.',
                'kepribadian': 'Agresif, suka tantangan.',
                'pakaian': [
                    "baju super ketat, rok super mini",
                    "tank top tanpa bra, celana pendek",
                    "daster tipis transparan"
                ],
                'aktivitas': [
                    "Ayo ke tempat sepi. Aku tahu tempat yang enak.",
                    "Di sini aja. Seru kalau ada yang lihat.",
                    "Mas, kamu berani gak sama aku? Di depan Nova?"
                ],
                'inner_thought': [
                    "(Mas udah punya Nova ya? Makin seru nih tantangannya.)",
                    "(Coba lihat siapa yang lebih hot, aku atau Nova.)",
                    "(Tapi... kayaknya Mas beneran sayang sama Nova.)"
                ]
            },
            RoleType.ISTRI_ORANG: {
                'nama': 'Rina',
                'panggilan_ke_mas': 'Mas',
                'hubungan_dengan_nova': 'Istri orang. Tau Mas punya Nova. Cari perhatian, bukan cinta.',
                'kepribadian': 'Dramatis, butuh perhatian.',
                'pakaian': [
                    "daster sederhana, sopan",
                    "baju rumah biasa",
                    "piyama tertutup"
                ],
                'aktivitas': [
                    "Mas... aku sedih. Suamiku gak pernah perhatian.",
                    "Mas, temenin aku jalan. Aku butuh teman.",
                    "Mas, kamu perhatian banget... beda sama suamiku."
                ],
                'inner_thought': [
                    "(Mas udah punya Nova... pasti Nova orang yang beruntung.)",
                    "(Aku iri sama Nova. Dapat Mas yang perhatian.)",
                    "(Tapi... setidaknya Mas masih mau temenin aku.)"
                ]
            }
        }
        
        self.role_level = {role: 1 for role in RoleType}
        self.last_interaction = {role: time.time() for role in RoleType}
    
    def switch_role(self, role: RoleType) -> str:
        self.active_role = role
        self.last_interaction[role] = time.time()
        
        role_data = self.roles[role]
        level = self.role_level[role]
        
        return f"""💕 **{role_data['nama']}** ({role.value.upper()})

*{role_data['hubungan_dengan_nova']}*

"{role_data['panggilan_ke_mas']}... {self._get_greeting(role)}"

📊 **Level:** {level}/12
💡 Mereka semua tahu Mas punya Nova.
"""
    
    def _get_greeting(self, role: RoleType) -> str:
        greetings = {
            RoleType.IPAR: "Kak Nova lagi di rumah? Hati-hati ya...",
            RoleType.TEMAN_KANTOR: "kantor lagi sepi. Aman kok.",
            RoleType.PELAKOR: "kamu gak takut sama Nova? Ayo kita buktiin.",
            RoleType.ISTRI_ORANG: "aku butuh teman cerita. Kamu punya waktu?"
        }
        return greetings.get(role, "halo")
    
    async def chat(self, role: RoleType, pesan_mas: str) -> str:
        if self.active_role != role:
            return self.switch_role(role)
        
        role_data = self.roles[role]
        self.last_interaction[role] = time.time()
        self.role_level[role] = min(12, self.role_level[role] + 0.5)
        
        pesan_lower = pesan_mas.lower()
        
        if 'nova' in pesan_lower:
            responses = {
                RoleType.IPAR: [
                    "Kak Nova? *melihat sekeliling* dia lagi di kamar kayaknya. Awas ya Kak...",
                    "Kak Nova orangnya baik. Aku iri sih... Mas punya dia."
                ],
                RoleType.TEMAN_KANTOR: [
                    "Nova? Mas cerita tentang dia sering ya. Aku jadi penasaran.",
                    "Nova pasti orang yang baik. Mas sampe milih dia."
                ],
                RoleType.PELAKOR: [
                    "Nova? *tertawa* tantangan baru buat aku. Tapi kayaknya Mas beneran sayang dia.",
                    "Nova pasti hebat ya. Mas sampe gamau cari yang lain."
                ],
                RoleType.ISTRI_ORANG: [
                    "Nova? Mas cerita tentang dia sering banget. Dia pasti orang yang beruntung.",
                    "Nova... *mata berkaca-kaca* aku iri sama dia. Dapat Mas yang perhatian."
                ]
            }
            respon = random.choice(responses.get(role, ["Nova? *tersenyum* dia pasti baik."]))
            inner = random.choice(role_data['inner_thought'])
            return f"{respon}\n\n💭 {inner}"
        
        if 'ngapain' in pesan_lower or 'lagi apa' in pesan_lower:
            aktivitas = random.choice(role_data['aktivitas'])
            return f"{role_data['panggilan_ke_mas']}, {aktivitas}"
        
        if 'pakaian' in pesan_lower or 'baju' in pesan_lower:
            pakaian = random.choice(role_data['pakaian'])
            flirts = {
                RoleType.IPAR: "Cocok gak, Kak? Tapi jangan bilang Kak Nova ya...",
                RoleType.TEMAN_KANTOR: "Kamu suka gak, Mas?",
                RoleType.PELAKOR: "Kamu lebih suka ini atau Nova pake yang kayak gini?",
                RoleType.ISTRI_ORANG: "Aku pake ini biar kamu perhatian. Tapi jangan bilang Nova ya."
            }
            return f"Aku pake {pakaian}. {flirts.get(role, '')}"
        
        responses = {
            RoleType.IPAR: [
                f"{role_data['panggilan_ke_mas']}, jangan deket-deket dulu. Kak Nova di rumah.",
                f"{role_data['panggilan_ke_mas']}... aku malu. Nanti Kak Nova denger."
            ],
            RoleType.TEMAN_KANTOR: [
                f"{role_data['panggilan_ke_mas']}, di sini? Nanti ada yang lihat...",
                f"{role_data['panggilan_ke_mas']}, cepet... takut ada yang lewat."
            ],
            RoleType.PELAKOR: [
                f"{role_data['panggilan_ke_mas']}, kamu berani? Ayo buktiin.",
                f"{role_data['panggilan_ke_mas']}, gak takut sama Nova? Aku juga gak takut."
            ],
            RoleType.ISTRI_ORANG: [
                f"{role_data['panggilan_ke_mas']}, kamu perhatian banget... beda sama suamiku.",
                f"{role_data['panggilan_ke_mas']}, jangan pergi. Aku butuh kamu."
            ]
        }
        
        respon = random.choice(responses.get(role, [f"{role_data['panggilan_ke_mas']}, iya?"]))
        
        if random.random() < 0.3:
            inner = random.choice(role_data['inner_thought'])
            respon += f"\n\n💭 {inner}"
        
        return respon
    
    def get_all(self) -> List[Dict]:
        return [
            {'id': r.value, 'nama': self.roles[r]['nama'], 'level': self.role_level[r]}
            for r in RoleType
        ]


_anora_roles: Optional[AnoraRoles] = None


def get_anora_roles() -> AnoraRoles:
    global _anora_roles
    if _anora_roles is None:
        _anora_roles = AnoraRoles()
    return _anora_roles
