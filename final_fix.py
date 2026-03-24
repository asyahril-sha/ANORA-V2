# final_fix.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final fix - just verify columns are there
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def verify_and_fix():
    """Verify columns and add if missing"""
    
    print("=" * 60)
    print("🔧 AMORIA - FINAL DATABASE VERIFICATION")
    print("=" * 60)
    
    try:
        # Use direct sqlite3 to avoid wrapper issues
        import sqlite3
        
        db_path = Path("data/amoria.db")
        
        if not db_path.exists():
            print(f"❌ Database not found at {db_path}")
            return False
        
        print(f"📁 Database: {db_path}")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check registrations table
        cursor.execute("PRAGMA table_info(registrations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📊 Registrations table:")
        print(f"   Total columns: {len(columns)}")
        
        # Check critical columns
        critical = [
            'weighted_memory_score',
            'weighted_memory_data',
            'emotional_bias',
            'stamina_bot',
            'stamina_user'
        ]
        
        missing = []
        for col in critical:
            if col in columns:
                print(f"   ✅ {col} exists")
            else:
                print(f"   ❌ {col} MISSING")
                missing.append(col)
        
        # Add missing columns if any
        if missing:
            print(f"\n🔧 Adding missing columns...")
            for col in missing:
                if col == 'weighted_memory_score':
                    cursor.execute("ALTER TABLE registrations ADD COLUMN weighted_memory_score REAL DEFAULT 0.5")
                elif col == 'weighted_memory_data':
                    cursor.execute("ALTER TABLE registrations ADD COLUMN weighted_memory_data TEXT DEFAULT '{}'")
                elif col == 'emotional_bias':
                    cursor.execute("ALTER TABLE registrations ADD COLUMN emotional_bias TEXT DEFAULT '{}'")
                elif col == 'stamina_bot':
                    cursor.execute("ALTER TABLE registrations ADD COLUMN stamina_bot INTEGER DEFAULT 100")
                elif col == 'stamina_user':
                    cursor.execute("ALTER TABLE registrations ADD COLUMN stamina_user INTEGER DEFAULT 100")
                print(f"   ✅ Added {col}")
            
            conn.commit()
            print(f"\n✅ Added {len(missing)} column(s)")
        
        # Check state_tracker
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='state_tracker'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(state_tracker)")
            state_columns = [col[1] for col in cursor.fetchall()]
            
            print(f"\n📊 State tracker table:")
            print(f"   Total columns: {len(state_columns)}")
            
            if 'clothing_bot_outer_bottom' in state_columns:
                print(f"   ✅ clothing_bot_outer_bottom exists")
            else:
                print(f"   ⚠️ Adding clothing_bot_outer_bottom...")
                cursor.execute("ALTER TABLE state_tracker ADD COLUMN clothing_bot_outer_bottom TEXT")
                conn.commit()
                print(f"   ✅ Added clothing_bot_outer_bottom")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE VERIFICATION COMPLETE!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(verify_and_fix())
    sys.exit(0 if success else 1)
