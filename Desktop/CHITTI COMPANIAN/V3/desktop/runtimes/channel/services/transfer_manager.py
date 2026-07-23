import hashlib
import os
import time
from typing import Dict, Optional
from desktop.runtimes.channel.models.core import TransferState

class FileTransferRecord:
    def __init__(self, file_path: str, artifact_id: str):
        self.file_path = file_path
        self.artifact_id = artifact_id
        self.state = TransferState.QUEUED
        self.bytes_transferred = 0
        self.total_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.sha256 = self._calculate_hash()
        self.expires_at = time.time() + (24 * 3600) # 24 hour expiration
        
    def _calculate_hash(self) -> str:
        if not os.path.exists(self.file_path):
            return ""
        hasher = hashlib.sha256()
        with open(self.file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

class TransferManager:
    """Manages secure, chunked, verifiable file transfers over the LAN."""
    
    def __init__(self, max_transfer_size_mb: int = 500):
        self.max_transfer_size_bytes = max_transfer_size_mb * 1024 * 1024
        self.transfer_queue: Dict[str, FileTransferRecord] = {}
        
    def queue_transfer(self, artifact_id: str, file_path: str) -> Optional[FileTransferRecord]:
        if not os.path.exists(file_path):
            print(f"[TransferManager] Error: File not found {file_path}")
            return None
            
        file_size = os.path.getsize(file_path)
        if file_size > self.max_transfer_size_bytes:
            print(f"[TransferManager] Error: File exceeds {self.max_transfer_size_bytes} bytes")
            return None
            
        record = FileTransferRecord(file_path, artifact_id)
        self.transfer_queue[artifact_id] = record
        print(f"[TransferManager] Queued {artifact_id} ({file_size} bytes, SHA256: {record.sha256})")
        return record
        
    def get_chunk(self, artifact_id: str, offset: int, chunk_size: int = 1024 * 1024) -> Optional[bytes]:
        """Reads a chunk from the file for WebSocket transmission."""
        record = self.transfer_queue.get(artifact_id)
        if not record:
            return None
            
        if time.time() > record.expires_at:
            record.state = TransferState.FAILED
            del self.transfer_queue[artifact_id]
            return None
            
        record.state = TransferState.TRANSFERRING
        
        try:
            with open(record.file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(chunk_size)
                record.bytes_transferred += len(data)
                
                if record.bytes_transferred >= record.total_bytes:
                    record.state = TransferState.COMPLETED
                    
                return data
        except Exception as e:
            record.state = TransferState.FAILED
            print(f"[TransferManager] Transfer failed: {e}")
            return None
