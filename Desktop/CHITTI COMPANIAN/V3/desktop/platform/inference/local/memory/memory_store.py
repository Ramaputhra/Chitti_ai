import sqlite3
import json
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from desktop.platform.shared.models.knowledge import Entity, KnowledgeEdge, FactSource
from desktop.platform.shared.models.memory import Memory, MemoryCategory, MemoryStatus
from desktop.platform.shared.models.provenance import Provenance

class MemoryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def transaction(self):
        """
        Provides a transaction context manager.
        Usage:
            with memory_store.transaction() as cursor:
                cursor.execute(...)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn.cursor()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self.transaction() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    canonical_name TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    aliases TEXT,
                    confidence REAL,
                    created_at REAL,
                    updated_at REAL,
                    metadata TEXT,
                    provenance TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_edges (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship TEXT NOT NULL,
                    source TEXT,
                    created_by TEXT,
                    confidence REAL,
                    created_at REAL,
                    provenance TEXT,
                    metadata TEXT,
                    FOREIGN KEY (source_id) REFERENCES entities (id),
                    FOREIGN KEY (target_id) REFERENCES entities (id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    knowledge_ids TEXT,
                    status TEXT,
                    intelligence_score REAL,
                    source TEXT,
                    created_by TEXT,
                    created_at REAL,
                    updated_at REAL,
                    provenance TEXT,
                    metadata TEXT
                )
            """)
            
            # Indexes for faster resolution
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_canonical ON entities(canonical_name, entity_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON knowledge_edges(source_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON knowledge_edges(target_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status)")

    # --- Entity Methods ---

    def save_entity(self, entity: Entity) -> None:
        with self.transaction() as cursor:
            self._save_entity_cursor(cursor, entity)
            
    def _save_entity_cursor(self, cursor, entity: Entity) -> None:
        cursor.execute(
            """
            INSERT INTO entities (id, canonical_name, display_name, entity_type, aliases, confidence, created_at, updated_at, metadata, provenance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                canonical_name = excluded.canonical_name,
                display_name = excluded.display_name,
                entity_type = excluded.entity_type,
                aliases = excluded.aliases,
                confidence = excluded.confidence,
                updated_at = excluded.updated_at,
                metadata = excluded.metadata,
                provenance = excluded.provenance
            """,
            (
                entity.id,
                entity.canonical_name,
                entity.display_name,
                entity.entity_type,
                json.dumps(entity.aliases),
                entity.confidence,
                entity.created_at,
                entity.updated_at,
                json.dumps(entity.metadata),
                json.dumps(entity.provenance.__dict__) if entity.provenance else None
            )
        )

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_entity(row)
        return None

    def get_entity_by_canonical_name(self, canonical_name: str, entity_type: str) -> Optional[Entity]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entities WHERE canonical_name = ? AND entity_type = ?", (canonical_name, entity_type))
            row = cursor.fetchone()
            if row:
                return self._row_to_entity(row)
        return None

    def _row_to_entity(self, row) -> Entity:
        prov_dict = json.loads(row[9]) if row[9] else None
        provenance = Provenance(**prov_dict) if prov_dict else None
        return Entity(
            id=row[0],
            canonical_name=row[1],
            display_name=row[2],
            entity_type=row[3],
            aliases=json.loads(row[4]) if row[4] else [],
            confidence=row[5],
            created_at=row[6],
            updated_at=row[7],
            metadata=json.loads(row[8]) if row[8] else {},
            provenance=provenance
        )

    # --- Knowledge Edge Methods ---

    def save_edge(self, edge: KnowledgeEdge) -> None:
        with self.transaction() as cursor:
            self._save_edge_cursor(cursor, edge)
            
    def _save_edge_cursor(self, cursor, edge: KnowledgeEdge) -> None:
        cursor.execute(
            """
            INSERT INTO knowledge_edges (id, source_id, target_id, relationship, source, created_by, confidence, created_at, provenance, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                source_id = excluded.source_id,
                target_id = excluded.target_id,
                relationship = excluded.relationship,
                source = excluded.source,
                created_by = excluded.created_by,
                confidence = excluded.confidence,
                provenance = excluded.provenance,
                metadata = excluded.metadata
            """,
            (
                edge.id,
                edge.source_id,
                edge.target_id,
                edge.relationship,
                edge.source.value,
                edge.created_by,
                edge.confidence,
                edge.created_at,
                json.dumps(edge.provenance.__dict__) if edge.provenance else None,
                json.dumps(edge.metadata)
            )
        )

    def get_edges_for_entity(self, entity_id: str) -> List[KnowledgeEdge]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM knowledge_edges WHERE source_id = ? OR target_id = ?", (entity_id, entity_id))
            rows = cursor.fetchall()
            return [self._row_to_edge(row) for row in rows]

    def _row_to_edge(self, row) -> KnowledgeEdge:
        prov_dict = json.loads(row[8]) if row[8] else None
        provenance = Provenance(**prov_dict) if prov_dict else None
        return KnowledgeEdge(
            id=row[0],
            source_id=row[1],
            target_id=row[2],
            relationship=row[3],
            source=FactSource(row[4]) if row[4] else FactSource.PLANNER,
            created_by=row[5],
            confidence=row[6],
            created_at=row[7],
            provenance=provenance,
            metadata=json.loads(row[9]) if row[9] else {}
        )

    # --- Memory Methods ---

    def save_memory(self, memory: Memory) -> None:
        with self.transaction() as cursor:
            self._save_memory_cursor(cursor, memory)
            
    def _save_memory_cursor(self, cursor, memory: Memory) -> None:
        cursor.execute(
            """
            INSERT INTO memories (id, content, category, knowledge_ids, status, intelligence_score, source, created_by, created_at, updated_at, provenance, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                content = excluded.content,
                category = excluded.category,
                knowledge_ids = excluded.knowledge_ids,
                status = excluded.status,
                intelligence_score = excluded.intelligence_score,
                source = excluded.source,
                created_by = excluded.created_by,
                updated_at = excluded.updated_at,
                provenance = excluded.provenance,
                metadata = excluded.metadata
            """,
            (
                memory.id,
                memory.content,
                memory.category.value,
                json.dumps(memory.knowledge_ids),
                memory.status.value,
                memory.intelligence_score,
                memory.source.value,
                memory.created_by,
                memory.created_at,
                memory.updated_at,
                json.dumps(memory.provenance.__dict__) if memory.provenance else None,
                json.dumps(memory.metadata)
            )
        )

    def get_memories_by_category(self, category: MemoryCategory) -> List[Memory]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE category = ? AND status != 'Archived'", (category.value,))
            rows = cursor.fetchall()
            return [self._row_to_memory(row) for row in rows]

    def search_memories(self, query: str) -> List[Memory]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Simple LIKE search for now
            cursor.execute("SELECT * FROM memories WHERE content LIKE ? AND status != 'Archived'", (f"%{query}%",))
            rows = cursor.fetchall()
            return [self._row_to_memory(row) for row in rows]

    def _row_to_memory(self, row) -> Memory:
        prov_dict = json.loads(row[10]) if row[10] else None
        provenance = Provenance(**prov_dict) if prov_dict else None
        return Memory(
            id=row[0],
            content=row[1],
            category=MemoryCategory(row[2]),
            knowledge_ids=json.loads(row[3]) if row[3] else [],
            status=MemoryStatus(row[4]),
            intelligence_score=row[5],
            source=FactSource(row[6]) if row[6] else FactSource.PLANNER,
            created_by=row[7],
            created_at=row[8],
            updated_at=row[9],
            provenance=provenance,
            metadata=json.loads(row[11]) if row[11] else {}
        )
