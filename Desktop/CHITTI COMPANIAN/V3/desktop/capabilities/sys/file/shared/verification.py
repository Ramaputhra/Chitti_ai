"""
Filesystem Shared Primitive

This module is part of the frozen filesystem infrastructure.
Only functionality proven by at least two capabilities may be added.
Capability-specific logic is prohibited.
"""
import os
import hashlib

def size_matches(path1: str, path2: str) -> bool:
    """Checks if two files have the exact same size in bytes."""
    try:
        return os.path.getsize(path1) == os.path.getsize(path2)
    except OSError:
        return False

def timestamp_matches(path1: str, path2: str, tolerance_seconds: float = 2.0) -> bool:
    """Checks if two files have similar modified timestamps."""
    try:
        t1 = os.path.getmtime(path1)
        t2 = os.path.getmtime(path2)
        return abs(t1 - t2) <= tolerance_seconds
    except OSError:
        return False

def hash_matches(path1: str, path2: str, chunk_size: int = 8192) -> bool:
    """Checks if two files have the identical SHA-256 hash."""
    def get_hash(p: str) -> str:
        h = hashlib.sha256()
        with open(p, 'rb') as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
        
    try:
        return get_hash(path1) == get_hash(path2)
    except OSError:
        return False
