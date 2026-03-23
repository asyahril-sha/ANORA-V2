# backup/automated.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Automated Backup System
=============================================================================
"""

import os
import json
import time
import asyncio
import zipfile
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import settings
from database.connection import get_db
from database.models import Backup, BackupType, BackupStatus

logger = logging.getLogger(__name__)


class AutoBackup:
    """
    Manajer backup otomatis AMORIA
    - Backup database dan file penting
    - Retention 7 hari
    - Kompresi ke ZIP
    """
    
    def __init__(self):
        self.backup_dir = settings.backup.backup_dir
        self.retention_days = settings.backup.retention_days
        self.interval = settings.backup.interval
        self.enabled = settings.backup.enabled
        self.s3_bucket = settings.backup.s3_bucket
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.last_backup_time = None
        self.total_backups = 0
        self.total_size_mb = 0
        self.backup_history = []
        
        self._backup_task = None
        self._running = False
        
        logger.info(f"✅ AutoBackup initialized (dir: {self.backup_dir})")
    
    async def create_backup(self, backup_type: BackupType = BackupType.AUTO) -> Optional[Path]:
        """Create new backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"amoria_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        logger.info(f"📦 Creating backup: {backup_filename}")
        
        try:
            temp_dir = self.backup_dir / f"temp_{timestamp}"
            temp_dir.mkdir(exist_ok=True)
            
            await self._copy_files_to_backup(temp_dir)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
            
            size_bytes = backup_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            sha256 = self._calculate_hash(backup_path)
            
            from database.repository import Repository
            repo = Repository()
            
            backup_record = Backup(
                filename=backup_filename,
                size=int(size_bytes),
                created_at=time.time(),
                type=backup_type,
                status=BackupStatus.COMPLETED,
                metadata={"sha256": sha256}
            )
            
            await repo.add_backup(backup_record)
            
            shutil.rmtree(temp_dir)
            
            self.last_backup_time = time.time()
            self.total_backups += 1
            self.total_size_mb += size_mb
            self.backup_history.append({
                "filename": backup_filename,
                "time": self.last_backup_time,
                "size_mb": round(size_mb, 2)
            })
            
            await self.cleanup_old_backups()
            
            if self.s3_bucket:
                await self.upload_to_s3(backup_path)
                
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return None
    
    async def _copy_files_to_backup(self, temp_dir: Path):
        """Copy all important files to temp directory"""
        from config import settings
        
        db_path = settings.database.path
        if db_path.exists():
            shutil.copy2(db_path, temp_dir / "amoria.db")
        
        session_dir = settings.identity.session_dir
        if session_dir.exists():
            session_backup = temp_dir / "sessions"
            session_backup.mkdir()
            for json_file in session_dir.glob("*.json"):
                shutil.copy2(json_file, session_backup)
        
        memory_dir = settings.memory.memory_dir
        if memory_dir.exists():
            memory_backup = temp_dir / "memory"
            shutil.copytree(memory_dir, memory_backup)
        
        metadata = {
            "created_at": time.time(),
            "version": "1.0.0",
            "backup_type": "full"
        }
        
        with open(temp_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _calculate_hash(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    async def cleanup_old_backups(self, dry_run: bool = False) -> List[str]:
        """Delete backups older than retention_days"""
        cutoff_time = time.time() - (self.retention_days * 86400)
        deleted = []
        
        for backup_file in self.backup_dir.glob("amoria_backup_*.zip"):
            try:
                timestamp_str = backup_file.stem.replace("amoria_backup_", "")
                file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S").timestamp()
                
                if file_time < cutoff_time:
                    if dry_run:
                        logger.info(f"Would delete: {backup_file.name}")
                    else:
                        backup_file.unlink()
                        logger.info(f"🗑️ Deleted old backup: {backup_file.name}")
                    deleted.append(backup_file.name)
            except Exception as e:
                logger.error(f"Error processing {backup_file.name}: {e}")
        
        return deleted
    
    async def upload_to_s3(self, backup_path: Path):
        """Upload backup to S3 bucket"""
        if not self.s3_bucket:
            return
        logger.info(f"☁️ Would upload to S3 bucket {self.s3_bucket}: {backup_path.name}")
    
    async def start_auto_backup(self):
        """Start automatic backup scheduler"""
        if not self.enabled:
            logger.info("⏸️ Auto backup is disabled")
            return
        
        if self._running:
            return
        
        self._running = True
        self._backup_task = asyncio.create_task(self._backup_loop())
        logger.info(f"🔄 Auto backup started (interval: {self.interval} seconds)")
    
    async def stop_auto_backup(self):
        """Stop automatic backup scheduler"""
        self._running = False
        if self._backup_task:
            self._backup_task.cancel()
            try:
                await self._backup_task
            except asyncio.CancelledError:
                pass
        logger.info("🔄 Auto backup stopped")
    
    async def _backup_loop(self):
        while self._running:
            try:
                await self.create_backup(BackupType.AUTO)
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                await asyncio.sleep(3600)
    
    async def get_stats(self) -> Dict:
        """Get backup statistics"""
        from database.repository import Repository
        repo = Repository()
        backups = await repo.get_backups(10)
        
        return {
            "total_backups": len(backups),
            "total_size_mb": self.total_size_mb,
            "last_backup": self.last_backup_time,
            "retention_days": self.retention_days,
            "auto_backup_running": self._running,
            "recent_backups": [
                {"filename": b.filename, "date": datetime.fromtimestamp(b.created_at).strftime("%Y-%m-%d %H:%M"),
                 "size_mb": round(b.size / (1024 * 1024), 2) if b.size else 0}
                for b in backups
            ]
        }


_backup_manager = None


def get_backup_manager() -> AutoBackup:
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = AutoBackup()
    return _backup_manager


__all__ = ['AutoBackup', 'get_backup_manager']
