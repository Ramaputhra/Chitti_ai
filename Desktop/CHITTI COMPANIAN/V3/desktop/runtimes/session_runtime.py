import uuid
import time
from typing import Optional, Dict, Any

from desktop.models.lifecycle import IRuntime
from desktop.app.context import KernelContext
from desktop.models.session import WorkSession, SessionState
from desktop.models.intent import IntentRegistry
from desktop.productivity.workspace_extractor import WorkspaceResolver
from desktop.productivity.project_classifier import ProjectClassifier
from desktop.productivity.activity_classifier import ActivityClassifier
from desktop.productivity.intent_classifier import IntentClassifier

class SessionBuilder:
    def __init__(self):
        self.active_session: Optional[WorkSession] = None
        
    def start_new_session(self) -> WorkSession:
        self.active_session = WorkSession(
            id=str(uuid.uuid4()),
            start_time=time.time(),
            state=SessionState.ACTIVE
        )
        return self.active_session
        
    def process_window(self, app: str, title: str) -> bool:
        """Returns True if the session was modified"""
        if not self.active_session:
            self.start_new_session()
            
        modified = False
        if app not in self.active_session.applications:
            self.active_session.applications.add(app)
            modified = True
            
        doc = WorkspaceResolver.extract_document(app, title)
        if doc and doc not in self.active_session.documents:
            self.active_session.documents.add(doc)
            modified = True
            
        # Store raw active window for BrowserManager correlation later
        self.active_session.active_windows.append((time.time(), app, title))
            
        tab = WorkspaceResolver.extract_browser_tab(app, title)
        if tab and tab not in self.active_session.browser_title_hints:
            self.active_session.browser_title_hints.add(tab)
            modified = True
            
        dir_path = WorkspaceResolver.extract_directory(app, title)
        if dir_path and dir_path not in self.active_session.directories:
            self.active_session.directories.add(dir_path)
            modified = True
            
        # Update Activities (Layer 1)
        new_activities = ActivityClassifier.extract_activities(self.active_session, app, title)
        if new_activities and not new_activities.issubset(self.active_session.activities):
            self.active_session.activities.update(new_activities)
            modified = True
            
        return modified

    def process_clipboard(self, content: str, app: str) -> bool:
        """Processes a clipboard text change, minifying and classifying it (Rule 45)"""
        if not self.active_session or not content.strip():
            return False
            
        import hashlib
        import re
        from desktop.models.session import ClipboardEvent
        
        # 1. Deterministic Hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # 2. Changed?
        if self.active_session.clipboard_events:
            last_event = self.active_session.clipboard_events[-1]
            if last_event.content_hash == content_hash:
                return False # Ignore unchanged clipboard
                
        # 3. Deterministic Classification
        content_type = "TEXT"
        if re.match(r'^https?://', content):
            content_type = "URL"
        elif re.match(r'^[a-zA-Z]:\\[^/:*?"<>|]*', content) or content.startswith('/'):
            content_type = "PATH"
        elif re.search(r'\bSELECT\b.*\bFROM\b', content, re.IGNORECASE):
            content_type = "SQL"
        elif re.search(r'\bdef\b\s+\w+\s*\(', content) or re.search(r'\bclass\b\s+\w+:', content):
            content_type = "PYTHON"
        elif content.strip().startswith('{') and content.strip().endswith('}'):
            content_type = "JSON"
        elif re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            content_type = "EMAIL"
            
        # 4. Deterministic Redaction
        is_secret = False
        secret_patterns = [
            r'password\s*=?\s*["\'][^"\']+["\']',
            r'api_key\s*=?\s*["\'][^"\']+["\']',
            r'token\s*=?\s*["\'][^"\']+["\']',
            r'authorization:\s*bearer\s+\S+',
            r'BEGIN PRIVATE KEY',
            r'ssh-rsa\s+'
        ]
        for pat in secret_patterns:
            if re.search(pat, content, re.IGNORECASE):
                is_secret = True
                content_type = "SECRET"
                break
                
        char_count = len(content)
        preview = "<REDACTED>" if is_secret else content[:256]
        
        event = ClipboardEvent(
            timestamp=time.time(),
            application=app,
            content_preview=preview,
            content_hash=content_hash,
            content_type=content_type,
            character_count=char_count
        )
        
        
        self.active_session.clipboard_events.append(event)
        return True

    def process_terminal(self, shell: str, cwd: str, raw_command: str, duration_sec: float, exit_code: int) -> bool:
        """Processes terminal execution events (Rule 47: Normalization)"""
        if not self.active_session:
            self.start_new_session()
            
        from desktop.models.session import TerminalEvent
        from desktop.productivity.command_resolver import CommandResolver
        
        redacted_cmd = CommandResolver.redact_command(raw_command)
        
        event = TerminalEvent(
            timestamp=time.time(),
            shell=shell,
            cwd=cwd,
            command=redacted_cmd,
            duration_sec=duration_sec,
            exit_code=exit_code
        )
        self.active_session.terminal_events.append(event)
        return True

