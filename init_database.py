#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize database from scratch
"""

import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

async def init_database():
    """Initialize database from scratch"""
    
    print("=" * 60)
    print("💜 AMORIA - INITIALIZE DATABASE")
    print("=" * 60)
    
    try:
        # Create data directory if not exists
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {data_dir}")
        
        # Import database modules
        from database.connection import init_db, get_db, close_db
        
        # Initialize database (this will create tables)
        print("\n📁 Initializing database...")
        await init_db()
        db = await get_db()
        
        print("✅ Database initialized successfully")
        
        # Verify tables
        print("\n📊 Verifying tables...")
        tables = await db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        
        if tables:
            print(f"\n✅ Tables created ({len(tables)} tables):")
            for table in tables:
                # Get column count
                columns = await db.fetch_all(f"PRAGMA table_info({table['name']})")
                print(f"   • {table['name']}: {len(columns)} columns")
                
                # Special check for registrations
                if table['name'] == 'registrations':
                    col_names = [c['name'] for c in columns]
                    critical = ['weighted_memory_score', 'stamina_bot', 'in_intimacy_cycle']
                    
                    for col in critical:
                        if col in col_names:
                            print(f"     ✅ {col} present")
                        else:
                            print(f"     ❌ {col} MISSING!")
        else:
            print("⚠️ No tables found!")
        
        # Database stats
        if data_dir.joinpath("amoria.db").exists():
            size_mb = data_dir.joinpath("amoria.db").stat().st_size / (1024 * 1024)
            print(f"\n💾 Database size: {size_mb:.2f} MB")
        
        await close_db()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_database():
    """Check if database exists and its status"""
    
    db_path = Path("data/amoria.db")
    
    print("=" * 60)
    print("🔍 CHECKING DATABASE")
    print("=" * 60)
    
    if db_path.exists():
        print(f"✅ Database exists: {db_path}")
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")
        
        # Try to connect
        try:
            import aiosqlite
            conn = await aiosqlite.connect(str(db_path))
            
            cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = await cursor.fetchall()
            
            print(f"\n📊 Tables ({len(tables)}):")
            for table in tables:
                cursor2 = await conn.execute(f"PRAGMA table_info({table[0]})")
                cols = await cursor2.fetchall()
                print(f"   • {table[0]}: {len(cols)} columns")
            
            await conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Cannot connect: {e}")
            return False
    else:
        print(f"❌ Database not found: {db_path}")
        print("   Run: python init_database.py to create it")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        success = asyncio.run(check_database())
    else:
        success = asyncio.run(init_database())
    
    sys.exit(0 if success else 1)
