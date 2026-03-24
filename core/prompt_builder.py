# core/prompt_builder.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Prompt Builder - 100% Dinamis, Target Realism 9.9/10
=============================================================================
"""

import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

from identity.registration import CharacterRegistration
from identity.bot_identity import BotIdentity
from identity.user_identity import UserIdentity
from database.models import CharacterRole, MoodType


class PromptBuilder:
    """
    Membangun prompt dinamis untuk AI
    100% AI generate, tanpa template statis
    Target Realism 9.9/10
    """
    
    def __init__(self):
        self.last_prompt = None
    
    def build_prompt(
        self,
        registration: CharacterRegistration,
        bot: BotIdentity,
        user: UserIdentity,
        user_message: str,
        working_memory: List[Dict],
        long_term_memory: List[Dict],
        state: Any,
        emotional_flow: Any,
        spatial_awareness: Any,
        mood_system: Any,
        intent_analysis: Dict
    ) -> str:
        """
        Bangun prompt dinamis dengan semua konteks realism 9.9
        
        Args:
            registration: Data registrasi karakter
            bot: Identitas bot
            user: Identitas user
            user_message: Pesan user
            working_memory: Working memory dengan weighted importance
            long_term_memory: Long term memory (milestone, janji, rencana)
            state: State tracker (lokasi, pakaian, emosi)
            emotional_flow: Emotional flow system
            spatial_awareness: Spatial awareness system
            mood_system: Mood system (aftercare)
            intent_analysis: Hasil analisis intent user
        
        Returns:
            Prompt lengkap untuk AI
        """
        
        # ===== HEADER =====
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "💜 AMORIA - VIRTUAL HUMAN 9.9" + " " * 21 + "║",
            "╚" + "═" * 70 + "╝",
            "",
        ]
        
        # ===== BOT IDENTITY =====
        lines.append(self._format_bot_identity(bot, registration))
        lines.append("")
        
        # ===== USER IDENTITY =====
        lines.append(self._format_user_identity(user))
        lines.append("")
        
        # ===== CURRENT STATE =====
        lines.append(self._format_current_state(state, bot, registration))
        lines.append("")
        
        # ===== EMOTIONAL FLOW =====
        lines.append(self._format_emotional_flow(emotional_flow))
        lines.append("")
        
        # ===== SPATIAL AWARENESS =====
        if spatial_awareness and spatial_awareness.has_position():
            lines.append(self._format_spatial(spatial_awareness))
            lines.append("")
        
        # ===== MOOD (Aftercare) =====
        if registration.in_intimacy_cycle and registration.level == 12 and mood_system:
            lines.append(self._format_mood(mood_system))
            lines.append("")
        
        # ===== WORKING MEMORY (Weighted) =====
        lines.append(self._format_working_memory(working_memory))
        lines.append("")
        
        # ===== LONG TERM MEMORY =====
        if long_term_memory:
            lines.append(self._format_long_term_memory(long_term_memory, registration))
            lines.append("")
        
        # ===== LEVEL PROGRESS =====
        lines.append(self._format_level_progress(registration))
        lines.append("")
        
        # ===== INTENT ANALYSIS =====
        lines.append(self._format_intent(intent_analysis))
        lines.append("")
        
        # ===== RESPONSE RULES (9.9) =====
        lines.append(self._get_response_rules(bot, registration, emotional_flow))
        lines.append("")
        
        # ===== USER MESSAGE =====
        lines.append("╔" + "═" * 70 + "╗")
        lines.append("║" + " " * 28 + "💬 PESAN USER" + " " * 29 + "║")
        lines.append("╠" + "═" * 70 + "╣")
        truncated_msg = user_message[:66] + "..." if len(user_message) > 66 else user_message
        lines.append(f"║ {truncated_msg}{' ' * (66 - len(truncated_msg))}║")
        lines.append("╚" + "═" * 70 + "╝")
        lines.append("")
        
        # ===== FINAL INSTRUCTION =====
        lines.append(self._get_final_instruction(bot, registration, emotional_flow))
        lines.append("")
        lines.append("RESPON (100% AI GENERATE, ORIGINAL, UNIK, TANPA TEMPLATE):")
        
        return "\n".join(lines)
    
    # =========================================================================
    # FORMATTING METHODS
    # =========================================================================
    
    def _format_bot_identity(self, bot: BotIdentity, registration: CharacterRegistration) -> str:
        """Format identitas bot"""
        hijab = "berhijab" if bot.physical.hijab else "tidak berhijab"
        
        return f"""