class SessionRepository:
    def __init__(self, context: KernelContext):
        self.context = context
        
    async def commit(self, session: WorkSession, reason: str):
        # Finalize timeline
        session.timeline.finalize()
        from desktop.productivity.episode_builder import EpisodeBuilder
        from desktop.productivity.workflow_reconstructor import WorkflowReconstructor
        from desktop.productivity.outcome_extractor import OutcomeExtractor
        from desktop.productivity.intent_extractor import IntentExtractor
        from desktop.models.cognition import ReasoningContext
        from desktop.cognition.planner.goal_planner import GoalPlanner
        from desktop.cognition.memory.repository import JsonGoalRepository
        
        builder = EpisodeBuilder()
        episode_data = builder.build_episode(session)
        
        # Phase F: Workflow Reconstruction (Rule 52)
        project_workflows, general_workflows = WorkflowReconstructor.reconstruct(episode_data)
        
        # Phase F: Outcome Assessment (Rule 53)
        project_assessments = [OutcomeExtractor.assess(pw) for pw in project_workflows]
        
        # Phase G: Intent Modeling (Rule 54)
        all_project_intents = [IntentExtractor.extract(pa) for pa in project_assessments]
        
        # Phase G: Goal Selection & Continuity (Rules 55, 56)
        goal_planner = GoalPlanner()
        goal_repository = JsonGoalRepository()
        active_goals = []
        
        for pa, intents in zip(project_assessments, all_project_intents):
            # 1. Fetch recent goals
            recent_goals = goal_repository.get_recent_goals(pa.workflow.project_identity)
            
            # 2. Build ReasoningContext
            ctx = ReasoningContext(
                active_project=pa.workflow.project_identity,
                workflow=pa.workflow,
                assessment=pa,
                intent_candidates=intents,
                recent_goals=recent_goals,
                session_metadata={
                    "duration_sec": session.statistics.duration_sec,
                    "reason": reason
                }
            )
            
            # 3. Semantic Decision & Continuity (Goal Planner)
            active_goal = goal_planner.select_goal(ctx)
            active_goals.append(active_goal)
            
            # 4. Save goal
            goal_repository.save_project_goal(pa.workflow.project_identity, active_goal)
        
        # Serialize workflows, outcomes, intents, and active goal for the event bus
        episode_data["project_workflows"] = []
        for pa, intents, active_goal in zip(project_assessments, all_project_intents, active_goals):
            current_state = active_goal.current_state
            episode_data["project_workflows"].append({
                "project_identity": pa.workflow.project_identity.display_name,
                "status": pa.workflow.status,
                "statistics": {
                    "research_time_sec": pa.workflow.statistics.research_time_sec,
                    "coding_time_sec": pa.workflow.statistics.coding_time_sec,
                    "testing_time_sec": pa.workflow.statistics.testing_time_sec,
                    "debug_time_sec": pa.workflow.statistics.debug_time_sec,
                    "build_attempts": pa.workflow.statistics.build_attempts,
                    "failures": pa.workflow.statistics.failures
                },
                "events": [
                    {
                        "action": ev.action.value,
                        "stage": ev.stage.value,
                        "domain": ev.domain.value,
                        "start_time": ev.start_time,
                        "end_time": ev.end_time,
                        "metadata": ev.metadata
                    } for ev in pa.workflow.events
                ],
                "outcomes": [
                    {
                        "type": out.type.value,
                        "description": out.description,
                        "strength": out.strength.value
                    } for out in pa.outcomes
                ],
                "intent_candidates": [
                    {
                        "intent_type": ic.intent_type.value,
                        "category": ic.category.value,
                        "strength": ic.strength.value,
                        "trigger_rules": ic.evidence.trigger_rules
                    } for ic in intents
                ],
                "active_goal": {
                    "goal_id": active_goal.goal_id,
                    "intent_type": active_goal.intent_type.value,
                    "status": current_state.status if current_state else "UNKNOWN",
                    "decision_basis": current_state.decision_basis if current_state else []
                }
            })
        
        # Add summary and reason to the payload
        episode_data["summary"] = f"Work session on {session.primary_project or 'Unknown'} ({reason})"
        episode_data["reason"] = reason
        episode_data["activities"] = list(session.activities)
        episode_data["timeline"] = [
            {
                "intent": entry.intent,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "duration_sec": entry.duration_sec
            }
            for entry in session.timeline.entries
        ]
        episode_data["applications"] = list(session.applications)
        episode_data["documents"] = list(session.documents)
        episode_data["directories"] = list(session.directories)
        episode_data["aliases"] = list(session.aliases)
        
        if self.context and self.context.event_bus:
            await self.context.event_bus.publish("SessionFinalized", {"episode_data": episode_data})

class SessionFinalizer:
    def __init__(self, repository: SessionRepository):
        self.repository = repository
        self.idle_start_time: float = 0.0
        self.IDLE_TIMEOUT_SEC = 30 * 60 # 30 mins
        
    async def check_idle_timeout(self, session: WorkSession) -> bool:
        idle_duration = time.time() - self.idle_start_time
        if idle_duration > self.IDLE_TIMEOUT_SEC:
            await self.finalize(session, "idle_timeout")
            return True
        return False
        
    async def finalize(self, session: WorkSession, reason: str):
        session.state = SessionState.COMMITTED
        session.end_time = time.time()
        session.statistics.duration_sec = session.end_time - session.start_time
        await self.repository.commit(session, reason)

