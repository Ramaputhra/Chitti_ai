import asyncio
import sqlite3
import json
import time
import uuid
from typing import List, Optional, Any, Dict

from desktop.models.lifecycle import IRuntime
from desktop.app.context import KernelContext
from desktop.models.events import SystemEvent
from desktop.models.awareness import AwarenessEvent, AwarenessType, AwarenessLevel

class AwarenessEventPublished(SystemEvent):
    def __init__(self, event: AwarenessEvent):
        super().__init__("AwarenessEventPublished", {"event_id": event.id, "type": event.type.value})
        self.event = event

class AwarenessRuntime(IRuntime):
    """
    Rule 12 (Awareness Is Intentional): Maintains lightweight awareness of the desktop.
    Level 1: Always on (Window, Process, Battery)
    Level 2/3: Ephemeral watchers activated by user or capability.
    """
    def __init__(self, db_path: str = "chitti_awareness.db"):
        self.db_path = db_path
        self._running = False
        self.context: Optional[KernelContext] = None
        self._task: Optional[asyncio.Task] = None
        self._level2_watchers = {}
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS awareness_events (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    level INTEGER,
                    source TEXT,
                    label TEXT,
                    confidence REAL,
                    correlation_id TEXT,
                    payload TEXT,
                    timestamp REAL,
                    expires_at REAL
                )
            ''')
            # Index for TTL cleanup
            conn.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON awareness_events(expires_at)')

    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        self._init_db()
        return True
        
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._loop())
        
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            
    async def shutdown(self):
        pass

    def _save_event(self, event: AwarenessEvent):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO awareness_events 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id, event.type.value, event.level.value, event.source.value,
                event.label, event.confidence, event.correlation_id,
                json.dumps(event.payload), event.timestamp, event.expires_at
            ))

    def _cleanup_expired(self):
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM awareness_events WHERE expires_at IS NOT NULL AND expires_at <= ?", (now,))

    async def publish_event(self, event: AwarenessEvent):
        """Called by internal pollers or Level 2/3 dynamic watchers."""
        self._save_event(event)
        await self.context.event_bus.publish("AwarenessEventPublished", AwarenessEventPublished(event))

    def request_watcher(self, watcher_id: str, watcher_type: AwarenessType, target: str):
        """Level 2/3 API to spin up dynamic monitoring."""
        self._level2_watchers[watcher_id] = {"type": watcher_type, "target": target, "active": True}
        
    def cancel_watcher(self, watcher_id: str):
        """Destroy ephemeral watcher."""
        if watcher_id in self._level2_watchers:
            del self._level2_watchers[watcher_id]

    async def get_recent_events(self, event_type: AwarenessType, limit: int = 5) -> List[AwarenessEvent]:
        events = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM awareness_events 
                WHERE type = ? 
                ORDER BY timestamp DESC LIMIT ?
            """, (event_type.value, limit))
            
            for row in cursor.fetchall():
                from desktop.models.awareness import AwarenessSource
                evt = AwarenessEvent(
                    id=row[0],
                    type=AwarenessType(row[1]),
                    level=AwarenessLevel(row[2]),
                    source=AwarenessSource(row[3]),
                    label=row[4],
                    confidence=row[5],
                    correlation_id=row[6],
                    payload=json.loads(row[7]),
                    timestamp=row[8],
                    expires_at=row[9]
                )
                events.append(evt)
        return events

    async def _loop(self):
        """Background polling loop for Level 1 awareness and TTL cleanup."""
        last_cleanup = 0
        while self._running:
            now = time.time()
            
            # 1. TTL Cleanup (every 60 seconds)
            if now - last_cleanup > 60:
                self._cleanup_expired()
                last_cleanup = now
                
            # 2. Level 1 Mocks (Window focus)
            # In production, use pywin32 to get GetForegroundWindow()
            # For MVP, we simulate occasional window changes
            
            # Example publishing a Level 1 Window Focus event with 24 hr TTL
            # await self.publish_event(AwarenessEvent(
            #    id=str(uuid.uuid4()),
            #    type=AwarenessType.WINDOW,
            #    level=AwarenessLevel.LEVEL_1_ALWAYS_ON,
            #    label="Notepad focused",
            #    confidence=100.0,
            #    expires_at=now + (24 * 3600)
            # ))
            
            await asyncio.sleep(2.0)