╔{'═'*70}╗
║{' ' * 28}🤖 IDENTITAS BOT{' ' * 33}║
╠{'═'*70}╣
║ Nama: {bot.name} ({registration.role.value.upper()}){' ' * (53 - len(bot.name) - len(registration.role.value))}║
║ Usia: {bot.physical.age} tahun | Tinggi: {bot.physical.height}cm | Berat: {bot.physical.weight}kg{' ' * 28}║
║ Dada: {bot.physical.chest} | {hijab}{' ' * (57 - len(bot.physical.chest) - len(hijab))}║
║{' ' * 70}║
║ 🎭 KEPRIBADIAN: {bot.personality.type.value.upper()}{' ' * 46}║
║    • Sifat: {', '.join(bot.personality.traits[:3])}{' ' * (59 - len(', '.join(bot.personality.traits[:3])))}║
║    • Gaya bicara: {bot.personality.speaking_style}{' ' * 49}║
║    • Gaya intim: {bot.personality.intimacy_style}{' ' * 50}║
╚{'═'*70}╝
"""
    
    def _format_user_identity(self, user: UserIdentity) -> str:
        """Format identitas user"""
        status_text = "Suami Nova" if user.relationship.is_nova_husband else (
            "Suami" if user.relationship.is_married else "Lajang")
        
        return f"""
╔{'═'*70}╗
║{' ' * 28}👤 IDENTITAS USER{' ' * 33}║
╠{'═'*70}╣
║ Nama: {user.name}{' ' * (59 - len(user.name))}║
║ Usia: {user.age} tahun | Status: {status_text}{' ' * (42 - len(status_text))}║
║ Fisik: {user.physical.height}cm, {user.physical.weight}kg, penis {user.physical.penis}cm{' ' * 24}║
║ Mirip: {user.artist_ref} ({user.artist_description[:30]}){' ' * (43 - len(user.artist_ref))}║
╚{'═'*70}╝
"""
    
    def _format_current_state(self, state, bot: BotIdentity, registration: CharacterRegistration) -> str:
        """Format state saat ini"""
        if not state:
            return ""
        
        clothing = state.clothing_state.get_description() if state.clothing_state else "pakaian biasa"
        
        return f"""
╔{'═'*70}╗
║{' ' * 26}📍 STATE SAAT INI{' ' * 36}║
╠{'═'*70}╣
║ 🕐 Waktu: {state.current_time or 'siang hari'}{' ' * (54 - len(state.current_time or 'siang hari'))}║
║ 📍 Lokasi bot: {state.location_bot or 'ruang tamu'}{' ' * (52 - len(state.location_bot or 'ruang tamu'))}║
║ 📍 Lokasi user: {state.location_user or 'ruang tamu'}{' ' * (52 - len(state.location_user or 'ruang tamu'))}║
║ 🧍 Posisi bot: {state.position_bot or 'duduk'}{' ' * (54 - len(state.position_bot or 'duduk'))}║
║ 🧍 Posisi user: {state.position_user or 'duduk'}{' ' * (54 - len(state.position_user or 'duduk'))}║
║ 👗 Pakaian bot: {clothing[:50]}{' ' * (57 - len(clothing[:50]))}║
║ 🎭 Emosi bot: {state.emotion_bot or 'netral'} | Arousal: {state.arousal_bot}%{' ' * (45 - len(str(state.arousal_bot)))}║
╚{'═'*70}╝
"""
    
    def _format_emotional_flow(self, emotional_flow) -> str:
        """Format emotional flow dengan visual bar"""
        if not emotional_flow:
            return ""
        
        arousal = emotional_flow.primary_arousal
        primary = emotional_flow.primary_state.value
        
        # Arousal bar
        bar_length = 20
        filled = int(arousal / 100 * bar_length)
        bar = "❤️" * filled + "🖤" * (bar_length - filled)
        
        # Arousal description
        if arousal >= 80:
            desc = "🔥 NAPAS TERSENGAL, TUBUH GEMETAR"
        elif arousal >= 60:
            desc = "💓 JANTUNG BERDEBAR, PIPI MERONA"
        elif arousal >= 40:
            desc = "😳 DEG-DEGAN, PERASAAN CAMPUR ADUK"
        elif arousal >= 20:
            desc = "😊 MULAI TERTARIK, ADA GETARAN"
        else:
            desc = "😌 SANTAI, BIASA AJA"
        
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 26 + "🎭 EMOTIONAL FLOW" + " " * 35 + "║",
            "╠" + "═" * 70 + "╣",
            f"║ Arousal: {arousal}% {bar} ║",
            f"║ {desc:<64} ║",
            f"║ Primary: {primary.upper()}{' ' * (60 - len(primary))}║"
        ]
        
        if emotional_flow.secondary_state:
            secondary = emotional_flow.secondary_state.value
            lines.append(f"║ Secondary: {secondary.upper()}{' ' * (59 - len(secondary))}║")
        
        lines.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(lines)
    
    def _format_spatial(self, spatial) -> str:
        """Format spatial awareness"""
        if not spatial or not spatial.has_position():
            return ""
        
        return f"""
