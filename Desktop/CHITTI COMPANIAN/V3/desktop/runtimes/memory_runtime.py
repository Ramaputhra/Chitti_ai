import asyncio
import sqlite3
import json
import time
from typing import List, Optional, Any, Dict

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.app.context import KernelContext
from desktop.models.memory import Episode, Fact, FactStatus, MemorySource
from desktop.models.memory_index import MemoryIndexManager
from desktop.platform.core.memory_providers import SQLiteIndex

from desktop.models.events import SystemEvent

class MemoryEvent(SystemEvent):
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data

class MemoryRuntime(IRuntime):
    """
    Core Intelligence Subsystem (Rule 15).
    Three layers:
    1. Episodes (Raw History, Immutable)
    2. Facts (Semantic Knowledge, Planner-approved, Provenance)
    3. Embeddings (Disposable Index - Placeholder in MVP)
    """
    def __init__(self, db_path: str = "storage/chitti_memory.db"):
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._running = False
        self.context: Optional[KernelContext] = None
        from desktop.runtimes.memory.retrieval_engine import MemoryRetrievalEngine
        from desktop.runtimes.memory.learning_engine import MemoryLearningEngine
        self._index_manager = MemoryIndexManager(SQLiteIndex(db_path))
        self.retrieval_engine = MemoryRetrievalEngine()
        self.learning_engine = MemoryLearningEngine()

    @property
    def dependencies(self):
        return []

    def health(self) -> HealthState:
        return HealthState.HEALTHY
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Layer 1: Episodes
            conn.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    content TEXT,
                    source TEXT,
                    correlation_id TEXT,
                    metadata TEXT
                )
            ''')
            # Phase 3 Canonical Episodes
            conn.execute('''
                CREATE TABLE IF NOT EXISTS phase3_episodes (
                    episode_id TEXT PRIMARY KEY,
                    intent_type TEXT,
                    timestamp REAL,
                    version TEXT,
                    payload_json TEXT
                )
            ''')
            # Layer 2: Facts
            conn.execute('''
                CREATE TABLE IF NOT EXISTS facts (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    subject TEXT,
                    predicate TEXT,
                    value TEXT,
                    confidence REAL,
                    source_episode_id TEXT,
                    source_type TEXT,
                    status TEXT,
                    superseded_by TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            ''')
            # Layer 2.5: Relationships
            conn.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_id TEXT,
                    target_id TEXT,
                    relationship_type TEXT
                )
            ''')
            # Layer 3: Activity Memory (Session State)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activity_memory (
                    activity_id TEXT PRIMARY KEY,
                    domain TEXT,
                    application TEXT,
                    workspace_path TEXT,
                    project_name TEXT,
                    launch_command TEXT,
                    readiness TEXT,
                    browser_url TEXT,
                    git_branch TEXT,
                    last_active REAL,
                    resume_priority INTEGER,
                    verification TEXT,
                    state TEXT DEFAULT 'PAUSED',
                    resume_confidence REAL DEFAULT 1.0,
                    observer_health TEXT DEFAULT '[]',
                    schema_version INTEGER DEFAULT 1
                )
            ''')
            # V1.1 Migration (ignoring errors if columns already exist)
            try:
                conn.execute('ALTER TABLE activity_memory ADD COLUMN state TEXT DEFAULT "PAUSED"')
                conn.execute('ALTER TABLE activity_memory ADD COLUMN resume_confidence REAL DEFAULT 1.0')
                conn.execute('ALTER TABLE activity_memory ADD COLUMN observer_health TEXT DEFAULT "[]"')
                conn.execute('ALTER TABLE activity_memory ADD COLUMN schema_version INTEGER DEFAULT 1')
            except sqlite3.OperationalError:
                pass # Columns likely already exist
                
            # Layer 4: Conversation History
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp REAL
                )
            ''')

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        self._init_db()
        return True
        
    async def start(self):
        self._running = True
        
    async def stop(self):
        self._running = False
            
    async def shutdown(self):
        pass

    async def _publish(self, event_name: str, data: dict):
        if self.context and self.context.event_bus:
            self.context.event_bus.publish(MemoryEvent(event_name, data))

    # --- Layer 1: Episodes ---
    
    async def commit_episode(self, episode: Episode):
        """Saves immutable history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO episodes 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                episode.id, episode.timestamp, episode.content,
                episode.source, episode.correlation_id, json.dumps(episode.metadata)
            ))
        await self._publish("EpisodeCommittedEvent", {"episode_id": episode.id})
            
    def search_episodes(self, query: str, limit: int = 5) -> List[Episode]:
        """Delegates to active IMemoryIndex provider."""
        return self._index_manager.provider.search_episodes(query, limit)

    # --- Layer 2: Facts ---
    
    async def commit_fact(self, fact: Fact):
        """Saves Planner-approved semantic knowledge."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO facts 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fact.id, fact.type, fact.subject, fact.predicate, fact.value,
                fact.confidence, fact.source_episode_id, fact.source_type.value,
                fact.status.value, fact.superseded_by, fact.created_at, fact.updated_at
            ))
        await self._publish("FactCommittedEvent", {"fact_id": fact.id, "type": fact.type})

    async def update_fact(self, old_fact_id: str, new_fact: Fact):
        """Facts are not deleted. They are superseded."""
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE facts SET status = 'SUPERSEDED', superseded_by = ?, updated_at = ?
                WHERE id = ?
            ''', (new_fact.id, now, old_fact_id))
            
        # Commit the new fact
        await self.commit_fact(new_fact)
        await self._publish("FactSupersededEvent", {"old_fact_id": old_fact_id, "new_fact_id": new_fact.id})

    async def archive_fact(self, fact_id: str):
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE facts SET status = 'ARCHIVED', updated_at = ?
                WHERE id = ?
            ''', (now, fact_id))
        await self._publish("FactArchivedEvent", {"fact_id": fact_id})

    def search_facts(self, query: str, limit: int = 5) -> List[Fact]:
        """Delegates to active IMemoryIndex provider."""
        return self._index_manager.provider.search_facts(query, limit)
        
    # --- Unified Retrieval ---
    
    async def retrieve(self, query: str, sources: List[MemorySource], limit: int = 5) -> List[Any]:
        """
        Retrieval logic returning MemoryResult objects.
        """
        from desktop.models.memory import MemoryResult
        results = []
        now = time.time()
        
        if MemorySource.EPISODES in sources:
            episodes = self.search_episodes(query, limit)
            for ep in episodes:
                results.append(MemoryResult(
                    score=1.0, # Placeholder
                    source=MemorySource.EPISODES,
                    episode_id=ep.id,
                    last_accessed=now,
                    data=ep.__dict__
                ))
                
        if MemorySource.FACTS in sources:
            facts = self.search_facts(query, limit)
            for f in facts:
                results.append(MemoryResult(
                    score=1.0, # Placeholder
                    source=MemorySource.FACTS,
                    fact_id=f.id,
                    confidence=f.confidence,
                    last_accessed=now,
                    data=f.__dict__
                ))
                
        await self._publish("RecallPerformedEvent", {"query": query, "results_count": len(results)})
        return results

    # --- Layer 3: Activity Memory ---
    
    async def commit_activity(self, activity: Any):
        """Persists an ActivityMemoryModel."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO activity_memory 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity.activity_id, activity.domain, activity.application,
                activity.workspace_path, activity.project_name, activity.launch_command,
                activity.readiness, activity.browser_url, activity.git_branch,
                activity.last_active.timestamp() if hasattr(activity.last_active, 'timestamp') else time.time(), 
                activity.resume_priority, json.dumps(activity.verification),
                activity.state.value if hasattr(activity.state, 'value') else activity.state,
                activity.resume_confidence,
                json.dumps([{"observer": o.observer, "healthy": o.healthy, "reason": o.reason, "timestamp": o.timestamp.isoformat()} for o in activity.observer_health]),
                activity.schema_version
            ))
        await self._publish("ActivityCommittedEvent", {"activity_id": activity.activity_id})

    def get_latest_activity(self, domain: Optional[str] = None) -> Optional[Any]:
        """Retrieves the most recent ActivityMemoryModel."""
        from desktop.models.companion import ActivityMemoryModel
        import datetime
        def parse_observers(health_str):
            try:
                from desktop.models.companion import ObserverStatus
                import datetime
                raw = json.loads(health_str)
                return [ObserverStatus(observer=o['observer'], healthy=o['healthy'], reason=o['reason'], timestamp=datetime.datetime.fromisoformat(o['timestamp'])) for o in raw]
            except Exception:
                return []

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if domain:
                cursor = conn.execute('SELECT * FROM activity_memory WHERE domain = ? ORDER BY last_active DESC LIMIT 1', (domain,))
            else:
                cursor = conn.execute('SELECT * FROM activity_memory ORDER BY last_active DESC LIMIT 1')
            row = cursor.fetchone()
            
            if row:
                from desktop.models.companion import ActivityState
                return ActivityMemoryModel(
                    activity_id=row['activity_id'],
                    domain=row['domain'],
                    application=row['application'],
                    workspace_path=row['workspace_path'],
                    project_name=row['project_name'],
                    launch_command=row['launch_command'],
                    readiness=row['readiness'],
                    browser_url=row['browser_url'],
                    git_branch=row['git_branch'],
                    last_active=datetime.datetime.fromtimestamp(row['last_active']),
                    resume_priority=row['resume_priority'],
                    verification=json.loads(row['verification']) if row['verification'] else {},
                    state=ActivityState(row['state']) if row['state'] else ActivityState.PAUSED,
                    resume_confidence=row['resume_confidence'] if 'resume_confidence' in row.keys() else 1.0,
                    observer_health=parse_observers(row['observer_health']) if 'observer_health' in row.keys() and row['observer_health'] else [],
                    schema_version=row['schema_version'] if 'schema_version' in row.keys() else 1
                )
        return None
        
    # --- Layer 4: Conversation History ---
    def append_message_to_history(self, session_id: str, role: str, content: str):
        import time
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO conversation_turns (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, time.time()))
            
    def load_recent_history(self, session_id: str, limit: int = 20) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT role, content FROM conversation_turns 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            # Reverse to chronological order
            history = [{"role": row[0], "content": row[1]} for row in reversed(rows)]
            return history
        
    # --- IMemoryService Interface — CID-003 Fix (RSM-1) ---
    def snapshot(self, session_id: str, workflow_id: str) -> 'MemorySnapshot':
        """
        Builds a real MemorySnapshot from SQLite storage (IMemoryService).

        CID-003 Resolution (RSM-1): Previously this was a stub that always
        returned records=[] and working_memory={}, causing the PlannerRuntime
        to plan with zero memory context.

        This implementation queries:
          - Layer 4: Recent conversation turns (recent_interactions)
          - Layer 2: Active facts (facts)
          - Layer 1: Recent episodes (episodes)
          - Layer 2.5: Knowledge graph relationships (relationships)

        Rule 85: Context is a read-only projection. This method never writes.
        Rule 36: Memory reads are cheap, writes are explicit.
        """
        from desktop.models.memory import (
            MemorySnapshot, InteractionRecord, FactRecord,
            EpisodeRecord, RelationshipRecord, SessionState
        )

        # --- Layer 4: Recent Conversation Turns (last 20 turns) ---
        recent_interactions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT rowid, role, content, timestamp FROM conversation_turns '
                    'WHERE session_id = ? ORDER BY timestamp DESC LIMIT 20',
                    (session_id,)
                )
                rows = cursor.fetchall()
                for i, row in enumerate(reversed(rows)):
                    recent_interactions.append(InteractionRecord(
                        interaction_id=f"{session_id}_turn_{row['rowid']}",
                        session_id=session_id,
                        role=row['role'],
                        content=row['content'],
                        timestamp=row['timestamp'],
                        metadata={}
                    ))
        except Exception as e:
            logger_mem = __import__('logging').getLogger(__name__)
            logger_mem.warning(f"[MemoryRuntime.snapshot] Error reading conversation turns: {e}")

        # --- Layer 2: Active Facts (confidence > 0.5, status = ACTIVE) ---
        facts = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT id, type, subject, predicate, value, confidence, "
                    "source_type, status FROM facts "
                    "WHERE status = 'ACTIVE' ORDER BY confidence DESC LIMIT 50"
                )
                for row in cursor.fetchall():
                    facts.append(FactRecord(
                        id=row['id'],
                        type=row['type'],
                        subject=row['subject'],
                        predicate=row['predicate'],
                        value=row['value'],
                        confidence=row['confidence'],
                        source_type=row['source_type'],
                        status=row['status']
                    ))
        except Exception as e:
            logger_mem = __import__('logging').getLogger(__name__)
            logger_mem.warning(f"[MemoryRuntime.snapshot] Error reading facts: {e}")

        # --- Layer 1: Recent Episodes (last 10) ---
        episodes = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT id, timestamp, content, source, correlation_id, metadata '
                    'FROM episodes ORDER BY timestamp DESC LIMIT 10'
                )
                for row in cursor.fetchall():
                    meta = {}
                    try:
                        meta = json.loads(row['metadata']) if row['metadata'] else {}
                    except Exception:
                        pass
                    episodes.append(EpisodeRecord(
                        id=row['id'],
                        timestamp=row['timestamp'],
                        content=row['content'],
                        source=row['source'],
                        correlation_id=row['correlation_id'],
                        metadata=meta
                    ))
        except Exception as e:
            logger_mem = __import__('logging').getLogger(__name__)
            logger_mem.warning(f"[MemoryRuntime.snapshot] Error reading episodes: {e}")

        # --- Layer 2.5: Relationships ---
        relationships = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT id, source_id, target_id, relationship_type FROM relationships LIMIT 100'
                )
                for row in cursor.fetchall():
                    relationships.append(RelationshipRecord(
                        id=row['id'],
                        source_id=row['source_id'],
                        target_id=row['target_id'],
                        relationship_type=row['relationship_type']
                    ))
        except Exception as e:
            logger_mem = __import__('logging').getLogger(__name__)
            logger_mem.warning(f"[MemoryRuntime.snapshot] Error reading relationships: {e}")

        # COG-31A: Memory Retrieval & Selection Engine Two-Stage Pipeline
        episode_hints = []
        try:
            pool_limit = getattr(self.retrieval_engine.config, "candidate_pool_limit", 50)
            phase3_candidates = self.get_phase3_episodes(limit=pool_limit)
            
            # Interaction object constructed for retrieval scoring
            dummy_interaction = None
            if recent_interactions:
                from desktop.models.interaction import InteractionEnvelope
                last_turn = recent_interactions[-1]
                dummy_interaction = InteractionEnvelope(
                    id=last_turn.interaction_id,
                    session_id=session_id,
                    timestamp=time.time(),
                    origin="CLI",
                    transport="CLI",
                    payload=last_turn.content
                )
            elif phase3_candidates:
                from desktop.models.interaction import InteractionEnvelope
                cand_intent = getattr(phase3_candidates[0], "intent", {})
                payload_str = cand_intent.get("query", "") if isinstance(cand_intent, dict) else getattr(cand_intent, "query", "")
                dummy_interaction = InteractionEnvelope(
                    id=f"{session_id}_auto",
                    session_id=session_id,
                    timestamp=time.time(),
                    origin="CLI",
                    transport="CLI",
                    payload=payload_str or "default query"
                )

            if phase3_candidates and dummy_interaction:
                episode_hints = self.retrieval_engine.retrieve_hints(dummy_interaction, phase3_candidates)
        except Exception as e:
            logger_mem = __import__('logging').getLogger(__name__)
            logger_mem.warning(f"[MemoryRuntime.snapshot] Error in COG-31A MemoryRetrievalEngine: {e}")

        snapshot = MemorySnapshot(
            session_id=session_id,
            workflow_id=workflow_id,
            session_state=SessionState.ACTIVE,
            recent_interactions=recent_interactions,
            working_memory=[],          # Working memory is workflow-scoped; provided on demand
            facts=facts,
            episodes=episodes,
            relationships=relationships,
            records=recent_interactions  # Legacy compatibility for planner_contracts.py
        )
        snapshot.episode_hints = episode_hints
        return snapshot

    def save_phase3_episode(self, episode: Episode) -> bool:
        """
        Saves a canonical Phase 3 Episode instance into durable storage.
        """
        try:
            payload = json.dumps(episode.to_dict())
            intent_type = "unknown"
            if isinstance(episode.intent, dict):
                intent_type = episode.intent.get("subtype", "unknown")
            elif hasattr(episode.intent, "subtype"):
                intent_type = episode.intent.subtype
            elif isinstance(episode.intent, str):
                intent_type = episode.intent

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO phase3_episodes (episode_id, intent_type, timestamp, version, payload_json)
                    VALUES (?, ?, ?, ?, ?)
                ''', (episode.episode_id, intent_type, episode.timestamp, episode.version, payload))
            return True
        except Exception as e:
            return False

    def get_phase3_episode(self, episode_id: str) -> Optional[Episode]:
        """
        Retrieves a canonical Phase 3 Episode instance from durable storage.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT payload_json FROM phase3_episodes WHERE episode_id = ?", (episode_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    data = json.loads(row[0])
                    return Episode.from_dict(data)
            return None
        except Exception as e:
            return None

    def get_phase3_episodes(self, limit: int = 50) -> List[Episode]:
        """
        Stage 1 Cheap Fetch: Reads up to limit Phase 3 Episode objects from SQLite storage.
        """
        episodes = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT payload_json FROM phase3_episodes ORDER BY timestamp DESC LIMIT ?", (limit,))
                for row in cursor.fetchall():
                    if row and row[0]:
                        try:
                            episodes.append(Episode.from_dict(json.loads(row[0])))
                        except Exception:
                            pass
        except Exception as e:
            pass
        return episodes

    def delete_phase3_episode(self, episode_id: str) -> bool:
        """
        COG-31F: Removes an untrusted episode from Cognitive Memory when its retention threshold is crossed (S < 0.10).
        Cognitive Memory contains ONLY trusted, reusable experiences.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM phase3_episodes WHERE episode_id = ?", (episode_id,))
            return True
        except Exception as e:
            return False

    def process_execution_learning(self, episode: Episode, is_success: bool, latency_ms: float) -> Dict[str, Any]:
        """
        COG-31F: Asynchronous learning processing triggered by ExecutionCompletedEvent.
        Delegates to internal MemoryLearningEngine to evolve metadata and update SQLite storage.
        """
        outcome = self.learning_engine.process_execution_outcome(episode, is_success, latency_ms)
        
        if outcome["should_remove"]:
            self.delete_phase3_episode(episode.episode_id)
        else:
            # Update Episode metadata without rewriting historical Episode content
            episode.episode_score = outcome["updated_score"]
            episode.episode_quality = outcome["updated_quality"]
            self.save_phase3_episode(episode)
            
        return outcome

