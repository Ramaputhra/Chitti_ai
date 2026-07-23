import sqlite3
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ExperienceDatabase:
    """
    Lightweight SQLite wrapper for the Experience Learning Engine.
    Handles storage and retrieval of successful experiences, patterns, and contexts.
    """
    def __init__(self, db_path: str = "chitti_experiences.db"):
        self.db_path = db_path
        self._initialize_schemas()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_schemas(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Experiences Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experience_version INTEGER DEFAULT 1,
                    supersedes_experience_id INTEGER,
                    command_text TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    capability_id TEXT NOT NULL,
                    parameters TEXT, -- JSON
                    execution_time_ms INTEGER,
                    confidence_score REAL,
                    verified BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            """)
            
            # 2. Experience Context Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experience_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experience_id INTEGER NOT NULL,
                    workspace TEXT,
                    active_project TEXT,
                    running_apps TEXT, -- JSON
                    time_of_day TEXT,
                    display_layout TEXT,
                    user_mode TEXT,
                    FOREIGN KEY(experience_id) REFERENCES experiences(id)
                )
            """)
            
            # 3. Experience Patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experience_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_text TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    capability_id TEXT NOT NULL,
                    confidence_score REAL
                )
            """)
            
            # 4. Experience Stats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experience_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experience_id INTEGER NOT NULL,
                    success_rate REAL DEFAULT 1.0,
                    average_latency_ms REAL,
                    failure_count INTEGER DEFAULT 0,
                    FOREIGN KEY(experience_id) REFERENCES experiences(id)
                )
            """)
            
            # 5. Experience Embeddings (Stubbed for BGE integration)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experience_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experience_id INTEGER NOT NULL,
                    vector BLOB,
                    FOREIGN KEY(experience_id) REFERENCES experiences(id)
                )
            """)
            
            conn.commit()

    def save_experience(self, command: str, intent: str, capability: str, 
                        parameters: Dict[str, Any], context: Dict[str, Any], 
                        confidence: float, execution_time: int) -> int:
        """
        Saves a completely verified and successful experience, along with its context.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exact command exists to increment use_count instead of duplicate
            cursor.execute("SELECT id, use_count FROM experiences WHERE command_text = ? AND intent = ? AND capability_id = ?", 
                           (command, intent, capability))
            row = cursor.fetchone()
            
            if row:
                exp_id = row[0]
                new_count = row[1] + 1
                cursor.execute("""
                    UPDATE experiences 
                    SET use_count = ?, last_used = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (new_count, exp_id))
            else:
                cursor.execute("""
                    INSERT INTO experiences (command_text, intent, capability_id, parameters, execution_time_ms, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (command, intent, capability, json.dumps(parameters), execution_time, confidence))
                exp_id = cursor.lastrowid
                
                # Insert Context
                cursor.execute("""
                    INSERT INTO experience_context (experience_id, workspace, active_project, time_of_day, user_mode)
                    VALUES (?, ?, ?, ?, ?)
                """, (exp_id, context.get("workspace"), context.get("active_project"), 
                      context.get("time_of_day"), context.get("user_mode")))
                
                # Insert Initial Stats
                cursor.execute("""
                    INSERT INTO experience_stats (experience_id, success_rate, average_latency_ms, failure_count)
                    VALUES (?, 1.0, ?, 0)
                """, (exp_id, execution_time))
                
            conn.commit()
            return exp_id

    def find_exact_match(self, command: str) -> Optional[Dict[str, Any]]:
        """Retrieve an exact historical match for a command."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.*, s.success_rate 
                FROM experiences e
                LEFT JOIN experience_stats s ON e.id = s.experience_id
                WHERE e.command_text = ? AND e.verified = 1
                ORDER BY e.use_count DESC, s.success_rate DESC
                LIMIT 1
            """, (command,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def find_pattern_match(self, command: str) -> Optional[Dict[str, Any]]:
        """Stub for semantic pattern extraction."""
        # e.g., mapping 'Open Documents' to 'Open <Folder>' 
        # This will be fully implemented when the BGE/NLP pipeline hooks up.
        return None
