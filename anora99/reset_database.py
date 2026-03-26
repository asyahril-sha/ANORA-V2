#!/usr/bin/env python3
"""
Reset Database ANORA 9.9
Menghapus database lama dan membuat database baru dengan struktur yang benar.
"""

import os
import sys
import asyncio
import shutil
from pathlib import Path
from datetime import datetime

# Tambahkan path project
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🗄️  RESET DATABASE ANORA 9.9")
print("=" * 70)


async def reset_database():
    """Reset database ANORA 9.9"""
    
    # Path database
    db_path = Path("data/anora.db")
    backup_dir = Path("backups_anora99")
    backup_dir.mkdir(exist_ok=True)
    
    print("\n📁 Database path:", db_path)
    print("📁 Backup directory:", backup_dir)
    
    # ========== 1. BACKUP DATABASE LAMA (JIKA ADA) ==========
    if db_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"anora99_old_{timestamp}.db"
        
        print(f"\n📦 Backup database lama ke: {backup_path.name}")
        shutil.copy(db_path, backup_path)
        
        size_kb = db_path.stat().st_size / 1024
        print(f"   Size: {size_kb:.2f} KB")
        print(f"   ✅ Backup berhasil")
    else:
        print("\n📦 Database lama tidak ditemukan, akan membuat baru.")
    
    # ========== 2. HAPUS DATABASE LAMA ==========
    if db_path.exists():
        print("\n🗑️  Menghapus database lama...")
        db_path.unlink()
        print("   ✅ Database lama dihapus")
    
    # ========== 3. BUAT DATABASE BARU ==========
    print("\n🔄 Membuat database baru...")
    
    try:
        # Import komponen ANORA
        from anora99.memory_persistent import get_anora_persistent
        from anora99.brain import get_anora_brain
        from anora99.roles.role_manager import get_role_manager
        from anora99.emotional_engine import get_emotional_engine
        from anora99.relationship import get_relationship_manager
        from anora99.conflict_engine import get_conflict_engine
        
        # Inisialisasi database baru
        persistent = await get_anora_persistent()
        print("   ✅ Persistent memory initialized")
        
        brain = get_anora_brain()
        await persistent.save_current_state(brain)
        print("   ✅ Brain state saved")
        
        # Load role manager (akan membuat data awal)
        role_manager = get_role_manager()
        if role_manager:
            await role_manager.load_all(persistent)
            print("   ✅ Role states loaded")
        
        # Cek apakah database sudah dibuat
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            print(f"\n✅ Database baru berhasil dibuat!")
            print(f"   📁 Path: {db_path}")
            print(f"   📊 Size: {size_kb:.2f} KB")
        else:
            print("\n❌ Database gagal dibuat!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_database():
    """Cek status database"""
    db_path = Path("data/anora.db")
    
    print("\n" + "=" * 70)
    print("🔍 CEK STATUS DATABASE")
    print("=" * 70)
    
    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print(f"✅ Database ada: {db_path}")
        print(f"   Size: {size_kb:.2f} KB")
        
        # Coba cek isi database
        try:
            import aiosqlite
            
            async def check_tables():
                conn = await aiosqlite.connect(str(db_path))
                cursor = await conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                tables = await cursor.fetchall()
                await conn.close()
                return [t[0] for t in tables]
            
            tables = await check_tables()
            print(f"   Tables: {', '.join(tables)}")
            print(f"   Total: {len(tables)} tabel")
            
        except Exception as e:
            print(f"   ⚠️  Gagal cek tabel: {e}")
        
        return True
    else:
        print("❌ Database tidak ada!")
        return False


async def main():
    """Main function"""
    print("=" * 70)
    print("🗄️  ANORA 9.9 - Database Reset Tool")
    print("=" * 70)
    
    # Cek status sebelum reset
    await check_database()
    
    print("\n" + "=" * 70)
    print("⚠️  PERINGATAN!")
    print("=" * 70)
    print("Database lama akan dihapus dan dibuat baru.")
    print("Semua data yang tersimpan akan hilang.")
    print("\nTekan ENTER untuk melanjutkan, atau CTRL+C untuk membatalkan...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Dibatalkan oleh user.")
        return
    
    # Reset database
    success = await reset_database()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ RESET DATABASE BERHASIL!")
        print("=" * 70)
        
        # Cek status setelah reset
        await check_database()
        
        print("\n📌 Catatan:")
        print("   - Database baru sudah siap digunakan")
        print("   - Restart bot untuk menggunakan database baru")
        print("   - Kirim /nova untuk mulai ngobrol dengan Nova")
        
    else:
        print("\n" + "=" * 70)
        print("❌ RESET DATABASE GAGAL!")
        print("=" * 70)
        print("Cek error di atas dan coba lagi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Dibatalkan oleh user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
