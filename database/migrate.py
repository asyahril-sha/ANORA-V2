# database/migrate.py
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_db

logger = logging.getLogger(__name__)


# =========================================================
# CREATE TABLES (SAFE - NO DROP)
# =========================================================

async def create_tables(db):
    logger.info("📦 Creating tables (SQLite safe mode)...")

    await db.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id TEXT PRIMARY KEY,
        role TEXT,
        sequence INTEGER,
        status TEXT DEFAULT 'active',
        created_at REAL,
        last_updated REAL,

        bot_identity TEXT DEFAULT '{}',
        user_identity TEXT DEFAULT '{}',

        bot_name TEXT,
        bot_age INTEGER,
        bot_height INTEGER,
        bot_weight INTEGER,
        bot_chest TEXT,
        bot_hijab INTEGER DEFAULT 0,

        user_name TEXT,
        user_status TEXT DEFAULT 'lajang',
        user_age INTEGER,
        user_height INTEGER,
        user_weight INTEGER,
        user_penis INTEGER,
        user_artist_ref TEXT,

        level INTEGER DEFAULT 1,
        total_chats INTEGER DEFAULT 0,
        total_climax_bot INTEGER DEFAULT 0,
        total_climax_user INTEGER DEFAULT 0,
        stamina_bot INTEGER DEFAULT 100,
        stamina_user INTEGER DEFAULT 100,

        in_intimacy_cycle INTEGER DEFAULT 0,
        intimacy_cycle_count INTEGER DEFAULT 0,
        last_climax_time REAL,
        cooldown_until REAL,

        weighted_memory_score REAL DEFAULT 0.5,
        weighted_memory_data TEXT DEFAULT '{}',
        emotional_bias TEXT DEFAULT '{}',

        secondary_emotion TEXT,
        secondary_arousal INTEGER DEFAULT 0,
        secondary_emotion_reason TEXT,

        physical_sensation TEXT DEFAULT 'biasa aja',
        physical_hunger INTEGER DEFAULT 30,
        physical_thirst INTEGER DEFAULT 30,
        physical_temperature INTEGER DEFAULT 25,

        metadata TEXT DEFAULT '{}'
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS working_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_id TEXT,
        chat_index INTEGER,
        timestamp REAL,
        user_message TEXT,
        bot_response TEXT,
        context TEXT
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS long_term_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_id TEXT,
        memory_type TEXT,
        content TEXT,
        importance REAL DEFAULT 0.5,
        timestamp REAL,
        status TEXT,
        emotional_tag TEXT,
        metadata TEXT DEFAULT '{}'
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS state_tracker (
        registration_id TEXT PRIMARY KEY,

        location_bot TEXT,
        location_user TEXT,
        position_bot TEXT,
        position_user TEXT,
        position_relative TEXT,

        clothing_bot_outer TEXT,
        clothing_bot_outer_bottom TEXT,
        clothing_bot_inner_top TEXT,
        clothing_bot_inner_bottom TEXT,
        clothing_user_outer TEXT,
        clothing_user_outer_bottom TEXT,
        clothing_user_inner_bottom TEXT,
        clothing_history TEXT DEFAULT '[]',

        family_status TEXT,
        family_location TEXT,
        family_activity TEXT,
        family_estimate_return TEXT,

        activity_bot TEXT,
        activity_user TEXT,

        current_time TEXT,
        time_override_history TEXT DEFAULT '[]',

        updated_at REAL
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        size INTEGER,
        created_at REAL,
        type TEXT DEFAULT 'auto',
        status TEXT DEFAULT 'completed',
        metadata TEXT DEFAULT '{}'
    )
    """)

    await db.commit()
    logger.info("✅ Tables ready")


# =========================================================
# FIX MISSING COLUMNS (CRITICAL)
# =========================================================

async def fix_missing_columns(db):
    logger.info("🧱 Fixing missing columns...")

    async def get_columns(table):
        rows = await db.fetch_all(f"PRAGMA table_info({table})")
        return [r['name'] for r in rows]

    async def add_column(table, col, definition):
        try:
            await db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
            logger.info(f"✅ Added column {table}.{col}")
        except Exception:
            pass

    # ================= REGISTRATIONS =================
    cols = await get_columns("registrations")

    reg_columns = {
        "secondary_emotion": "TEXT",
        "secondary_arousal": "INTEGER DEFAULT 0",
        "secondary_emotion_reason": "TEXT",
        "user_penis": "INTEGER",
        "user_artist_ref": "TEXT",
        "weighted_memory_data": "TEXT DEFAULT '{}'",
        "emotional_bias": "TEXT DEFAULT '{}'"
    }

    for col, defn in reg_columns.items():
        if col not in cols:
            await add_column("registrations", col, defn)

    # ================= STATE TRACKER =================
    cols = await get_columns("state_tracker")

    state_columns = {
        "clothing_bot_outer_bottom": "TEXT",
        "clothing_bot_inner_top": "TEXT",
        "clothing_bot_inner_bottom": "TEXT",
        "clothing_user_outer": "TEXT",
        "clothing_user_outer_bottom": "TEXT",
        "clothing_user_inner_bottom": "TEXT",
        "family_status": "TEXT",
        "family_location": "TEXT",
        "family_activity": "TEXT",
        "family_estimate_return": "TEXT",
        "clothing_history": "TEXT DEFAULT '[]'",
        "time_override_history": "TEXT DEFAULT '[]'"
    }

    for col, defn in state_columns.items():
        if col not in cols:
            await add_column("state_tracker", col, defn)

    # ================= LONG TERM =================
    cols = await get_columns("long_term_memory")

    if "status" not in cols:
        await add_column("long_term_memory", "status", "TEXT")

    if "emotional_tag" not in cols:
        await add_column("long_term_memory", "emotional_tag", "TEXT")

    await db.commit()
    logger.info("✅ Missing columns fixed")


# =========================================================
# INDEXES
# =========================================================

async def create_indexes(db):
    await db.execute("CREATE INDEX IF NOT EXISTS idx_reg_role ON registrations(role)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_reg_status ON registrations(status)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_mem_reg ON working_memory(registration_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_ltm_reg ON long_term_memory(registration_id)")
    await db.commit()
    logger.info("⚡ Indexes ready")


# =========================================================
# MAIN
# =========================================================

async def run_migrations():
    logger.info("=" * 60)
    logger.info("🚀 SQLITE SAFE MIGRATION")
    logger.info("=" * 60)

    try:
        db = await get_db()

        await create_tables(db)
        await fix_missing_columns(db)
        await create_indexes(db)

        logger.info("✅ DATABASE READY")
        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


async def migrate():
    """Alias for run_migrations (for compatibility)"""
    return await run_migrations()


def run_migration_sync():
    return asyncio.run(run_migrations())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migration_sync()
