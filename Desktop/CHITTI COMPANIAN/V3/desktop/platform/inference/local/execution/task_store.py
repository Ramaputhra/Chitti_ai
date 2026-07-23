import sqlite3
import json
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import uuid
import time

from desktop.platform.shared.models.task import (
    TaskContext, TaskState, ExecutionState, TaskPriority,
    TaskObservation, TaskStepData, TaskCheckpoint, TaskMetrics
)

class TaskStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def transaction(self):
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
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    source_intent TEXT,
                    correlation_id TEXT,
                    priority TEXT,
                    state TEXT,
                    execution_state TEXT,
                    current_state_summary TEXT,
                    current_workflow TEXT,
                    current_step TEXT,
                    waiting_on TEXT,
                    estimated_remaining_steps INTEGER,
                    progress_percentage REAL,
                    template_context TEXT,
                    completed_steps TEXT,
                    observations TEXT,
                    failures TEXT,
                    retry_count INTEGER,
                    max_retries INTEGER,
                    execution_history TEXT,
                    start_time REAL,
                    end_time REAL,
                    active_workflow_id TEXT,
                    metrics TEXT,
                    schema_version TEXT,
                    archived INTEGER DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    timestamp REAL,
                    workflow_id TEXT,
                    completed_step_ids TEXT,
                    observations_hash TEXT,
                    planner_version TEXT,
                    kernel_version TEXT,
                    retry_count INTEGER,
                    completed_steps TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state, archived)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_task ON checkpoints(task_id, timestamp)")

    # --- Serialization Helpers ---

    def _serialize_step(self, step: TaskStepData) -> dict:
        return {
            "action_type": step.action_type,
            "parameters": step.parameters,
            "reasoning": step.reasoning
        }

    def _deserialize_step(self, data: dict) -> TaskStepData:
        return TaskStepData(**data)

    def _serialize_observation(self, obs: TaskObservation) -> dict:
        return {
            "step_id": obs.step_id,
            "result": obs.result,
            "success": obs.success,
            "timestamp": obs.timestamp
        }

    def _deserialize_observation(self, data: dict) -> TaskObservation:
        return TaskObservation(**data)
        
    def _serialize_metrics(self, metrics: TaskMetrics) -> dict:
        return metrics.__dict__
        
    def _deserialize_metrics(self, data: dict) -> TaskMetrics:
        return TaskMetrics(**data)

    def _task_to_row(self, task: TaskContext) -> tuple:
        return (
            task.task_id,
            task.goal,
            task.source_intent,
            task.correlation_id,
            task.priority.value,
            task.state.value,
            task.execution_state.value,
            task.current_state_summary,
            task.current_workflow,
            task.current_step,
            task.waiting_on,
            task.estimated_remaining_steps,
            task.progress_percentage,
            json.dumps(task.template_context),
            json.dumps([self._serialize_step(s) for s in task.completed_steps]),
            json.dumps([self._serialize_observation(o) for o in task.observations]),
            json.dumps(task.failures),
            task.retry_count,
            task.max_retries,
            json.dumps(task.execution_history),
            task.start_time,
            task.end_time,
            task.active_workflow_id,
            json.dumps(self._serialize_metrics(task.metrics)),
            task.schema_version,
            0 # archived
        )

    def _row_to_task(self, row) -> TaskContext:
        metrics_dict = json.loads(row[23]) if row[23] else {}
        metrics = self._deserialize_metrics(metrics_dict)
        return TaskContext(
            task_id=row[0],
            goal=row[1],
            source_intent=row[2],
            correlation_id=row[3],
            priority=TaskPriority(row[4]),
            state=TaskState(row[5]),
            execution_state=ExecutionState(row[6]),
            current_state_summary=row[7],
            current_workflow=row[8],
            current_step=row[9],
            waiting_on=row[10],
            estimated_remaining_steps=row[11],
            progress_percentage=row[12],
            template_context=json.loads(row[13]) if row[13] else None,
            completed_steps=[self._deserialize_step(s) for s in json.loads(row[14])] if row[14] else [],
            observations=[self._deserialize_observation(o) for o in json.loads(row[15])] if row[15] else [],
            failures=json.loads(row[16]) if row[16] else [],
            retry_count=row[17],
            max_retries=row[18],
            execution_history=json.loads(row[19]) if row[19] else [],
            start_time=row[20],
            end_time=row[21],
            active_workflow_id=row[22],
            metrics=metrics,
            schema_version=row[24]
        )

    # --- APIs ---

    def save_task(self, task: TaskContext) -> None:
        with self.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    goal=excluded.goal,
                    source_intent=excluded.source_intent,
                    correlation_id=excluded.correlation_id,
                    priority=excluded.priority,
                    state=excluded.state,
                    execution_state=excluded.execution_state,
                    current_state_summary=excluded.current_state_summary,
                    current_workflow=excluded.current_workflow,
                    current_step=excluded.current_step,
                    waiting_on=excluded.waiting_on,
                    estimated_remaining_steps=excluded.estimated_remaining_steps,
                    progress_percentage=excluded.progress_percentage,
                    template_context=excluded.template_context,
                    completed_steps=excluded.completed_steps,
                    observations=excluded.observations,
                    failures=excluded.failures,
                    retry_count=excluded.retry_count,
                    max_retries=excluded.max_retries,
                    execution_history=excluded.execution_history,
                    start_time=excluded.start_time,
                    end_time=excluded.end_time,
                    active_workflow_id=excluded.active_workflow_id,
                    metrics=excluded.metrics,
                    schema_version=excluded.schema_version,
                    archived=excluded.archived
                """,
                self._task_to_row(task)
            )

    def load_task(self, task_id: str) -> Optional[TaskContext]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_task(row)
        return None

    def load_active_tasks(self) -> List[TaskContext]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE archived = 0 AND state NOT IN ('Completed', 'Failed', 'Cancelled')")
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

    def archive_task(self, task_id: str) -> None:
        with self.transaction() as cursor:
            cursor.execute("UPDATE tasks SET archived = 1 WHERE task_id = ?", (task_id,))

    def delete_completed(self) -> None:
        with self.transaction() as cursor:
            cursor.execute("DELETE FROM tasks WHERE state IN ('Completed', 'Failed', 'Cancelled') AND archived = 1")

    # --- Checkpoints ---

    def save_checkpoint(self, task_id: str, checkpoint: TaskCheckpoint) -> None:
        # Rule 68: Checkpoints are append only.
        with self.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO checkpoints (checkpoint_id, task_id, timestamp, workflow_id, completed_step_ids, observations_hash, planner_version, kernel_version, retry_count, completed_steps)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checkpoint.checkpoint_id,
                    task_id,
                    checkpoint.timestamp,
                    checkpoint.workflow_id,
                    json.dumps(checkpoint.completed_step_ids),
                    checkpoint.observations_hash,
                    checkpoint.planner_version,
                    checkpoint.kernel_version,
                    checkpoint.retry_count,
                    json.dumps([self._serialize_step(s) for s in checkpoint.completed_steps])
                )
            )

    def load_latest_checkpoint(self, task_id: str) -> Optional[TaskCheckpoint]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM checkpoints WHERE task_id = ? ORDER BY timestamp DESC LIMIT 1", (task_id,))
            row = cursor.fetchone()
            if row:
                return TaskCheckpoint(
                    checkpoint_id=row[0],
                    timestamp=row[2],
                    workflow_id=row[3],
                    completed_step_ids=json.loads(row[4]) if row[4] else [],
                    observations_hash=row[5],
                    planner_version=row[6],
                    kernel_version=row[7],
                    retry_count=row[8],
                    completed_steps=[self._deserialize_step(s) for s in json.loads(row[9])] if row[9] else []
                )
        return None
