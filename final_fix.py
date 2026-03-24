# final_fix.py
# -*- coding: utf-8 -*-
"""
Final fix untuk menambahkan kolom time_data ke state_tracker
"""

import sqlite3
import os
from pathlib import Path


def find_database_path():
    """Cari database di berbagai kemungkinan path"""
    possible_paths = [
        Path("data/amoria.db"),
        Path("/app/data/amoria.db"),
        Path("./amoria.db"),
        Path("amoria.db"),
        Path(os.getenv("DATABASE_PATH", "")),
    ]
    
    for path in possible_paths:
        if path and path.exists():
            return path
    
    return None


def add_time_data_column():
    """Tambahkan kolom time_data ke state_tracker"""
    
    print("=" * 60)
    print("🔧 FINAL FIX: Adding time_data column")
    print("=" * 60)
    
    # Cari database
    db_path = find_database_path()
    
    if not db_path:
        print("❌ Database tidak ditemukan!")
        print("\nMencoba membuat database baru...")
        
        # Buat direktori data
        Path("data").mkdir(parents=True, exist_ok=True)
        db_path = Path("data/amoria.db")
        
        print(f"📁 Database baru akan dibuat di: {db_path}")
    
    print(f"📁 Database path: {db_path}")
    
    try:
        # Connect ke database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Cek apakah tabel state_tracker ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='state_tracker'")
        if not cursor.fetchone():
            print("⚠️ Tabel state_tracker belum ada, membuat...")
            
            # Buat tabel state_tracker dengan semua kolom
            cursor.execute('''
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
                    clothing_history TEXT,
                    family_status TEXT,
                    family_location TEXT,
                    family_activity TEXT,
                    family_estimate_return TEXT,
                    activity_bot TEXT,
                    activity_user TEXT,
                    current_time TEXT,
                    time_override_history TEXT,
                    time_data TEXT,
                    updated_at REAL
                )
            ''')
            conn.commit()
            print("✅ Tabel state_tracker dibuat dengan kolom time_data")
        
        else:
            # Cek kolom yang ada
            cursor.execute("PRAGMA table_info(state_tracker)")
            columns = [col[1] for col in cursor.fetchall()]
            
            print(f"📊 Existing columns: {columns}")
            
            # Tambahkan kolom yang hilang
            columns_to_add = {
                'time_data': 'TEXT',
                'clothing_bot_outer_bottom': 'TEXT',
                'clothing_user_outer_bottom': 'TEXT',
                'clothing_history': 'TEXT',
                'family_status': 'TEXT',
                'family_location': 'TEXT',
                'family_activity': 'TEXT',
                'family_estimate_return': 'TEXT',
                'time_override_history': 'TEXT',
                'current_time': 'TEXT',
                'position_bot': 'TEXT',
                'position_user': 'TEXT',
                'position_relative': 'TEXT',
            }
            
            added = 0
            for col, col_type in columns_to_add.items():
                if col not in columns:
                    try:
                        cursor.execute(f"ALTER TABLE state_tracker ADD COLUMN {col} {col_type}")
                        print(f"  ✅ Added column: {col}")
                        added += 1
                    except Exception as e:
                        print(f"  ⚠️ Failed: {col} - {e}")
            
            if added > 0:
                conn.commit()
                print(f"\n✅ Added {added} column(s)")
            else:
                print("\n✅ No missing columns")
        
        # Verifikasi final
        cursor.execute("PRAGMA table_info(state_tracker)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📊 Final columns ({len(columns)}):")
        for col in columns:
            print(f"   • {col}")
        
        if 'time_data' in columns:
            print("\n✅ SUCCESS: time_data column exists!")
        else:
            print("\n❌ ERROR: time_data column still missing!")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ FINAL FIX COMPLETE!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = add_time_data_column()
    
    if success:
        print("\n🎉 Database siap digunakan!")
    else:
        print("\n❌ Fix gagal, periksa error di atas.")
