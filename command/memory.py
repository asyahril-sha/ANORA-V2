# command/memory.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /memory, /flashback - Ringkasan Memory & Flashback
Target Realism 9.9/10
=============================================================================
"""

import logging
import random
import time
from typing import Optional, Dict, List, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from identity.manager import IdentityManager
from memory.working_memory import WorkingMemory
from memory.long_term_memory import LongTermMemory
from memory.emotional_memory import EmotionalMemory
from database.repository import Repository

logger = logging.getLogger(__name__)


async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /memory - Ringkasan memory karakter dengan weighted stats
    """
    user_id = update.effective_user.id
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter, atau `/sessions` untuk melanjutkan karakter tersimpan.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    bot_name = current_reg.get('bot_name')
    
    identity_manager = IdentityManager()
    repo = Repository()
    
    # Dapatkan memory
    working_memories = await repo.get_working_memory(registration_id, limit=1000)
    long_term_memories = await repo.get_long_term_memory(registration_id, limit=200)
    
    # Hitung weighted stats
    weighted_stats = await _calculate_weighted_stats(working_memories)
    
    # Kelompokkan long term memory
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    promises = [m for m in long_term_memories if m.get('type') == 'promise' and m.get('status') == 'pending']
    plans = [m for m in long_term_memories if m.get('type') == 'plan' and m.get('status') == 'pending']
    preferences = [m for m in long_term_memories if m.get('type') == 'preference']
    
    response = _format_memory_summary(
        bot_name=bot_name,
        total_chats=current_reg.get('total_chats', 0),
        weighted_stats=weighted_stats,
        milestones=milestones,
        promises=promises,
        plans=plans,
        preferences=preferences
    )
    
    keyboard = [
        [InlineKeyboardButton("📜 Chat Terakhir", callback_data="memory_chat"),
         InlineKeyboardButton("🏆 Milestone", callback_data="memory_milestone")],
        [InlineKeyboardButton("📝 Janji & Rencana", callback_data="memory_promises"),
         InlineKeyboardButton("💖 Preferensi", callback_data="memory_preferences")],
        [InlineKeyboardButton("📊 Weighted Stats", callback_data="memory_weighted"),
         InlineKeyboardButton("🎭 Flashback", callback_data="flashback_random")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def memory_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat chat terakhir"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    repo = Repository()
    
    working_memories = await repo.get_working_memory(registration_id, limit=20)
    
    if not working_memories:
        await query.edit_message_text(
            "📜 **CHAT TERAKHIR**\n\nBelum ada percakapan.",
            parse_mode='HTML'
        )
        return
    
    lines = ["📜 **CHAT TERAKHIR**\n"]
    
    for i, msg in enumerate(working_memories[-10:], 1):
        time_str = datetime.fromtimestamp(msg['timestamp']).strftime("%H:%M")
        lines.append(f"{i}. [{time_str}] **User:** {msg['user'][:60]}")
        lines.append(f"   **Bot:** {msg['bot'][:60]}")
        lines.append("")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_milestone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat milestone"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    repo = Repository()
    
    long_term_memories = await repo.get_long_term_memory(registration_id, limit=100)
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    
    if not milestones:
        await query.edit_message_text(
            "🏆 **MILESTONE**\n\nBelum ada milestone. Terus berinteraksi untuk menciptakan momen spesial!",
            parse_mode='HTML'
        )
        return
    
    lines = ["🏆 **MILESTONE**\n"]
    
    for m in milestones[-10:]:
        time_str = datetime.fromtimestamp(m['timestamp']).strftime("%d %b %Y")
        emotion = m.get('emotional_tag', 'spesial')
        emoji = _get_emotion_emoji(emotion)
        lines.append(f"{emoji} [{time_str}] {m['content'][:80]}")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_promises_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat janji & rencana"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    repo = Repository()
    
    long_term_memories = await repo.get_long_term_memory(registration_id, limit=100)
    promises = [m for m in long_term_memories if m.get('type') == 'promise' and m.get('status') == 'pending']
    plans = [m for m in long_term_memories if m.get('type') == 'plan' and m.get('status') == 'pending']
    
    lines = ["📝 **JANJI & RENCANA**\n"]
    
    if promises:
        lines.append("**Janji yang belum ditepati:**")
        for p in promises[:5]:
            time_str = datetime.fromtimestamp(p['timestamp']).strftime("%d %b")
            lines.append(f"• [{time_str}] {p['content'][:70]}")
        lines.append("")
    
    if plans:
        lines.append("**Rencana yang akan datang:**")
        for p in plans[:5]:
            time_str = datetime.fromtimestamp(p['timestamp']).strftime("%d %b")
            lines.append(f"• [{time_str}] {p['content'][:70]}")
        lines.append("")
    
    if not promises and not plans:
        lines.append("Belum ada janji atau rencana yang tercatat.")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_preferences_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat preferensi"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    repo = Repository()
    
    long_term_memories = await repo.get_long_term_memory(registration_id, limit=100)
    preferences = [m for m in long_term_memories if m.get('type') == 'preference']
    
    if not preferences:
        await query.edit_message_text(
            "💖 **PREFERENSI**\n\nBelum ada data preferensi. Bot akan belajar dari interaksi.",
            parse_mode='HTML'
        )
        return
    
    # Kelompokkan berdasarkan kategori
    by_category = {}
    for p in preferences:
        meta = p.get('metadata', {})
        category = meta.get('category', 'umum')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(p)
    
    lines = ["💖 **PREFERENSI USER**\n"]
    
    for category, items in by_category.items():
        lines.append(f"**{category.upper()}:**")
        for item in items[:3]:
            score = item.get('importance', 0.5) * 100
            bar = "❤️" * int(score / 10) + "🖤" * (10 - int(score / 10))
            lines.append(f"   • {item['content'][:30]}: {bar} {score:.0f}%")
        lines.append("")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_weighted_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat weighted stats"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    repo = Repository()
    
    working_memories = await repo.get_working_memory(registration_id, limit=1000)
    weighted_stats = await _calculate_weighted_stats(working_memories)
    
    response = _format_weighted_stats(weighted_stats)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /flashback - Flashback random
    """
    user_id = update.effective_user.id
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    repo = Repository()
    
    # Dapatkan long term memory
    long_term_memories = await repo.get_long_term_memory(registration_id, limit=200)
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    
    if not milestones:
        await update.message.reply_text(
            "🎭 **FLASHBACK**\n\n"
            "Belum ada kenangan yang cukup untuk flashback.\n"
            "Terus berinteraksi untuk menciptakan momen spesial!",
            parse_mode='HTML'
        )
        return
    
    # Pilih random milestone
    memory = random.choice(milestones)
    
    # Format flashback
    flashback_text = _format_flashback(memory)
    
    keyboard = [[InlineKeyboardButton("🎲 Flashback Lain", callback_data="flashback_random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(flashback_text, reply_markup=reply_markup, parse_mode='HTML')


async def flashback_random_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk flashback random"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    repo = Repository()
    
    long_term_memories = await repo.get_long_term_memory(registration_id, limit=200)
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    
    if not milestones:
        await query.edit_message_text("Belum ada kenangan.", parse_mode='HTML')
        return
    
    memory = random.choice(milestones)
    flashback_text = _format_flashback(memory)
    
    keyboard = [[InlineKeyboardButton("🎲 Flashback Lain", callback_data="flashback_random"),
                 InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(flashback_text, reply_markup=reply_markup, parse_mode='HTML')


async def memory_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback kembali ke menu memory utama"""
    query = update.callback_query
    await query.answer()
    
    await memory_command(update, context)


async def _calculate_weighted_stats(working_memories: List[Dict]) -> Dict:
    """Hitung weighted stats dari working memory"""
    if not working_memories:
        return {'total': 0, 'avg_importance': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    total = len(working_memories)
    importance_sum = sum(m.get('importance', 0.3) for m in working_memories)
    avg_importance = importance_sum / total if total > 0 else 0
    
    high = sum(1 for m in working_memories if m.get('importance', 0) >= 0.7)
    medium = sum(1 for m in working_memories if 0.4 <= m.get('importance', 0) < 0.7)
    low = sum(1 for m in working_memories if m.get('importance', 0) < 0.4)
    
    # Top important memories
    top_important = sorted(working_memories, key=lambda x: x.get('importance', 0), reverse=True)[:5]
    
    return {
        'total': total,
        'avg_importance': round(avg_importance, 2),
        'high': high,
        'medium': medium,
        'low': low,
        'top_important': [
            {'user': m['user'][:80], 'importance': m.get('importance', 0)}
            for m in top_important
        ]
    }


def _format_memory_summary(
    bot_name: str,
    total_chats: int,
    weighted_stats: Dict,
    milestones: List[Dict],
    promises: List[Dict],
    plans: List[Dict],
    preferences: List[Dict]
) -> str:
    """Format ringkasan memory"""
    
    bar_length = 20
    filled = int(weighted_stats['avg_importance'] * bar_length)
    importance_bar = "⭐" * filled + "·" * (bar_length - filled)
    
    return (
        f"🧠 **MEMORY {bot_name.upper()}**\n\n"
        f"📊 **Statistik:**\n"
        f"• Total Chat: {total_chats}\n"
        f"• Working Memory: {min(weighted_stats['total'], 1000)} chat\n"
        f"• Weighted Importance: {importance_bar} {weighted_stats['avg_importance']:.0%}\n"
        f"  - Penting (>70%): {weighted_stats['high']}\n"
        f"  - Sedang (40-70%): {weighted_stats['medium']}\n"
        f"  - Biasa (<40%): {weighted_stats['low']}\n"
        f"• Milestone: {len(milestones)} momen spesial\n"
        f"• Janji Tertunda: {len(promises)}\n"
        f"• Rencana: {len(plans)}\n"
        f"• Preferensi: {len(preferences)} item\n\n"
        f"💡 Bot ingat {min(weighted_stats['total'], 1000)} chat terakhir dengan weighted importance.\n"
        f"   Momen penting (⭐) lebih diingat daripada obrolan biasa.\n\n"
        f"_Pilih kategori untuk melihat detail:_"
    )


def _format_weighted_stats(weighted_stats: Dict) -> str:
    """Format weighted stats untuk display"""
    if weighted_stats['total'] == 0:
        return "📊 **WEIGHTED STATS**\n\nBelum ada data cukup."
    
    lines = ["📊 **WEIGHTED STATS**\n"]
    lines.append(f"📈 **Total Chat:** {weighted_stats['total']}")
    lines.append(f"⭐ **Rata-rata Importance:** {weighted_stats['avg_importance']:.0%}")
    lines.append("")
    lines.append("📊 **Distribusi:**")
    lines.append(f"   • Tinggi (>70%): {weighted_stats['high']} chat")
    lines.append(f"   • Sedang (40-70%): {weighted_stats['medium']} chat")
    lines.append(f"   • Rendah (<40%): {weighted_stats['low']} chat")
    lines.append("")
    
    if weighted_stats['top_important']:
        lines.append("🏆 **TOP 5 MOMEN PENTING:**")
        for i, m in enumerate(weighted_stats['top_important'], 1):
            lines.append(f"{i}. [{m['importance']:.0%}] {m['user'][:60]}")
    
    return "\n".join(lines)


def _format_flashback(memory: Dict) -> str:
    """Format flashback untuk display"""
    time_str = datetime.fromtimestamp(memory['timestamp']).strftime("%d %b %Y, %H:%M")
    content = memory['content']
    emotion = memory.get('emotional_tag', 'kenangan')
    
    emoji = _get_emotion_emoji(emotion)
    
    return f"""
🎭 **FLASHBACK** {emoji}

*{time_str}*

{content}

💭 _Kenangan indah yang tidak akan pernah terlupa..._
"""


def _get_emotion_emoji(emotion: str) -> str:
    """Dapatkan emoji untuk emotional tag"""
    emojis = {
        'romantis': '💕',
        'senang': '😊',
        'sedih': '😢',
        'horny': '🔥',
        'climax': '💦',
        'rindu': '🥺',
        'malu': '😳',
        'berani': '😏',
        'spesial': '✨',
        'first_kiss': '💋',
        'first_intim': '💕',
        'milestone': '🏆'
    }
    return emojis.get(emotion.lower(), '💭')


__all__ = [
    'memory_command',
    'flashback_command',
    'memory_chat_callback',
    'memory_milestone_callback',
    'memory_promises_callback',
    'memory_preferences_callback',
    'memory_weighted_callback',
    'flashback_random_callback',
    'memory_back_callback'
]
