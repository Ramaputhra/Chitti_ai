from typing import Dict, Any, List, Optional
import sqlite3
import json

class MemoryRuntime:
    """
    Pure infrastructure layer for Cognitive Memory.
    Owns SQLite persistence, retrieval, and indices.
    Zero cognitive reasoning.
    """
    def __init__(self, db_path: str = "chitti_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        import contextlib
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_episodes (
                    episode_id TEXT PRIMARY KEY,
                    source_experience_id TEXT,
                    semantic_summary TEXT,
                    importance_score REAL,
                    retention_policy TEXT,
                    metadata_json TEXT,
                    state TEXT,
                    full_payload_json TEXT
                )
            ''')
            # Temporal and Spatial index
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON memory_episodes(source_experience_id)')
            conn.commit()

    def persist(self, episode_dict: Dict[str, Any]) -> str:
        """
        Ingests a READY_FOR_PERSISTENCE MemoryEpisode.
        """
        episode_id = episode_dict.get('identity', {}).get('episode_id', 'unknown')
        source_id = episode_dict.get('identity', {}).get('source_experience_id', '')
        summary = episode_dict.get('semantic_summary', '')
        score = episode_dict.get('importance_score', 0.5)
        policy = str(episode_dict.get('retention_policy', 'LONG_TERM'))
        metadata = json.dumps(episode_dict.get('metadata', {}))
        full_payload = json.dumps(episode_dict)
        
        import contextlib
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO memory_episodes 
                (episode_id, source_experience_id, semantic_summary, importance_score, retention_policy, metadata_json, state, full_payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (episode_id, source_id, summary, score, policy, metadata, "INDEXED", full_payload))
            conn.commit()
        
        return episode_id

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Basic retrieval via string matching (simulating FTS/metadata filters).
        """
        import contextlib
        results = []
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT episode_id, semantic_summary, state, full_payload_json
                FROM memory_episodes 
                WHERE semantic_summary LIKE ?
            ''', (f'%{query}%',))
            for row in cursor.fetchall():
                payload = json.loads(row[3]) if row[3] else {}
                results.append({
                    "episode_id": row[0],
                    "summary": row[1],
                    "state": row[2],
                    "full_payload": payload
                })
        return results

    def forget(self, episode_id: str):
        """Hard deletion of a memory."""
        import contextlib
        with contextlib.closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM memory_episodes WHERE episode_id = ?', (episode_id,))
            conn.commit()
