# backup/recovery.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Backup Recovery System
=============================================================================
"""

import json
import time
import zipfile
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import settings
from .automated import get_backup_manager
from .verify import BackupVerifier

logger = logging.getLogger(__name__)


class RecoveryManager:
    """Manajer untuk recovery dari backup"""
    
    def __init__(self, backup_manager):
        self.backup_manager = backup_manager
        self.backup_dir = backup_manager.backup_dir
        self.verifier = BackupVerifier()
    
    async def list_backups(self, limit: int = 10) -> List[Dict]:
        """List available backups"""
        from database.repository import Repository
        repo = Repository()
        backups = await repo.get_backups(limit)
        
        result = []
        for i, backup in enumerate(backups, 1):
            result.append({
                "index": i,
                "filename": backup.filename,
                "date": datetime.fromtimestamp(backup.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                "size_mb": round(backup.size / (1024 * 1024), 2) if backup.size else 0,
                "type": backup.type.value
            })
        return result
    
    async def find_backup(self, identifier: str) -> Optional[Path]:
        """Find backup file by identifier"""
        try:
            idx = int(identifier)
            backups = await self.list_backups(limit=50)
            if 1 <= idx <= len(backups):
                backup_path = self.backup_dir / backups[idx - 1]['filename']
                if backup_path.exists():
                    return backup_path
        except ValueError:
            backup_path = self.backup_dir / identifier
            if backup_path.exists():
                return backup_path
        return None
    
    async def restore_backup(self, backup_path: Path, dry_run: bool = False) -> Dict:
        """Restore from backup"""
        if not backup_path.exists():
            return {"success": False, "error": "Backup file not found"}
        
        logger.info(f"🔄 Restoring from backup: {backup_path.name}")
        
        verify_result = await self.verifier.verify_backup(backup_path)
        if not verify_result['valid']:
            return {"success": False, "error": f"Backup corrupted: {verify_result.get('error', 'Unknown')}"}
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "filename": backup_path.name,
                "files": verify_result.get('files', 0),
                "size_mb": verify_result['size_mb']
            }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = self.backup_dir / f"restore_temp_{timestamp}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            await self._backup_current_data()
            
            await self._restore_files(temp_dir)
            
            logger.info(f"✅ Restore completed: {backup_path.name}")
            
            return {
                "success": True,
                "filename": backup_path.name,
                "files_restored": verify_result.get('files', 0),
                "size_mb": verify_result['size_mb'],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    async def _backup_current_data(self):
        """Create backup of current data before restore"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_restore_backup_{timestamp}"
        backup_dir = self.backup_dir / backup_name
        backup_dir.mkdir(exist_ok=True)
        
        from config import settings
        db_path = settings.database.path
        if db_path.exists():
            shutil.copy2(db_path, backup_dir / "database_before_restore.sqlite")
        
        session_dir = settings.identity.session_dir
        if session_dir.exists():
            shutil.copytree(session_dir, backup_dir / "sessions_before_restore")
        
        logger.info(f"📦 Created pre-restore backup at {backup_dir}")
    
    async def _restore_files(self, temp_dir: Path):
        """Restore files from extracted backup"""
        from config import settings
        
        db_backup = temp_dir / "amoria.db"
        if db_backup.exists():
            db_path = settings.database.path
            db_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(db_backup, db_path)
            logger.info("✅ Database restored")
        
        session_backup = temp_dir / "sessions"
        if session_backup.exists():
            session_dir = settings.identity.session_dir
            if session_dir.exists():
                shutil.rmtree(session_dir)
            shutil.copytree(session_backup, session_dir)
            logger.info("✅ Sessions restored")
        
        memory_backup = temp_dir / "memory"
        if memory_backup.exists():
            memory_dir = settings.memory.memory_dir
            if memory_dir.exists():
                shutil.rmtree(memory_dir)
            shutil.copytree(memory_backup, memory_dir)
            logger.info("✅ Memory restored")


__all__ = ['RecoveryManager']
