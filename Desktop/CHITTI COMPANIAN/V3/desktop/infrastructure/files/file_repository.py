import sqlite3
import os
import hashlib
from typing import List, Dict, Any, Optional
from enum import Enum
import time

class FileState(Enum):
    ACTIVE = "ACTIVE"
    MISSING = "MISSING"
    MOVED = "MOVED"
    DELETED = "DELETED"
    IGNORED = "IGNORED"

class KnowledgeStatus(Enum):
    NOT_ANALYZED = "NOT_ANALYZED"
    PARSED = "PARSED"
    INDEXED = "INDEXED"
    SUMMARIZED = "SUMMARIZED"
    EMBEDDED = "EMBEDDED"
    STALE = "STALE"

class FileRepository:
    """
    Abstracted File Intelligence repository backing the local Hybrid Search.
    Follows Rule 8 (Local Knowledge First) by decoupling from raw Windows queries.
    """
    def __init__(self, db_path: str = "chitti_files.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_index (
                    path TEXT PRIMARY KEY,
                    filename TEXT,
                    extension TEXT,
                    parent_folder TEXT,
                    identity_hash TEXT,
                    state TEXT,
                    knowledge_status TEXT DEFAULT 'NOT_ANALYZED',
                    created_at REAL,
                    modified_at REAL,
                    last_opened REAL,
                    last_seen REAL,
                    size INTEGER,
                    tags TEXT,
                    frequency INTEGER DEFAULT 0
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_aliases (
                    alias TEXT PRIMARY KEY,
                    path TEXT
                )
            ''')
            
    def _compute_hash(self, path: str) -> Optional[str]:
        # For MVP, lightweight hash based on size and mtime to avoid reading full huge files
        try:
            stat = os.stat(path)
            h = hashlib.md5()
            h.update(f"{stat.st_size}_{stat.st_mtime}".encode())
            return h.hexdigest()
        except OSError:
            return None

    def exists(self, path: str) -> bool:
        """API requirement: Checks if the file actively exists on disk."""
        return os.path.exists(path)
        
    def refresh_index(self, path: str):
        """API requirement: Add or update a file in the index."""
        if not self.exists(path):
            self._mark_missing(path)
            return
            
        stat = os.stat(path)
        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].lower()
        parent = os.path.dirname(path)
        identity = self._compute_hash(path)
        now = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO file_index (
                    path, filename, extension, parent_folder, identity_hash, state,
                    created_at, modified_at, last_seen, size, tags, frequency
                ) VALUES (
                    ?, ?, ?, ?, ?, 'ACTIVE',
                    ?, ?, ?, ?, '', COALESCE((SELECT frequency FROM file_index WHERE path = ?), 0)
                )
            ''', (
                path, filename, ext, parent, identity,
                stat.st_ctime, stat.st_mtime, now, stat.st_size, path
            ))
            
    def refresh_all(self):
        """API requirement: Scan indexed files for missing/moved status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT path, identity_hash FROM file_index WHERE state = 'ACTIVE'")
            rows = cursor.fetchall()
            
        for path, old_hash in rows:
            if not self.exists(path):
                # Mark missing. In a real system, we'd scan for the hash elsewhere to mark MOVED
                self._mark_missing(path)
                
    def _mark_missing(self, path: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE file_index SET state = 'MISSING' WHERE path = ?", (path,))

    def mark_opened(self, path: str):
        """Updates frequency of use."""
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE file_index 
                SET frequency = frequency + 1, last_opened = ?, last_seen = ? 
                WHERE path = ?
            """, (now, now, path))

    def remember_alias(self, alias: str, path: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO file_aliases (alias, path) VALUES (?, ?)", (alias.lower(), path))
            
    def remove_alias(self, alias: str):
        """API requirement."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM file_aliases WHERE alias = ?", (alias.lower(),))

    def resolve_alias(self, alias: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT path FROM file_aliases WHERE alias = ?", (alias.lower(),))
            row = cursor.fetchone()
            return row[0] if row else None

    def update_knowledge_status(self, path: str, status: KnowledgeStatus):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE file_index SET knowledge_status = ? WHERE path = ?", (status.value, path))

    def get_all_active_files(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM file_index WHERE state = 'ACTIVE'")
            return [dict(row) for row in cursor.fetchall()]