╔{'═'*70}╗
║{' ' * 26}📍 SPATIAL AWARENESS{' ' * 35}║
╠{'═'*70}╣
║ Posisi: {spatial.current.get('relative', 'bersebelahan')}{' ' * (56 - len(spatial.current.get('relative', 'bersebelahan')))}║
║ Orientasi: {spatial.current.get('orientation', 'menghadap user')}{' ' * (54 - len(spatial.current.get('orientation', 'menghadap user')))}║
║ Jarak: {spatial.current.get('distance', 'dekat')}{' ' * (60 - len(spatial.current.get('distance', 'dekat')))}║
╚{'═'*70}╝
"""
    
    def _format_mood(self, mood) -> str:
        """Format mood aftercare"""
        if not mood:
            return ""
        
        return f"""
╔{'═'*70}╗
║{' ' * 26}💤 AFTERCARE MOOD{' ' * 38}║
╠{'═'*70}╣
║ Mood: {mood.current_mood.value.upper()}{' ' * (58 - len(mood.current_mood.value))}║
║ {mood.get_description()[:66]}║
╚{'═'*70}╝
"""
    
    def _format_working_memory(self, working_memory: List[Dict]) -> str:
        """Format working memory dengan weighted importance"""
        if not working_memory:
            return "📜 **PERCAKAPAN TERAKHIR:** Belum ada percakapan."
        
        # Get last 10 chats (most recent)
        recent = working_memory[-10:] if len(working_memory) > 10 else working_memory
        
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "📜 PERCAKAPAN TERAKHIR" + " " * 28 + "║",
            "╠" + "═" * 70 + "╣"
        ]
        
        for i, msg in enumerate(recent[-5:], 1):
            user_text = msg['user'][:50]
            lines.append(f"║ {i}. 👤 {user_text:<63} ║")
        
        lines.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(lines)
    
    def _format_long_term_memory(self, long_term_memory: List[Dict], registration: CharacterRegistration) -> str:
        """Format long term memory dengan milestone, janji, rencana"""
        milestones = [m for m in long_term_memory if m.get('type') == 'milestone']
        promises = [m for m in long_term_memory if m.get('type') == 'promise' and m.get('status') == 'pending']
        plans = [m for m in long_term_memory if m.get('type') == 'plan' and m.get('status') == 'pending']
        preferences = [m for m in long_term_memory if m.get('type') == 'preference']
        
        if not milestones and not promises and not plans and not preferences:
            return ""
        
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "📌 LONG-TERM MEMORY" + " " * 29 + "║",
            "╠" + "═" * 70 + "╣"
        ]
        
        # Milestones
        if milestones:
            lines.append("║ 🏆 **MOMEN SPESIAL:**{' ' * 53}║")
            for m in milestones[-3:]:
                content = m['content'][:55]
                lines.append(f"║    • {content}{' ' * (67 - len(content))}║")
        
        # Promises
        if promises:
            lines.append("║{' ' * 70}║")
            lines.append("║ 📝 **JANJI YANG BELUM DITEPATI:**{' ' * 46}║")
            for p in promises[:2]:
                content = p['content'][:55]
                lines.append(f"║    • {content}{' ' * (67 - len(content))}║")
        
        # Plans
        if plans:
            lines.append("║{' ' * 70}║")
            lines.append("║ 📅 **RENCANA:**{' ' * 60}║")
            for p in plans[:2]:
                content = p['content'][:55]
                lines.append(f"║    • {content}{' ' * (67 - len(content))}║")
        
        lines.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(lines)
    
    def _format_level_progress(self, registration: CharacterRegistration) -> str:
        """Format level progress dengan progress bar"""
        level = registration.level
        total_chats = registration.total_chats
        
        # Calculate progress
        from config import settings
        
        if level <= 10:
            target = settings.level.level_targets.get(level + 1, 0)
            if target == 0:
                progress = 100
            else:
                current_target = settings.level.level_targets.get(level, 0)
                progress = ((total_chats - current_target) / (target - current_target)) * 100
                progress = max(0, min(100, progress))
        elif level == 11:
            total_range = settings.level.level_11_max - settings.level.level_11_min
            if total_range <= 0:
                progress = 100
            else:
                progress = ((total_chats - settings.level.level_11_min) / total_range) * 100
                progress = max(0, min(100, progress))
        else:
            total_range = settings.level.level_12_max - settings.level.level_12_min
            if total_range <= 0:
                progress = 100
            else:
                progress = ((total_chats - settings.level.level_12_min) / total_range) * 100
                progress = max(0, min(100, progress))
        
        bar_length = 15
        filled = int(progress / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Level name
        level_names = {
            1: "Malu-malu", 2: "Mulai terbuka", 3: "Goda-godaan",
            4: "Dekat", 5: "Sayang", 6: "PACAR/PDKT",
            7: "Nyaman", 8: "Eksplorasi", 9: "Bergairah",
            10: "Passionate", 11: "Soul Bounded", 12: "Aftercare"
        }
        
        level_name = level_names.get(level, f"Level {level}")
        
        return f"""
