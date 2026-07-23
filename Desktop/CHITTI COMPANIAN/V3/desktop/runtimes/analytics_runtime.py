import os
import json
import time
import sqlite3
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.models.events import ExecutionCompletedEvent
from desktop.models.analytics import (
    AnalyticsRecord, ExecutionMetrics, ActivityTimelineEntry, ProductivitySummary, 
    TimelineEntry, ActivityTimeline, InsightCard, SuggestedNarrationFacts, AnalyticsPresentationBundle
)
from desktop.runtimes.analytics.collector import AnalyticsCollector

logger = logging.getLogger(__name__)

class AnalyticsRuntime(IRuntime):
    """
    S32A: Passive telemetry runtime.
    Sole owner of storage/analytics.db.
    Subscribes to EventBus signals, normalizes via AnalyticsCollector, and exposes public Analytics APIs.
    """
    def __init__(self, db_path: str = "storage/analytics.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._running = False
        self.collector = AnalyticsCollector()
        self._init_db()

    @property
    def dependencies(self):
        return []

    def health(self) -> HealthState:
        return HealthState.HEALTHY if self._running else HealthState.DEGRADED

    def _init_db(self):
        """
        Initializes SQLite storage table for analytics.db.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS analytics_records (
                        record_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        source_subsystem TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        duration_ms REAL NOT NULL,
                        status TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    )
                ''')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_analytics_ts ON analytics_records(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_analytics_session ON analytics_records(session_id)')
        except Exception as e:
            logger.error(f"[AnalyticsRuntime] Error initializing analytics.db: {e}")

    async def initialize(self, context: Any = None) -> bool:
        self._context = context
        if context and hasattr(context, "event_bus"):
            from desktop.models.analytics import UserActivityEvent
            context.event_bus.subscribe(ExecutionCompletedEvent, self.on_event)
            context.event_bus.subscribe(UserActivityEvent, self.on_event)
        return True

    async def start(self) -> bool:
        self._running = True
        logger.info("[AnalyticsRuntime] Started telemetry runtime.")
        return True

    async def stop(self) -> bool:
        self._running = False
        logger.info("[AnalyticsRuntime] Stopped telemetry runtime.")
        return True

    async def shutdown(self) -> bool:
        await self.stop()
        return True

    def on_event(self, event: Any):
        """
        EventBus subscriber handler. Normalizes and persists events asynchronously.
        """
        record = self.collector.normalize_event(event)
        if record:
            self.save_record(record)

    def save_record(self, record: AnalyticsRecord) -> bool:
        """
        Persists a normalized AnalyticsRecord to analytics.db.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO analytics_records 
                    (record_id, event_type, source_subsystem, session_id, timestamp, duration_ms, status, payload_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.record_id, record.event_type, record.source_subsystem,
                    record.session_id, record.timestamp, record.duration_ms,
                    record.status, record.payload_json
                ))
            return True
        except Exception as e:
            logger.error(f"[AnalyticsRuntime] Error saving record {record.record_id}: {e}")
            return False

    def get_records(self, session_id: Optional[str] = None, limit: int = 100) -> List[AnalyticsRecord]:
        """
        Retrieves raw AnalyticsRecords from analytics.db.
        """
        records = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                if session_id:
                    cursor = conn.execute(
                        "SELECT record_id, event_type, source_subsystem, session_id, timestamp, duration_ms, status, payload_json FROM analytics_records WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                        (session_id, limit)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT record_id, event_type, source_subsystem, session_id, timestamp, duration_ms, status, payload_json FROM analytics_records ORDER BY timestamp DESC LIMIT ?",
                        (limit,)
                    )
                for row in cursor.fetchall():
                    records.append(AnalyticsRecord(
                        record_id=row[0], event_type=row[1], source_subsystem=row[2],
                        session_id=row[3], timestamp=row[4], duration_ms=row[5],
                        status=row[6], payload_json=row[7]
                    ))
        except Exception as e:
            logger.error(f"[AnalyticsRuntime] Error reading records: {e}")
        return records

    # Public Analytics API
    def get_execution_metrics(self, session_id: Optional[str] = None) -> ExecutionMetrics:
        records = self.get_records(session_id=session_id, limit=500)
        exec_records = [r for r in records if r.event_type == "EXECUTION_COMPLETED"]
        
        total = len(exec_records)
        if total == 0:
            return ExecutionMetrics()

        successes = sum(1 for r in exec_records if r.status == "SUCCESS")
        failures = total - successes
        rate = round(successes / total, 4) if total > 0 else 0.0
        avg_dur = round(sum(r.duration_ms for r in exec_records) / total, 2) if total > 0 else 0.0

        return ExecutionMetrics(
            total_executions=total,
            success_count=successes,
            failure_count=failures,
            success_rate=rate,
            avg_duration_ms=avg_dur,
            replay_count=0
        )

    def get_activity_timeline(self, session_id: Optional[str] = None, limit: int = 50) -> List[ActivityTimelineEntry]:
        records = self.get_records(session_id=session_id, limit=limit)
        entries = []
        for r in records:
            meta = {}
            try:
                meta = json.loads(r.payload_json)
            except Exception:
                pass
            
            title_str = f"{r.event_type} via {r.source_subsystem}"
            if "capability_name" in meta:
                title_str = f"Executed {meta['capability_name']}"
            elif "app_name" in meta:
                title_str = f"Focus {meta['app_name']}"

            entries.append(ActivityTimelineEntry(
                timestamp=r.timestamp,
                event_type=r.event_type,
                title=title_str,
                duration_ms=r.duration_ms,
                metadata=meta
            ))
        return entries

    def get_productivity_summary(self, session_id: str = "global") -> ProductivitySummary:
        records = self.get_records(session_id=session_id, limit=500)
        total_rec = len(records)
        exec_rec = sum(1 for r in records if r.event_type == "EXECUTION_COMPLETED")
        
        start_t = min((r.timestamp for r in records), default=time.time())
        end_t = max((r.timestamp for r in records), default=time.time())
        total_dur = max(0.0, end_t - start_t)

        top_evs = list(set(r.event_type for r in records))[:5]

        return ProductivitySummary(
            session_id=session_id,
            start_time=start_t,
            end_time=end_t,
            total_records=total_rec,
            total_executions=exec_rec,
            total_duration_sec=round(total_dur, 2),
            top_events=top_evs
        )

    def get_structured_timeline(self, session_id: str = "global", limit: int = 50) -> ActivityTimeline:
        records = self.get_records(session_id=session_id, limit=limit)
        entries = []
        for r in records:
            meta = {}
            try:
                meta = json.loads(r.payload_json)
            except Exception:
                pass
            app_id = meta.get("app_name", r.source_subsystem)
            title = meta.get("window_title", f"{r.event_type} event")
            entries.append(TimelineEntry(
                entry_id=r.record_id,
                timestamp=r.timestamp,
                event_type=r.event_type,
                app_identity=app_id,
                window_title=title,
                duration_ms=r.duration_ms,
                session_id=r.session_id,
                metadata=meta
            ))
        start_t = min((e.timestamp for e in entries), default=time.time())
        end_t = max((e.timestamp for e in entries), default=time.time())
        return ActivityTimeline(
            session_id=session_id,
            entries=entries,
            start_timestamp=start_t,
            end_timestamp=end_t
        )

    def get_insight_cards(self, session_id: str = "global") -> List[InsightCard]:
        metrics = self.get_execution_metrics(session_id)
        cards = [
            InsightCard(
                card_id=f"card_exec_{session_id}",
                metric_key="TOTAL_EXECUTIONS",
                metric_value=metrics.total_executions,
                category="EXECUTION_PERFORMANCE"
            ),
            InsightCard(
                card_id=f"card_rate_{session_id}",
                metric_key="SUCCESS_RATE_PERCENT",
                metric_value=round(metrics.success_rate * 100.0, 2),
                category="EXECUTION_PERFORMANCE"
            )
        ]
        return cards

    def get_suggested_narration_facts(self, session_id: str = "global") -> SuggestedNarrationFacts:
        records = self.get_records(session_id=session_id, limit=500)
        metrics = self.get_execution_metrics(session_id)
        
        apps = []
        ev_types = []
        for r in records:
            ev_types.append(r.event_type)
            try:
                meta = json.loads(r.payload_json)
                if "app_name" in meta:
                    apps.append(meta["app_name"])
            except Exception:
                pass
        
        top_app = max(set(apps), key=apps.count) if apps else "Desktop"
        most_freq_ev = max(set(ev_types), key=ev_types.count) if ev_types else "NONE"

        return SuggestedNarrationFacts(
            session_id=session_id,
            top_application=top_app,
            total_execution_count=metrics.total_executions,
            success_rate_percent=round(metrics.success_rate * 100.0, 2),
            replay_count=metrics.replay_count,
            most_frequent_event=most_freq_ev
        )

    def get_presentation_bundle(self, session_id: str = "global") -> AnalyticsPresentationBundle:
        """
        S32C: Domain presentation bundle projection for Presentation Platform.
        Aggregates ActivityTimeline, ExecutionMetrics, ProductivitySummary, InsightCard list, and SuggestedNarrationFacts.
        """
        metrics = self.get_execution_metrics(session_id)
        summary = self.get_productivity_summary(session_id)
        timeline = self.get_structured_timeline(session_id, limit=20)
        insights = self.get_insight_cards(session_id)
        narration_facts = self.get_suggested_narration_facts(session_id)

        return AnalyticsPresentationBundle(
            bundle_id=f"bundle_analytics_{session_id}_{int(time.time())}",
            session_id=session_id,
            activity_timeline=timeline,
            execution_metrics=metrics,
            productivity_summary=summary,
            insight_cards=insights,
            suggested_narration_facts=narration_facts,
            timestamp=time.time()
        )
