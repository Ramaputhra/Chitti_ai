import sqlite3
import json
from typing import List

from desktop.models.memory import Episode, Fact, FactStatus, FactSourceType
from desktop.models.memory_index import IMemoryIndex

class SQLiteIndex(IMemoryIndex):
    """
    Standard SQLite provider for local memory search using LIKE queries.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path

    def index_episode(self, episode: Episode) -> bool:
        # SQLite indexing is implicitly done upon commit
        return True

    def search_episodes(self, query: str, limit: int = 5) -> List[Episode]:
        episodes = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM episodes 
                WHERE content LIKE ? 
                ORDER BY timestamp DESC LIMIT ?
            """, (f"%{query}%", limit))
            for row in cursor.fetchall():
                episodes.append(Episode(
                    id=row[0], timestamp=row[1], content=row[2],
                    source=row[3], correlation_id=row[4], metadata=json.loads(row[5])
                ))
        return episodes

    def index_fact(self, fact: Fact) -> bool:
        return True

    def search_facts(self, query: str, limit: int = 5) -> List[Fact]:
        facts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM facts 
                WHERE status = 'ACTIVE' AND (subject LIKE ? OR value LIKE ?)
                ORDER BY created_at DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            for row in cursor.fetchall():
                facts.append(Fact(
                    id=row[0], type=row[1], subject=row[2], predicate=row[3], value=row[4],
                    confidence=row[5], source_episode_id=row[6], source_type=FactSourceType(row[7]),
                    status=FactStatus(row[8]), superseded_by=row[9], created_at=row[10], updated_at=row[11]
                ))
        return facts