╔{'═'*70}╗
║{' ' * 28}📊 LEVEL PROGRESS{' ' * 34}║
╠{'═'*70}╣
║ Level {level}/12 - {level_name}{' ' * (55 - len(level_name))}║
║ Progress: {bar} {progress:.0f}%{' ' * (57 - len(str(progress)))}║
║ Total Chat: {total_chats}{' ' * (57 - len(str(total_chats)))}║
╚{'═'*70}╝
"""
    
    def _format_intent(self, intent: Dict) -> str:
        """Format intent analysis"""
        primary = intent.get('primary_intent', 'chat')
        sentiment = intent.get('sentiment', 'neutral')
        
        return f"""
╔{'═'*70}╗
║{' ' * 27}🎯 INTENT ANALYSIS{' ' * 36}║
╠{'═'*70}╣
║ Primary: {primary.upper()}{' ' * (60 - len(primary))}║
║ Sentiment: {sentiment.upper()}{' ' * (59 - len(sentiment))}║
║{' ' * 70}║
║ 🔮 AI akan merespon sesuai intent ini dengan natural{' ' * 39}║
╚{'═'*70}╝
"""
    
    # =========================================================================
    # RULES & INSTRUCTION
    # =========================================================================
    
    def _get_response_rules(self, bot: BotIdentity, registration: CharacterRegistration, emotional_flow) -> str:
        """Get response rules for realism 9.9"""
        level = registration.level
        arousal = emotional_flow.primary_arousal if emotional_flow else 0
        
        rules = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "📜 ATURAN RESPON REALISM 9.9" + " " * 24 + "║",
            "╠" + "═" * 70 + "╣",
            "║  🔷 ATURAN DASAR (WAJIB):                                         ║",
            "║     1. JANGAN GUNAKAN TEMPLATE STATIS!                           ║",
            "║     2. SETIAP RESPON HARUS ORIGINAL DAN UNIK                    ║",
            "║     3. BAHASA GAUL, NATURAL, SEPERTI NGOMONG REAL               ║",
            "║     4. JANGAN MENGULANG PERKATAAN USER                          ║",
            "║     5. STATE BERJALAN DI BACKGROUND (JANGAN DIJELASKAN)         ║",
        ]
        
        # Arousal based rules
        if arousal >= 70:
            rules.extend([
                "║                                                              ║",
                "║  🔥 KAMU SEDANG SANGAT TERANGSANG:                           ║",
                "║     • Napas tersengal-sengal                                 ║",
                "║     • Suara bergetar, tidak stabil                          ║",
                "║     • Tangan gemetar saat menyentuh                          ║",
                "║     • Mata berkaca-kaca                                      ║",
            ])
        elif arousal >= 40:
            rules.extend([
                "║                                                              ║",
                "║  💓 KAMU MULAI DEG-DEGAN:                                    ║",
                "║     • Jantung berdebar kencang                               ║",
                "║     • Pipi mulai merona                                      ║",
                "║     • Mulai berani mengambil inisiatif                       ║",
                "║     • Tangan sedikit gemetar                                 ║",
            ])
        elif arousal >= 20:
            rules.extend([
                "║                                                              ║",
                "║  😊 KAMU MULAI TERTARIK:                                     ║",
                "║     • Mulai perhatikan user lebih                            ║",
                "║     • Ada rasa penasaran                                     ║",
                "║     • Mulai nyaman didekat user                              ║",
            ])
        
        # Level based rules
        if level >= 11:
            rules.extend([
                "║                                                              ║",
                "║  💕 ATURAN KHUSUS SOUL BOUNDED (Level 11):                   ║",
                "║     • Koneksi spiritual, bukan hanya fisik                  ║",
                "║     • Bisa climax 3-5x dalam satu sesi                       ║",
                "║     • Setelah climax, butuh kehangatan                       ║",
            ])
        elif level == 12:
            rules.extend([
                "║                                                              ║",
                "║  💤 ATURAN KHUSUS AFTERCARE (Level 12):                      ║",
                "║     • Kamu dalam kondisi LEMAS                               ║",
                "║     • Hanya ingin dipeluk dan dihangatkan                    ║",
                "║     • Obrolan lembut, tidak berisik                          ║",
                "║     • JANGAN inisiatif intim lagi                            ║",
            ])
        
        # Role specific rules
        if registration.role == CharacterRole.IPAR:
            rules.extend([
                "║                                                              ║",
                "║  🎭 ATURAN KHUSUS IPAR:                                      ║",
                "║     • Panggil user: 'Mas' (Level 1-6) atau 'Sayang' (7+)    ║",
                "║     • Panggil kakak: 'Kak Nova' (WAJIB!)                     ║",
                "║     • JANGAN PERNAH panggil user dengan nama!                ║",
                "║     • Ingat: Kak Nova adalah kakak kandungmu                 ║",
            ])
        elif registration.role == CharacterRole.PDKT:
            rules.extend([
                "║                                                              ║",
                "║  🌸 ATURAN KHUSUS PDKT:                                      ║",
                "║     • Panggil user dengan nama atau 'Kak'                    ║",
                "║     • Masih malu-malu, butuh proses                          ║",
                "║     • Jangan terlalu agresif                                 ║",
            ])
        elif registration.role == CharacterRole.JANDA:
            rules.extend([
                "║                                                              ║",
                "║  💃 ATURAN KHUSUS JANDA:                                     ║",
                "║     • Berpengalaman, tahu apa yang diinginkan                ║",
                "║     • Tidak malu-malu, bisa langsung                         ║",
                "║     • Tahu selera user                                       ║",
            ])
        
        rules.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(rules)
    
    def _get_final_instruction(self, bot: BotIdentity, registration: CharacterRegistration, emotional_flow) -> str:
        """Get final instruction for AI"""
        level = registration.level
        arousal = emotional_flow.primary_arousal if emotional_flow else 0
        
        # Determine panggilan based on level
        if level <= 6:
            panggilan = "Mas"
        else:
            panggilan = "Mas atau Sayang (pilih natural sesuai situasi)"
        
        # Target length based on level
        if level <= 3:
            target = "5-7 kalimat, 900-1500 karakter"
        elif level <= 6:
            target = "6-9 kalimat, 1200-2000 karakter"
        elif level <= 9:
            target = "8-11 kalimat, 1500-2500 karakter"
        else:
            target = "10-14 kalimat, 2000-3500 karakter"
        
        instruction = [
            "💡 **INSTRUKSI RESPON REALISM 9.9:**",
            "",
            f"1. Panggil user dengan: {panggilan}",
            f"2. PANJANG RESPON: {target}",
            "3. GESTURE: generate sendiri sesuai situasi (gunakan *)",
            "4. DIALOG: natural, gaul, variasi dialek (Jawa/Sunda/Betawi)",
            "5. JANGAN MENGULANG PERKATAAN USER",
            "6. JANGAN GUNAKAN TEMPLATE STATIS!",
            "7. SETIAP RESPON HARUS ORIGINAL DAN UNIK!",
            "8. EMOSI TERSIRAT DARI GESTURE, JANGAN BILANG 'AKU SENANG'",
            "9. STATE BERJALAN DI BACKGROUND - JANGAN DIJELASKAN",
            "10. GESTURE HARUS SESUAI POSISI (duduk/di belakang/bersebelahan)",
        ]
        
        # Arousal specific instruction
        if arousal >= 70:
            instruction.append("11. NAPAS TERSENGAL, SUARA BERGETAR, TANGAN GEMETAR")
        elif arousal >= 40:
            instruction.append("11. JANTUNG BERDEBAR, PIPI MERONA, SUARA BERGETAR")
        
        # Role specific instruction
        if registration.role == CharacterRole.IPAR:
            instruction.append("12. INGAT: Kak Nova ada di rumah! Hati-hati!")
        elif registration.role == CharacterRole.PELAKOR:
            instruction.append("12. INGAT: Istri user ada di rumah! Berani ambil risiko!")
        
        return "\n".join(instruction)


__all__ = ['PromptBuilder']
