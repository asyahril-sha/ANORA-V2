```python
# fix_missing_columns.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - FIX MISSING COLUMNS (SAFE MIGRATION TOOL)
=============================================================================

Tujuan:
- Menambahkan kolom yang belum ada di schema lama
- Tanpa reset database
- Aman untuk production (idempotent)

Usage:
    python fix_missing_columns.py
"""

import asyncio
import logging

from database.postgres_connection import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_state_tracker_columns(db):
    """Fix missing columns di state_tracker"""

    logger.info("🔧 Checking & fixing state_tracker columns...")

    await db.execute("""
        DO $$
        BEGIN
            -- BOT CLOTHING
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'state_tracker' 
                AND column_name = 'clothing_bot_outer_bottom'
            ) THEN
                ALTER TABLE state_tracker ADD COLUMN clothing_bot_outer_bottom TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'state_tracker' 
                AND column_name = 'clothing_bot_inner_top'
            ) THEN
                ALTER TABLE state_tracker ADD COLUMN clothing_bot_inner_top TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'state_tracker' 
                AND column_name = 'clothing_bot_inner_bottom'
            ) THEN
                ALTER TABLE state_tracker ADD COLUMN clothing_bot_inner_bottom TEXT;
            END IF;

            -- USER CLOTHING
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'state_tracker' 
                AND column_name = 'clothing_user_outer'
            ) THEN
                ALTER TABLE state_tracker ADD COLUMN clothing_user_outer TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'state_tracker' 
                AND column_name = 'clothing_user_outer_bottom'
            ) THEN
                ALTER TABLE state_tracker ADD COLUMN clothing_user_outer_bottom TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'state_tracker' 
                AND column_name = 'clothing_user_inner_bottom'
            ) THEN
                ALTER TABLE state_tracker ADD COLUMN clothing_user_inner_bottom TEXT;
            END IF;

        END $$;
    """)

    logger.info("✅ state_tracker columns fixed")


async def run_fix():
    """Main runner"""
    print("\n⚠ Ini akan memperbaiki schema database TANPA menghapus data")
    confirm = input("Ketik 'FIX' untuk melanjutkan: ")

    if confirm != "FIX":
        print("❌ Dibatalkan")
        return

    try:
        db = await get_db()

        # Fix columns
        await fix_state_tracker_columns(db)

        logger.info("🎉 ALL FIXES COMPLETED")

    except Exception as e:
        logger.exception("❌ FIX FAILED")
        raise


if __name__ == "__main__":
    asyncio.run(run_fix())
```
