#!/usr/bin/env python3
"""
Reset Database ANORA 9.9 - FOR RAILWAY
Tanpa input interaktif, langsung reset
"""

import os
import sys
import asyncio
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🗄️  RESET DATABASE ANORA 9.9 (RAILWAY MODE)")
print("=" * 70)


async def reset_database():
    """Reset database tanpa konfirmasi"""
    
    db_path = Path("data/anora.db")
    backup_dir = Path("backups_anora99")
    backup_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Database path: {db_path}")
    
    # ========== 1. BACKUP ==========
    if db_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"anora99_old_{timestamp}.db"
        
        print(f"\n📦 Backup database lama ke: {backup_path.name}")
        shutil.copy(db_path, backup_path)
        print(f"   ✅ Backup berhasil")
    
    # ========== 2. HAPUS ==========
    if db_path.exists():
        print("\n🗑️  Menghapus database lama...")
        db_path.unlink()
        print("   ✅ Database lama dihapus")
    
    # ========== 3. BUAT BARU ==========
    print("\n🔄 Membuat database baru...")
    
    try:
        from anora99.memory_persistent import get_anora_persistent
        from anora99.brain import get_anora_brain
        from anora99.roles.role_manager import get_role_manager
        
        persistent = await get_anora_persistent()
        print("   ✅ Persistent memory initialized")
        
        brain = get_anora_brain()
        await persistent.save_current_state(brain)
        print("   ✅ Brain state saved")
        
        role_manager = get_role_manager()
        if role_manager:
            await role_manager.load_all(persistent)
            print("   ✅ Role states loaded")
        
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            print(f"\n✅ Database baru berhasil dibuat!")
            print(f"   📁 Path: {db_path}")
            print(f"   📊 Size: {size_kb:.2f} KB")
            return True
        else:
            print("\n❌ Database gagal dibuat!")
            return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function"""
    print("=" * 70)
    print("🗄️  ANORA 9.9 - Database Reset (Railway Mode)")
    print("=" * 70)
    print("⚠️  Database akan direset tanpa konfirmasi!")
    print("   (Backup akan dibuat terlebih dahulu)")
    print("")
    
    success = await reset_database()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ RESET DATABASE BERHASIL!")
        print("=" * 70)
        print("\n📌 Next step:")
        print("   - Restart bot untuk menggunakan database baru")
        print("   - Kirim /nova untuk mulai ngobrol dengan Nova")
    else:
        print("\n" + "=" * 70)
        print("❌ RESET DATABASE GAGAL!")
        print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
