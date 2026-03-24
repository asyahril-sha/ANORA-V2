# database/repository.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Database Repository - Complete with all methods
Target Realism 9.9/10
=============================================================================
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .connection import get_db
from .models import (
    Registration, RegistrationStatus, CharacterRole,
    WorkingMemoryItem, LongTermMemoryItem, MemoryType,
    StateTracker, ClothingState, MoodType,
    USER_PHYSICAL_TEMPLATES, Backup, BackupType, BackupStatus
)

logger = logging.getLogger(__name__)


class Repository:
    """
    Repository untuk semua operasi database AMORIA 9.9
    """
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    # =========================================================================
    # REGISTRATION OPERATIONS
    # =========================================================================
    
    async def get_next_sequence(self, role: CharacterRole) -> int:
        """Dapatkan nomor urut berikutnya untuk role tertentu"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT MAX(sequence) as max_seq FROM registrations WHERE role = ?",
            (role.value,)
        )
        
        if result and result['max_seq']:
            return result['max_seq'] + 1
        return 1
    
    async def create_registration(self, registration: Registration) -> str:
        """Buat registrasi baru"""
        db = await self._get_db()
        data = registration.to_dict()
        
        await db.execute(
            """
            INSERT INTO registrations (
                id, role, sequence, status, created_at, last_updated,
                bot_identity, user_identity,
                bot_name, bot_age, bot_height, bot_weight, bot_chest, bot_hijab,
                user_name, user_status, user_age, user_height, user_weight,
                user_penis, user_artist_ref,
                level, total_chats, total_climax_bot, total_climax_user,
                stamina_bot, stamina_user,
                in_intimacy_cycle, intimacy_cycle_count,
                last_climax_time, cooldown_until,
                weighted_memory_score, weighted_memory_data, emotional_bias,
                secondary_emotion, secondary_arousal, secondary_emotion_reason,
                physical_sensation, physical_hunger, physical_thirst, physical_temperature,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data['id'], data['role'], data['sequence'], data['status'],
                data['created_at'], data['last_updated'],
                data['bot_identity'], data['user_identity'],
                data['bot_name'], data['bot_age'], data['bot_height'],
                data['bot_weight'], data['bot_chest'], data['bot_hijab'],
                data['user_name'], data['user_status'], data['user_age'],
                data['user_height'], data['user_weight'], data['user_penis'],
                data['user_artist_ref'],
                data['level'], data['total_chats'], data['total_climax_bot'],
                data['total_climax_user'], data['stamina_bot'], data['stamina_user'],
                data['in_intimacy_cycle'], data['intimacy_cycle_count'],
                data['last_climax_time'], data['cooldown_until'],
                data['weighted_memory_score'], data['weighted_memory_data'],
                data['emotional_bias'],
                data['secondary_emotion'], data['secondary_arousal'],
                data['secondary_emotion_reason'],
                data['physical_sensation'], data['physical_hunger'],
                data['physical_thirst'], data['physical_temperature'],
                data['metadata']
            )
        )
        
        logger.info(f"✅ Created registration: {registration.id}")
        return registration.id
    
    async def get_registration(self, registration_id: str) -> Optional[Registration]:
        """Dapatkan registrasi berdasarkan ID"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT * FROM registrations WHERE id = ?",
            (registration_id,)
        )
        
        if not result:
            return None
        
        return Registration.from_dict(dict(result))
    
    async def get_user_registrations(self, user_id: int, role: Optional[CharacterRole] = None) -> List[Registration]:
        """Dapatkan semua registrasi untuk user"""
        db = await self._get_db()
        
        if role:
            results = await db.fetch_all(
                "SELECT * FROM registrations WHERE role = ? ORDER BY last_updated DESC",
                (role.value,)
            )
        else:
            results = await db.fetch_all(
                "SELECT * FROM registrations ORDER BY last_updated DESC"
            )
        
        registrations = []
        for row in results:
            registrations.append(Registration.from_dict(dict(row)))
        
        return registrations
    
    async def update_registration(self, registration: Registration):
        """Update registrasi"""
        db = await self._get_db()
        data = registration.to_dict()
        
        registration.last_updated = time.time()
        
        await db.execute(
            """
            UPDATE registrations SET
                status = ?, last_updated = ?,
                bot_identity = ?, user_identity = ?,
                bot_name = ?, bot_age = ?, bot_height = ?, bot_weight = ?, bot_chest = ?, bot_hijab = ?,
                user_name = ?, user_status = ?, user_age = ?, user_height = ?, user_weight = ?,
                user_penis = ?, user_artist_ref = ?,
                level = ?, total_chats = ?, total_climax_bot = ?, total_climax_user = ?,
                stamina_bot = ?, stamina_user = ?,
                in_intimacy_cycle = ?, intimacy_cycle_count = ?,
                last_climax_time = ?, cooldown_until = ?,
                weighted_memory_score = ?, weighted_memory_data = ?, emotional_bias = ?,
                secondary_emotion = ?, secondary_arousal = ?, secondary_emotion_reason = ?,
                physical_sensation = ?, physical_hunger = ?, physical_thirst = ?, physical_temperature = ?,
                metadata = ?
            WHERE id = ?
            """,
            (
                data['status'], registration.last_updated,
                data['bot_identity'], data['user_identity'],
                data['bot_name'], data['bot_age'], data['bot_height'],
                data['bot_weight'], data['bot_chest'], data['bot_hijab'],
                data['user_name'], data['user_status'], data['user_age'],
                data['user_height'], data['user_weight'], data['user_penis'],
                data['user_artist_ref'],
                data['level'], data['total_chats'], data['total_climax_bot'],
                data['total_climax_user'], data['stamina_bot'], data['stamina_user'],
                data['in_intimacy_cycle'], data['intimacy_cycle_count'],
                data['last_climax_time'], data['cooldown_until'],
                data['weighted_memory_score'], data['weighted_memory_data'],
                data['emotional_bias'],
                data['secondary_emotion'], data['secondary_arousal'],
                data['secondary_emotion_reason'],
                data['physical_sensation'], data['physical_hunger'],
                data['physical_thirst'], data['physical_temperature'],
                data['metadata'], registration.id
            )
        )
    
    async def close_registration(self, registration_id: str):
        """Tutup registrasi (close session)"""
        db = await self._get_db()
        await db.execute(
            "UPDATE registrations SET status = ?, last_updated = ? WHERE id = ?",
            (RegistrationStatus.CLOSED.value, time.time(), registration_id)
        )
        logger.info(f"📁 Closed registration: {registration_id}")
    
    async def end_registration(self, registration_id: str):
        """Akhiri registrasi (hapus permanen)"""
        db = await self._get_db()
        await db.execute(
            "UPDATE registrations SET status = ?, last_updated = ? WHERE id = ?",
            (RegistrationStatus.ENDED.value, time.time(), registration_id)
        )
        logger.info(f"💔 Ended registration: {registration_id}")
    
    async def delete_registration(self, registration_id: str):
        """Hapus registrasi permanen"""
        db = await self._get_db()
        await db.execute("DELETE FROM registrations WHERE id = ?", (registration_id,))
        logger.info(f"🗑️ Deleted registration: {registration_id}")
    
    # =========================================================================
    # WORKING MEMORY OPERATIONS
    # =========================================================================
    
    async def add_to_working_memory(self, item: WorkingMemoryItem):
        """Tambah item ke working memory"""
        db = await self._get_db()
        data = item.to_dict()
        
        await db.execute(
            """
            INSERT INTO working_memory
            (registration_id, chat_index, timestamp, user_message, bot_response, context)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data['registration_id'], data['chat_index'],
                data['timestamp'], data['user_message'],
                data['bot_response'], data['context']
            )
        )
    
    async def get_working_memory(self, registration_id: str, limit: int = 1000) -> List[Dict]:
        """Dapatkan working memory (chat terakhir)"""
        db = await self._get_db()
        
        results = await db.fetch_all(
            """
            SELECT * FROM working_memory
            WHERE registration_id = ?
            ORDER BY chat_index DESC LIMIT ?
            """,
            (registration_id, limit)
        )
        
        results.reverse()
        
        memories = []
        for row in results:
            memories.append({
                'chat_index': row['chat_index'],
                'timestamp': row['timestamp'],
                'user': row['user_message'],
                'bot': row['bot_response'],
                'importance': row.get('importance', 0.3),
                'context': json.loads(row['context']) if row['context'] else {}
            })
        
        return memories
    
    async def get_last_chat_index(self, registration_id: str) -> int:
        """Dapatkan index chat terakhir"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT MAX(chat_index) as max_idx FROM working_memory WHERE registration_id = ?",
            (registration_id,)
        )
        
        return result['max_idx'] if result and result['max_idx'] else 0
    
    async def cleanup_old_working_memory(self, registration_id: str, keep: int = 1000):
        """Hapus working memory lama, sisakan keep terakhir"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            """
            SELECT MIN(chat_index) as min_keep FROM (
                SELECT chat_index FROM working_memory
                WHERE registration_id = ?
                ORDER BY chat_index DESC LIMIT ?
            )
            """,
            (registration_id, keep)
        )
        
        if result and result['min_keep']:
            await db.execute(
                "DELETE FROM working_memory WHERE registration_id = ? AND chat_index < ?",
                (registration_id, result['min_keep'])
            )
    
    # =========================================================================
    # LONG TERM MEMORY OPERATIONS
    # =========================================================================
    
    async def add_long_term_memory(
        self,
        registration_id: str,
        memory_type: str,
        content: str,
        importance: float = 0.5,
        status: Optional[str] = None,
        emotional_tag: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Tambah item ke long-term memory"""
        db = await self._get_db()
        
        await db.execute(
            """
            INSERT INTO long_term_memory
            (registration_id, memory_type, content, importance, timestamp, status, emotional_tag, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                registration_id, memory_type, content, importance,
                time.time(), status, emotional_tag,
                json.dumps(metadata or {})
            )
        )
    
    async def get_long_term_memory(
        self,
        registration_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Dapatkan long-term memory"""
        db = await self._get_db()
        
        if memory_type:
            results = await db.fetch_all(
                """
                SELECT * FROM long_term_memory
                WHERE registration_id = ? AND memory_type = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
                """,
                (registration_id, memory_type, limit)
            )
        else:
            results = await db.fetch_all(
                """
                SELECT * FROM long_term_memory
                WHERE registration_id = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
                """,
                (registration_id, limit)
            )
        
        memories = []
        for row in results:
            memories.append({
                'id': row['id'],
                'type': row['memory_type'],
                'content': row['content'],
                'importance': row['importance'],
                'timestamp': row['timestamp'],
                'status': row['status'],
                'emotional_tag': row['emotional_tag'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            })
        
        return memories
    
    # =========================================================================
    # STATE TRACKER OPERATIONS (TANPA EMOTION/AROUSAL/MOOD)
    # =========================================================================
    
    async def save_state(self, state: StateTracker):
        """Simpan state tracker (tanpa emotion/arousal/mood)"""
        db = await self._get_db()
        data = state.to_dict()
        
        state.updated_at = time.time()
        
        existing = await db.fetch_one(
            "SELECT registration_id FROM state_tracker WHERE registration_id = ?",
            (state.registration_id,)
        )
        
        if existing:
            await db.execute(
                """
                UPDATE state_tracker SET
                    location_bot = ?, location_user = ?, position_bot = ?,
                    position_user = ?, position_relative = ?,
                    clothing_bot_outer = ?, clothing_bot_outer_bottom = ?,
                    clothing_bot_inner_top = ?, clothing_bot_inner_bottom = ?,
                    clothing_user_outer = ?, clothing_user_outer_bottom = ?,
                    clothing_user_inner_bottom = ?, clothing_history = ?,
                    family_status = ?, family_location = ?, family_activity = ?,
                    family_estimate_return = ?,
                    activity_bot = ?, activity_user = ?,
                    current_time = ?, time_override_history = ?,
                    updated_at = ?
                WHERE registration_id = ?
                """,
                (
                    data['location_bot'], data['location_user'],
                    data['position_bot'], data['position_user'], data['position_relative'],
                    data['clothing_bot_outer'], data['clothing_bot_outer_bottom'],
                    data['clothing_bot_inner_top'], data['clothing_bot_inner_bottom'],
                    data['clothing_user_outer'], data['clothing_user_outer_bottom'],
                    data['clothing_user_inner_bottom'], data['clothing_history'],
                    data['family_status'], data['family_location'], data['family_activity'],
                    data['family_estimate_return'],
                    data['activity_bot'], data['activity_user'],
                    data['current_time'], data['time_override_history'],
                    data['updated_at'], state.registration_id
                )
            )
        else:
            await db.execute(
                """
                INSERT INTO state_tracker (
                    registration_id, location_bot, location_user, position_bot,
                    position_user, position_relative, clothing_bot_outer,
                    clothing_bot_outer_bottom, clothing_bot_inner_top,
                    clothing_bot_inner_bottom, clothing_user_outer,
                    clothing_user_outer_bottom, clothing_user_inner_bottom,
                    clothing_history, family_status, family_location,
                    family_activity, family_estimate_return, activity_bot,
                    activity_user, current_time, time_override_history, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.registration_id, data['location_bot'], data['location_user'],
                    data['position_bot'], data['position_user'], data['position_relative'],
                    data['clothing_bot_outer'], data['clothing_bot_outer_bottom'],
                    data['clothing_bot_inner_top'], data['clothing_bot_inner_bottom'],
                    data['clothing_user_outer'], data['clothing_user_outer_bottom'],
                    data['clothing_user_inner_bottom'], data['clothing_history'],
                    data['family_status'], data['family_location'], data['family_activity'],
                    data['family_estimate_return'], data['activity_bot'], data['activity_user'],
                    data['current_time'], data['time_override_history'], data['updated_at']
                )
            )
        
        logger.debug(f"State saved for {state.registration_id}")
    
    async def load_state(self, registration_id: str) -> Optional[StateTracker]:
        """Load state tracker"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT * FROM state_tracker WHERE registration_id = ?",
            (registration_id,)
        )
        
        if not result:
            return None
        
        return StateTracker.from_dict(dict(result))
    
    # =========================================================================
    # BACKUP OPERATIONS
    # =========================================================================
    
    async def add_backup(self, backup: Backup) -> int:
        """Tambah record backup"""
        db = await self._get_db()
        data = backup.to_dict()
        
        result = await db.execute(
            """
            INSERT INTO backups (filename, size, created_at, type, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data['filename'], data['size'], data['created_at'],
                data['type'], data['status'], data['metadata']
            )
        )
        
        return result.lastrowid
    
    async def get_backups(self, limit: int = 10) -> List[Backup]:
        """Dapatkan daftar backup terbaru"""
        db = await self._get_db()
        
        results = await db.fetch_all(
            "SELECT * FROM backups ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        backups = []
        for row in results:
            backups.append(Backup.from_dict(dict(row)))
        
        return backups
    
    async def get_stats(self) -> Dict:
        """Dapatkan statistik database"""
        db = await self._get_db()
        
        stats = {}
        
        tables = ['registrations', 'working_memory', 'long_term_memory', 'state_tracker', 'backups']
        
        for table in tables:
            try:
                result = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = result['count'] if result else 0
            except:
                stats[f"{table}_count"] = 0
        
        active = await db.fetch_one(
            "SELECT COUNT(*) as count FROM registrations WHERE status = 'active'"
        )
        stats['active_registrations'] = active['count'] if active else 0
        
        total_chats = await db.fetch_one(
            "SELECT SUM(total_chats) as total FROM registrations"
        )
        stats['total_chats_all_time'] = total_chats['total'] if total_chats and total_chats['total'] else 0
        
        db_path = settings.database.path
        if db_path.exists():
            stats['db_size_mb'] = round(db_path.stat().st_size / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
        
        return stats


__all__ = ['Repository']
