# backup/verify.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Backup Verification System
=============================================================================
"""

import zipfile
import hashlib
import json
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BackupVerifier:
    """Verifikasi integritas backup files"""
    
    def __init__(self):
        self.checksum_algo = hashlib.sha256
    
    async def verify_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Verify backup file integrity"""
        if not backup_path.exists():
            return {"valid": False, "error": "File not found", "filename": backup_path.name}
        
        result = {
            "filename": backup_path.name,
            "size_bytes": backup_path.stat().st_size,
            "size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2),
            "checks": {}
        }
        
        zip_check = await self._check_zip_integrity(backup_path)
        result["checks"]["zip_integrity"] = zip_check
        if not zip_check["valid"]:
            result["valid"] = False
            result["error"] = "ZIP file corrupted"
            return result
        
        metadata_check = await self._check_metadata(backup_path)
        result["checks"]["metadata"] = metadata_check
        
        structure_check = await self._check_file_structure(backup_path)
        result["checks"]["structure"] = structure_check
        
        result["checksum"] = await self._calculate_checksum(backup_path)
        
        result["valid"] = (
            zip_check["valid"] and
            metadata_check["valid"] and
            structure_check["valid"]
        )
        
        if result["valid"]:
            result["files"] = structure_check["files"]
            result["metadata"] = metadata_check["metadata"]
        
        return result
    
    async def _check_zip_integrity(self, zip_path: Path) -> Dict:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                bad_file = zipf.testzip()
                if bad_file:
                    return {"valid": False, "error": f"Corrupted file: {bad_file}"}
                return {"valid": True, "file_count": len(zipf.namelist())}
        except zipfile.BadZipFile as e:
            return {"valid": False, "error": f"Bad ZIP file: {e}"}
    
    async def _check_metadata(self, zip_path: Path) -> Dict:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if 'metadata.json' not in zipf.namelist():
                    return {"valid": False, "error": "metadata.json not found"}
                
                with zipf.open('metadata.json') as f:
                    metadata = json.loads(f.read().decode('utf-8'))
                
                required = ['created_at', 'version']
                missing = [f for f in required if f not in metadata]
                if missing:
                    return {"valid": False, "error": f"Missing fields: {missing}"}
                
                return {"valid": True, "metadata": metadata}
                
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def _check_file_structure(self, zip_path: Path) -> Dict:
        required_files = ['amoria.db', 'metadata.json']
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                files = zipf.namelist()
                missing = [req for req in required_files if req not in files]
                if missing:
                    return {"valid": False, "error": f"Missing: {missing}"}
                
                return {"valid": True, "files": len(files)}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def format_verify_result(self, result: Dict) -> str:
        """Format verification result for display"""
        if not result["valid"]:
            return f"❌ **Backup corrupted:** {result['filename']}\nError: {result.get('error', 'Unknown')}"
        
        lines = [f"✅ **Backup valid:** {result['filename']}", f"Size: {result['size_mb']} MB"]
        
        if "metadata" in result:
            meta = result["metadata"]
            created = datetime.fromtimestamp(meta['created_at']).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"Created: {created}")
        
        if "files" in result:
            lines.append(f"Total files: {result['files']}")
        
        return "\n".join(lines)


__all__ = ['BackupVerifier']