class SessionRuntime(IRuntime):
    """
    Interprets Awareness events into structured WorkSessions.
    Publishes SessionConfidenceChanged and WorkIntentChanged.
    """
    def __init__(self):
        self._running = False
        self.context: Optional[KernelContext] = None
        self.builder = SessionBuilder()
        self.finalizer: Optional[SessionFinalizer] = None
        self.repository: Optional[SessionRepository] = None
        self.intent_classifier: Optional[IntentClassifier] = None
        
    async def initialize(self, context: KernelContext) -> bool:
        self.context = context
        self.repository = SessionRepository(context)
        self.finalizer = SessionFinalizer(self.repository)
        self.intent_classifier = IntentClassifier(IntentRegistry())
        return True
        
    async def start(self):
        self._running = True
        if self.context and self.context.event_bus:
            await self.context.event_bus.subscribe("AwarenessEventPublished", self._on_awareness_event)
            await self.context.event_bus.subscribe("SystemSleepEvent", self._on_system_sleep)
            await self.context.event_bus.subscribe("SystemShutdownEvent", self._on_system_shutdown)
            
    async def stop(self):
        self._running = False
        if self.builder.active_session:
            await self.finalizer.finalize(self.builder.active_session, "shutdown")
            self.builder.active_session = None
            
    async def shutdown(self):
        pass

    async def _on_awareness_event(self, event):
        if not self._running:
            return
            
        evt_type = event.data.get("type")
        
        if evt_type == "IdleStarted":
            self.finalizer.idle_start_time = time.time()
                
        elif evt_type == "IdleEnded":
            if self.builder.active_session:
                finalized = await self.finalizer.check_idle_timeout(self.builder.active_session)
                if finalized:
                    self.builder.active_session = None
                
        elif evt_type in ["WindowActivated", "WindowOpened"]:
            app = event.data.get("app", "")
            title = event.data.get("title", "")
            
            modified = self.builder.process_window(app, title)
            if modified or not self.builder.active_session.primary_project:
                await self._update_classification(title)
                
        elif evt_type == "ClipboardChanged":
            app = event.data.get("app", "Unknown")
            content = event.data.get("content", "")
            self.builder.process_clipboard(content, app)
            
        elif evt_type == "TerminalCommandExecuted":
            shell = event.data.get("shell", "Unknown")
            cwd = event.data.get("cwd", "")
            cmd = event.data.get("command", "")
            duration = event.data.get("duration_sec", 0.0)
            exit_code = event.data.get("exit_code", 0)
            self.builder.process_terminal(shell, cwd, cmd, duration, exit_code)
                
    async def _update_classification(self, latest_title: str):
        session = self.builder.active_session
        titles = set([latest_title])
        proj_name, confidence = ProjectClassifier.classify(
            session.directories, session.documents, session.browser_title_hints, titles
        )
        
        old_confidence = session.confidence
        old_project = session.primary_project
        
        if old_project and old_project != proj_name and confidence > 0.8:
            # Major Context Switch!
            await self.finalizer.finalize(session, "context_switch")
            self.builder.start_new_session()
            session = self.builder.active_session
            session.primary_project = proj_name
            session.confidence = confidence
            await self._publish_confidence(session)
            
        elif proj_name != "Unknown" and (old_project != proj_name or confidence != old_confidence):
            session.primary_project = proj_name
            session.confidence = confidence
            await self._publish_confidence(session)
            
        # Layer 2: Intent Classification
        intent_name, intent_conf, evidence_set = self.intent_classifier.classify(session)
        if intent_name != session.intent:
            old_intent = session.intent
            session.intent = intent_name
            session.intent_confidence = intent_conf
            
            # Record timeline transition
            session.timeline.transition(
                new_intent=intent_name,
                activities=set(session.activities),
                confidence=intent_conf,
                evidence=evidence_set
            )
            
            # Publish Intent Change
            if self.context and self.context.event_bus:
                await self.context.event_bus.publish("WorkIntentChanged", {
                    "session_id": session.id,
                    "previous_intent": old_intent,
                    "new_intent": intent_name,
                    "confidence": intent_conf,
                    "evidence": list(evidence_set)
                })

    async def _publish_confidence(self, session: WorkSession):
        if self.context and self.context.event_bus:
            await self.context.event_bus.publish("SessionConfidenceChanged", {
                "session_id": session.id,
                "project": session.primary_project,
                "confidence": session.confidence,
                "applications": len(session.applications)
            })

    async def _on_system_sleep(self, event):
        if self.builder.active_session:
            await self.finalizer.finalize(self.builder.active_session, "sleep")
            self.builder.active_session = None
        
    async def _on_system_shutdown(self, event):
        if self.builder.active_session:
            await self.finalizer.finalize(self.builder.active_session, "shutdown")
            self.builder.active_session = None
