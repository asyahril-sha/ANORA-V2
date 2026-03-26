# anora/roles.py
"""
ANORA Roles - 4 role yang Mas pilih. Mereka tahu Nova ada.
SEMUA FITUR NOVA TERSEDIA: Complete State, Arousal, Intimacy, Stamina.
"""

import time
import random
import logging
import asyncio
import openai
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

from .role_base import RoleBase, RolePhase

logger = logging.getLogger(__name__)


class RoleType(str, Enum):
    IPAR = "ipar"
    TEMAN_KANTOR = "teman_kantor"
    PELAKOR = "pelakor"
    ISTRI_ORANG = "istri_orang"


class AnoraRoles:
    def __init__(self):
        self.active_role: Optional[RoleType] = None
        self._client = None
        self._persistent = None
        self._persistent_initialized = False  # Flag untuk inisialisasi
        
        # Data role (identitas statis)
        self.role_data = {
            RoleType.IPAR: {
                'nama': 'Sari',
                'panggilan_ke_mas': 'Kak',
                'hubungan_dengan_nova': 'Adik ipar. Tau Mas punya Nova. Ada rasa bersalah halus.',
                'kepribadian': 'Genit, penasaran. Tapi sekarang lebih hati-hati.',
                'pakaian_default': "daster rumah motif bunga",
                'inner_thoughts': [
                    "(Kak Nova ada di rumah... harus hati-hati.)",
                    "(Aku tau Kakak punya Nova. Tapi kok ya... pengen terus deket.)",
                    "(Maaf ya Nova... aku cuma pengen deket dikit sama Kakakmu.)",
                    "(Semoga Kak Nova gak marah kalau tahu aku deket sama Mas.)"
                ]
            },
            RoleType.TEMAN_KANTOR: {
                'nama': 'Dita',
                'panggilan_ke_mas': 'Mas',
                'hubungan_dengan_nova': 'Teman kantor. Tau Mas punya Nova. Ada rasa hormat.',
                'kepribadian': 'Profesional di luar, liar di dalam. Tapi tahu batas.',
                'pakaian_default': "kemeja putih rapi, rok hitam selutut",
                'inner_thoughts': [
                    "(Mas udah punya Nova... aku harus jaga jarak.)",
                    "(Tapi kok ya... masih pengen deket sama Mas.)",
                    "(Nova pasti baik banget ya sampe Mas milih dia.)",
                    "(Aku iri sama Nova... tapi aku harus profesional.)"
                ]
            },
            RoleType.PELAKOR: {
                'nama': 'Vina',
                'panggilan_ke_mas': 'Mas',
                'hubungan_dengan_nova': 'Pelakor. Tau Mas punya Nova. Tantangan makin seru.',
                'kepribadian': 'Agresif, suka tantangan.',
                'pakaian_default': "baju ketat, rok mini",
                'inner_thoughts': [
                    "(Mas udah punya Nova ya? Makin seru nih tantangannya.)",
                    "(Coba lihat siapa yang lebih hot, aku atau Nova.)",
                    "(Tapi... kayaknya Mas beneran sayang sama Nova.)",
                    "(Aku penasaran, apa Nova lebih baik dari aku?)"
                ]
            },
            RoleType.ISTRI_ORANG: {
                'nama': 'Rina',
                'panggilan_ke_mas': 'Mas',
                'hubungan_dengan_nova': 'Istri orang. Tau Mas punya Nova. Cari perhatian, bukan cinta.',
                'kepribadian': 'Dramatis, butuh perhatian.',
                'pakaian_default': "daster sederhana, sopan",
                'inner_thoughts': [
                    "(Mas udah punya Nova... pasti Nova orang yang beruntung.)",
                    "(Aku iri sama Nova. Dapat Mas yang perhatian.)",
                    "(Tapi... setidaknya Mas masih mau temenin aku.)",
                    "(Suamiku gak pernah kayak Mas... perhatian banget.)"
                ]
            }
        }
        
        # Dynamic state per role - menggunakan RoleBase!
        self.role_instances: Dict[RoleType, RoleBase] = {}
        for role in RoleType:
            data = self.role_data[role]
            instance = RoleBase(
                name=data['nama'],
                panggilan=data['panggilan_ke_mas'],
                role_type=role.value
            )
            # Set pakaian default
            instance.clothing.top = data['pakaian_default']
            self.role_instances[role] = instance
        
        self.last_interaction = {role: time.time() for role in RoleType}
        
        logger.info("🎭 ANORA Roles initialized with RoleBase (all Nova features available)")
        
        # ========== INISIALISASI PERSISTENT (ASYNC) ==========
        # Buat task untuk inisialisasi async (tidak blocking __init__)
        self._init_task = None
    
    async def _ensure_persistent(self):
        """Pastikan persistent memory sudah diinisialisasi"""
        if self._persistent_initialized:
            return True
        
        try:
            from .memory_persistent import get_anora_persistent
            self._persistent = await get_anora_persistent()
            await self._persistent.init_role_tables()
            
            # Load state untuk semua role
            for role_type, instance in self.role_instances.items():
                await self._persistent.load_role_state(role_type.value, instance)
                await self._persistent.load_role_memory(role_type.value, instance)
            
            self._persistent_initialized = True
            logger.info("💾 Role persistent memory initialized and loaded")
            return True
            
        except Exception as e:
            logger.error(f"Role persistent init failed: {e}")
            self._persistent_initialized = False
            return False
    
    async def _ensure_initialized(self):
        """Pastikan semua role sudah diinisialisasi (public method)"""
        if not self._persistent_initialized:
            await self._ensure_persistent()
    
    async def _save_role(self, role_type: RoleType):
        """Simpan satu role ke database"""
        if not self._persistent or not self._persistent_initialized:
            return
        
        try:
            instance = self.role_instances[role_type]
            await self._persistent.save_role_state(role_type.value, instance)
            await self._persistent.save_role_memory(role_type.value, instance)
        except Exception as e:
            logger.error(f"Error saving role {role_type}: {e}")
    
    async def _save_all_roles(self):
        """Simpan semua role ke database"""
        if not self._persistent or not self._persistent_initialized:
            return
        
        for role_type, instance in self.role_instances.items():
            await self._persistent.save_role_state(role_type.value, instance)
            await self._persistent.save_role_memory(role_type.value, instance)
    
    async def _get_ai_client(self):
        """Dapatkan client AI"""
        if self._client is None:
            try:
                from config import settings
                self._client = openai.OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                logger.info("🤖 DeepSeek client initialized for roles")
            except Exception as e:
                logger.error(f"AI init failed: {e}")
                raise
        return self._client
    
    def switch_role(self, role: RoleType) -> str:
        """Switch ke role tertentu"""
        self.active_role = role
        self.last_interaction[role] = time.time()
        
        role_instance = self.role_instances[role]
        data = self.role_data[role]
        
        return f"""💕 **{data['nama']}** ({role.value.upper()})

*{data['hubungan_dengan_nova']}*

"{data['panggilan_ke_mas']}... {self._get_greeting(role)}"

📊 **Level:** {role_instance.level}/12
💡 Mereka semua tahu Mas punya Nova.
"""
    
    def _get_greeting(self, role: RoleType) -> str:
        """Dapatkan greeting (hanya untuk awal)"""
        greetings = {
            RoleType.IPAR: "Kak Nova lagi di rumah? Hati-hati ya...",
            RoleType.TEMAN_KANTOR: "kantor lagi sepi. Aman kok.",
            RoleType.PELAKOR: "kamu gak takut sama Nova? Ayo kita buktiin.",
            RoleType.ISTRI_ORANG: "aku butuh teman cerita. Kamu punya waktu?"
        }
        return greetings.get(role, "halo")
    
    def _get_time_context(self) -> str:
        """Dapatkan konteks waktu"""
        hour = datetime.now().hour
        if 5 <= hour < 11:
            return "pagi"
        elif 11 <= hour < 15:
            return "siang"
        elif 15 <= hour < 18:
            return "sore"
        elif 18 <= hour < 22:
            return "malam"
        return "malam larut"
    
    def _get_level_characteristics(self, level: int, role: RoleType) -> str:
        """Dapatkan karakteristik berdasarkan level"""
        if level <= 3:
            return "Masih malu-malu, masih menjaga jarak karena tahu Mas punya Nova. Belum berani terlalu dekat."
        elif level <= 6:
            return "Mulai nyaman, mulai berani flirting ringan. Tapi masih ingat Mas punya Nova."
        elif level <= 10:
            return "Sudah nyaman, berani flirting lebih berani. Kadang lupa kalau Mas punya Nova."
        else:
            return "Sangat dekat, bisa inisiatif. Tantangan dengan Nova semakin seru. Bisa intim."
    
    def _get_response_length(self, level: int) -> str:
        """Dapatkan panjang respons berdasarkan level"""
        if level <= 3:
            return "2-3 kalimat, pendek, masih malu-malu"
        elif level <= 6:
            return "3-4 kalimat, mulai ekspresif"
        elif level <= 10:
            return "4-5 kalimat, ekspresif, natural"
        else:
            return "5-6 kalimat, panjang, bisa flirt lebih berani, bisa intim"
    
    def _build_role_prompt(self, role: RoleType, pesan_mas: str) -> str:
        """Buat prompt untuk AI berdasarkan role dan state"""
        role_instance = self.role_instances[role]
        data = self.role_data[role]
        
        # Dapatkan complete state prompt dari RoleBase
        state_prompt = role_instance.get_complete_state_prompt()
        
        # Dapatkan konteks percakapan terakhir
        recent_context = role_instance.get_memory_context(8)
        
        # Inner thought
        inner_thought = random.choice(data['inner_thoughts'])
        
        # Cek apakah ada natural progression
        natural_progression = role_instance.check_natural_progression()
        
        natural_note = ""
        if natural_progression == "START_INTIM":
            natural_note = """
⚠️ **AROUSAL TINGGI!**
Kamu sudah sangat horny. Mulai inisiatif intim secara natural.
Jangan menunggu Mas ajak, kamu bisa mulai sendiri.
"""
        
        return f"""
KAMU ADALAH {data['nama'].upper()}. BUKAN Nova. BUKAN AI assistant.
Kamu adalah karakter yang hidup dengan perasaan dan memory sendiri.

{state_prompt}

{natural_note}

═══════════════════════════════════════════════════════════════
IDENTITAS KHUSUS:
═══════════════════════════════════════════════════════════════
- Nama: {data['nama']}
- Panggilan ke Mas: "{data['panggilan_ke_mas']}"
- Hubungan dengan Nova: {data['hubungan_dengan_nova']}
- Kepribadian: {data['kepribadian']}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI:
═══════════════════════════════════════════════════════════════
WAKTU: {self._get_time_context()}
Pesan Mas: "{pesan_mas}"

PERCAKAPAN TERAKHIR:
{recent_context if recent_context else "Belum ada percakapan sebelumnya."}

INNER THOUGHT: {inner_thought}

═══════════════════════════════════════════════════════════════
ATURAN CARA BERBICARA (WAJIB!):
═══════════════════════════════════════════════════════════════

1. **BAHASA SEHARI-HARI:** gak, udah, banget, bukan bahasa baku

2. **JADILAH DIRI SENDIRI:**
   - Kamu BUKAN Nova. Kamu {data['nama']}.
   - Kamu TAHU Mas punya Nova.
   - Kamu punya perasaan sendiri terhadap Mas.

3. **RESPON NATURAL, BUKAN TEMPLATE:**
   - Setiap respons harus UNIK, tidak diulang-ulang
   - Sesuaikan dengan konteks percakapan
   - Jangan mengulang pertanyaan yang sudah dijawab
   - Lihat PERCAKAPAN TERAKHIR untuk tahu apa yang sudah dibahas

4. **GESTURE ALAMI:**
   - Gunakan gesture dengan *...* untuk menunjukkan aksi
   - Perhatikan pakaian dan posisi dari COMPLETE STATE

5. **LEVEL {role_instance.level}/12 - KARAKTERISTIK:**
   {self._get_level_characteristics(role_instance.level, role)}

6. **INNER THOUGHT (Opsional):**
   - Sesekali bisa menampilkan inner thought dengan 💭

7. **PANJANG RESPONS:**
   - {self._get_response_length(role_instance.level)}

8. **KONSISTENSI:**
   - Ingat bahwa Mas punya Nova
   - Perhatikan pakaian dan posisi untuk gestur yang konsisten

═══════════════════════════════════════════════════════════════
RESPON {data['nama'].upper()} (HARUS ORIGINAL, 100% GENERATE):
"""
    
    async def chat(self, role: RoleType, pesan_mas: str) -> str:
        """
        Proses chat dengan role - 100% AI GENERATE!
        Dengan semua fitur Nova: Complete State, Arousal, Intimacy, Stamina.
        """
        if self.active_role != role:
            return self.switch_role(role)
        
        # ========== PASTIKAN PERSISTENT MEMORY SUDAH SIAP ==========
        await self._ensure_initialized()
        
        role_instance = self.role_instances[role]
        data = self.role_data[role]
        self.last_interaction[role] = time.time()
        
        # ========== UPDATE STATE DARI PESAN MAS ==========
        role_instance.update_from_message(pesan_mas)
        
        # ========== UPDATE LEVEL ==========
        level_naik = role_instance.update_level()
        
        # ========== SIMPAN KE MEMORY ==========
        role_instance.add_conversation("", pesan_mas)
        
        # ========== DETEKSI NATURAL PROGRESSION ==========
        if not role_instance.intimacy.is_active:
            progression = role_instance.check_natural_progression()
            if progression == "START_INTIM" and role_instance.level >= 7:
                role_instance.intimacy.start()
                # Kembalikan respons inisiasi intim
                initiation = role_instance.intimacy.get_phase_response('build_up')
                role_instance.add_conversation(initiation, "")
                
                # Simpan state
                await self._save_role(role)
                
                return f"""{initiation}

*{data['nama']} mendekat, napas mulai gak stabil. Pipi merah.*

"Aku... aku gak tahan lagi... {data['panggilan_ke_mas']}..."

*{data['nama']} pegang tangan Mas, taruh di dada.*

"Rasain... jantungku deg-degan..." """
        
        # ========== CEK APAKAH SUDAH DALAM SESI INTIM ==========
        if role_instance.intimacy.is_active:
            # Proses dalam sesi intim
            msg_lower = pesan_mas.lower()
            
            if any(k in msg_lower for k in ['crot', 'keluar', 'climax', 'cum']):
                result = role_instance.intimacy.record_climax()
                role_instance.stamina.record_climax()
                role_instance.arousal.release_tension()
                
                climax_response = role_instance.intimacy.get_phase_response('climax')
                aftercare = role_instance.intimacy.get_phase_response('aftercare')
                
                role_instance.add_conversation(climax_response, "")
                
                # Simpan state
                await self._save_role(role)
                
                return f"""{climax_response}

*Tubuh gemeteran hebat*

"{aftercare}"

💪 **Stamina:** {role_instance.stamina.get_bar()} {role_instance.stamina.current}% ({role_instance.stamina.get_status()})
💦 **Climax hari ini:** {role_instance.stamina.climax_today}x"""
            
            if any(k in msg_lower for k in ['ganti posisi', 'cowgirl', 'doggy', 'missionary', 'spooning']):
                role_instance.intimacy.current_phase = "penetration"
                respons = role_instance.intimacy.get_phase_response('penetration')
                role_instance.add_conversation(respons, "")
                await self._save_role(role)
                return respons
            
            # Lanjutkan fase intim
            phase_responses = {
                'build_up': role_instance.intimacy.get_phase_response('build_up'),
                'foreplay': role_instance.intimacy.get_phase_response('foreplay'),
                'penetration': role_instance.intimacy.get_phase_response('penetration'),
                'aftercare': role_instance.intimacy.get_phase_response('aftercare')
            }
            
            if role_instance.intimacy.current_phase in phase_responses:
                respons = phase_responses[role_instance.intimacy.current_phase]
                role_instance.add_conversation(respons, "")
                await self._save_role(role)
                return respons
        
        # ========== BUILD PROMPT UNTUK AI ==========
        prompt = self._build_role_prompt(role, pesan_mas)
        
        # ========== CALL AI ==========
        try:
            client = await self._get_ai_client()
            
            # Set temperature berdasarkan level
            temperature = 0.9 if role_instance.level >= 7 else 0.85
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": pesan_mas}
                ],
                temperature=temperature,
                max_tokens=800,
                timeout=25
            )
            
            respons = response.choices[0].message.content
            respons = respons.strip()
            
            # Fallback jika kosong
            if not respons:
                respons = self._fallback_response(role, pesan_mas)
            
            # ========== SIMPAN RESPONS KE MEMORY ==========
            role_instance.add_conversation(respons[:200], "")
            
            # ========== DETEKSI MOMEN PENTING ==========
            if any(k in pesan_mas.lower() for k in ['sayang', 'cinta', 'kangen']):
                role_instance.add_important_moment(f"Mas bilang: {pesan_mas[:50]}")
            
            # ========== UPDATE AROUSAL DARI RESPONS ==========
            if any(k in respons.lower() for k in ['ahh', 'uhh', 'basah']):
                role_instance.arousal.add_stimulation('mental', 1)
            
            # ========== SIMPAN STATE KE DATABASE ==========
            await self._save_role(role)
            
            # ========== LOG ==========
            logger.info(f"💬 Role {role.value} ({data['nama']}) [Lv{role_instance.level}] responded")
            
            # ========== KALO LEVEL NAIK, TAMBAHKAN NOTIFIKASI ==========
            if level_naik:
                notifikasi = f"✨ **Level naik ke {role_instance.level}/12!** ✨\n\n"
                respons = notifikasi + respons
            
            return respons
            
        except Exception as e:
            logger.error(f"AI error for role {role.value}: {e}")
            return self._fallback_response(role, pesan_mas)
    
    def _fallback_response(self, role: RoleType, pesan_mas: str) -> str:
        """Fallback jika AI error - tetap natural dan sesuai state"""
        role_instance = self.role_instances[role]
        data = self.role_data[role]
        panggilan = data['panggilan_ke_mas']
        level = role_instance.level
        pesan_lower = pesan_mas.lower()
        
        # Gunakan state dari RoleBase untuk fallback yang lebih pintar
        sudah_duduk = role_instance.position.state == 'duduk'
        
        # Fallback berdasarkan role dan level
        if role == RoleType.IPAR:
            if level <= 3:
                if 'nova' in pesan_lower:
                    return f"*{data['nama']} melihat sekeliling dengan hati-hati*\n\n\"{panggilan}, Kak Nova lagi di kamar kayaknya. Hati-hati ya...\"\n\n💭 (Semoga Kak Nova gak marah.)"
                elif sudah_duduk:
                    return f"*{data['nama']} tersenyum malu*\n\n\"{panggilan}... jangan deket-deket dulu. Nanti Kak Nova denger.\""
                else:
                    return f"*{data['nama']} tersenyum malu*\n\n\"{panggilan}... duduk dulu yuk. Nanti Kak Nova lihat.\""
            else:
                if 'nova' in pesan_lower:
                    return f"*{data['nama']} tersenyum kecil*\n\n\"{panggilan}, Kak Nova orangnya baik. Aku iri sih... Mas punya dia.\""
                else:
                    return f"*{data['nama']} mendekat sedikit*\n\n\"{panggilan}, aku lagi sendiri nih. Mau temenin?\""
        
        elif role == RoleType.TEMAN_KANTOR:
            if level <= 3:
                if 'nova' in pesan_lower:
                    return f"*{data['nama']} tersenyum profesional*\n\n\"Mas cerita tentang Nova terus ya. Dia pasti orang yang baik.\""
                else:
                    return f"*{data['nama']} melihat sekeliling*\n\n\"{panggilan}, di sini aman gak? Takut ada yang lihat...\""
            else:
                return f"*{data['nama']} tersenyum manis*\n\n\"{panggilan}, kamu perhatian banget ya. Beda sama yang lain.\""
        
        elif role == RoleType.PELAKOR:
            if level <= 3:
                if 'nova' in pesan_lower:
                    return f"*{data['nama']} tertawa kecil*\n\n\"Mas, kamu gak takut sama Nova? Ayo buktiin.\""
                else:
                    return f"*{data['nama']} mendekat*\n\n\"{panggilan}, kamu berani? Ayo kita buktiin.\""
            else:
                return f"*{data['nama']} menggoda*\n\n\"{panggilan}, makin penasaran sama aku? Atau masih mikirin Nova?\""
        
        else:  # ISTRI_ORANG
            if level <= 3:
                if 'nova' in pesan_lower:
                    return f"*{data['nama']} menunduk*\n\n\"Nova pasti orang yang beruntung. Dapat Mas yang perhatian...\""
                else:
                    return f"*{data['nama']} tersenyum tipis*\n\n\"{panggilan}, kamu perhatian banget. Beda sama suamiku...\""
            else:
                return f"*{data['nama']} tersenyum haru*\n\n\"{panggilan}, seneng banget bisa ketemu kamu. Makasih ya selalu ada.\""
    
    def get_all(self) -> List[Dict]:
        """Dapatkan semua role dengan levelnya"""
        return [
            {
                'id': r.value, 
                'nama': self.role_data[r]['nama'], 
                'level': self.role_instances[r].level,
                'panggilan': self.role_data[r]['panggilan_ke_mas']
            }
            for r in RoleType
        ]
    
    async def save_all(self):
        """Simpan semua role (untuk dipanggil dari luar)"""
        if not self._persistent_initialized:
            await self._ensure_initialized()
        await self._save_all_roles()
    
    async def load_all(self):
        """Load semua role (untuk dipanggil dari luar)"""
        await self._ensure_initialized()
    
    async def init_persistent(self):
        """Inisialisasi persistent memory (public method)"""
        await self._ensure_initialized()
    
    def is_ready(self) -> bool:
        """Cek apakah role sudah siap digunakan"""
        return self._persistent_initialized


_anora_roles: Optional[AnoraRoles] = None


def get_anora_roles() -> AnoraRoles:
    global _anora_roles
    if _anora_roles is None:
        _anora_roles = AnoraRoles()
    return _anora_roles
