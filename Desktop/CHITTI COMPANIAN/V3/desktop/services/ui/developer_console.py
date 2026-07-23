import sys
import threading
import json
import dataclasses
from collections import deque
from typing import Any, Dict, List

from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLineEdit, QSplitter, QLabel, QTreeWidget, QTreeWidgetItem
)

from desktop.platform.shared.interfaces.developer_console import IDeveloperConsole
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.service import ServiceState

class UIBridge(QObject):
    event_signal = Signal(object) # Passes Event object safely to UI thread

class DeveloperConsoleWindow(QMainWindow):
    def __init__(self, event_bus: IEventBus) -> None:
        super().__init__()
        self.event_bus = event_bus
        self.setWindowTitle("CHITTI Runtime Inspector")
        self.resize(1100, 800)

        self.bridge = UIBridge()
        self.bridge.event_signal.connect(self._process_event)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._init_live_status_tab()
        self._init_workflow_inspector_tab()
        self._init_event_explorer_tab()
        self._init_memory_explorer_tab()
        self._init_telemetry_tab()
        self._init_provider_tab()
        self._init_presence_tab()
        self._init_browser_tab()
        self._init_task_orchestrator_tab()
        self._init_template_runtime_tab()
        self._init_dev_tools_tab()
        
        # State trackers
        self.token_count = 0
        self.recent_events = deque(maxlen=1000)

    def _init_live_status_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.live_status_text = QTextEdit()
        self.live_status_text.setReadOnly(True)
        self.live_status_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 14px;")
        layout.addWidget(self.live_status_text)
        self.tabs.addTab(tab, "Live Status")
        
        # Internal state for Live Status
        self.sys_state = {
            "Kernel": "Idle",
            "Planner": "Idle",
            "Memory": "Idle",
            "Inference": "Idle",
            "Expression": "Idle",
            "Presence": "Booting"
        }
        self._update_live_status()

    def _init_workflow_inspector_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # We use a QTreeWidget to show Workflow hierarchical execution
        self.wf_tree = QTreeWidget()
        self.wf_tree.setHeaderLabels(["Workflow ID / Step", "Status", "Duration"])
        self.wf_tree.setStyleSheet("background-color: #1e1e1e; color: #ffcc00; font-family: Consolas;")
        layout.addWidget(self.wf_tree)
        self.tabs.addTab(tab, "Workflow Inspector")
        
        self.workflows: Dict[str, QTreeWidgetItem] = {}

    def _init_event_explorer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.event_search = QLineEdit()
        self.event_search.setPlaceholderText("Search events...")
        search_layout.addWidget(self.event_search)
        layout.addLayout(search_layout)
        
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: Consolas;")
        layout.addWidget(self.event_log)
        self.tabs.addTab(tab, "Event Explorer")

    def _init_memory_explorer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.memory_text = QTextEdit()
        self.memory_text.setReadOnly(True)
        self.memory_text.setStyleSheet("background-color: #1e1e1e; color: #ff55ff; font-family: Consolas;")
        layout.addWidget(self.memory_text)
        self.tabs.addTab(tab, "Memory Explorer")

    def _init_telemetry_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.telemetry_text = QTextEdit()
        self.telemetry_text.setReadOnly(True)
        self.telemetry_text.setStyleSheet("background-color: #1e1e1e; color: #00ccff; font-family: Consolas;")
        layout.addWidget(self.telemetry_text)
        self.tabs.addTab(tab, "Telemetry")

    def _init_provider_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.provider_text = QTextEdit()
        self.provider_text.setReadOnly(True)
        self.provider_text.setStyleSheet("background-color: #1e1e1e; color: #55ff55; font-family: Consolas;")
        layout.addWidget(self.provider_text)
        self.tabs.addTab(tab, "Provider Monitor")

    def _init_presence_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.presence_text = QTextEdit()
        self.presence_text.setReadOnly(True)
        self.presence_text.setStyleSheet("background-color: #1e1e1e; color: #ffaa00; font-family: Consolas;")
        layout.addWidget(self.presence_text)
        self.tabs.addTab(tab, "Presence Monitor")
        
        # Internal presence state
        self.presence_data = {
            "Current State": "BOOTING",
            "Hidden Since": "-",
            "Last Activity": "-",
            "Dock Side": "AUTO",
            "Current Monitor": "-",
            "Wake Reason": "-",
            "Auto Hide Timer": "5 min",
            "Presence Mode": "AUTO_DOCK"
        }
        self._update_presence_display()

    def _init_browser_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.browser_text = QTextEdit()
        self.browser_text.setReadOnly(True)
        self.browser_text.setStyleSheet("background-color: #1e1e1e; color: #ff88ff; font-family: Consolas;")
        layout.addWidget(self.browser_text)
        self.tabs.addTab(tab, "Browser Runtime")
        
        self.browser_data = {
            "State": "UNINITIALIZED",
            "Current URL": "-",
            "Current Title": "-",
            "Current Search": "-",
            "Open Tabs": "0",
            "Extraction Time": "0 ms",
            "DOM Size": "0 bytes",
            "Memory Usage": "0 MB",
            "Last Navigation": "-",
            "Current Capability": "-",
            "Search Engine": "-",
            "Browser Profile": "-",
            "Queue Length": "0"
        }
        self._update_browser_display()

    def _update_browser_display(self):
        lines = ["=== BROWSER RUNTIME INSPECTOR ===", ""]
        for k, v in self.browser_data.items():
            lines.append(f"{k.ljust(20)}: {v}")
        self.browser_text.setPlainText("\n".join(lines))

    def _init_task_orchestrator_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.task_text = QTextEdit()
        self.task_text.setReadOnly(True)
        self.task_text.setStyleSheet("background-color: #1e1e1e; color: #ffaa00; font-family: Consolas;")
        layout.addWidget(self.task_text)
        self.tabs.addTab(tab, "Task Orchestrator")
        
        self.task_data = {
            "Running Tasks": "0",
            "Queued Tasks": "0",
            "Task Progress": "0%",
            "Current Step": "-",
            "Waiting For": "-",
            "Elapsed Time": "0s",
            "Checkpoint Count": "0",
            "Retries": "0",
            "Approvals": "0",
            "Task Priority": "-",
            "Recovery Source": "-",
            "Approval Age": "-"
        }
        self._update_task_orchestrator_display()

    def _update_task_orchestrator_display(self):
        lines = ["=== TASK ORCHESTRATOR ===", ""]
        for k, v in self.task_data.items():
            lines.append(f"{k.ljust(20)}: {v}")
        self.task_text.setPlainText("\n".join(lines))

    def _update_presence_display(self):
        text = "Presence Runtime Inspector\n────────────────────────────────────────────\n\n"
        for k, v in self.presence_data.items():
            text += f"{k:<18} {v}\n"
        self.presence_text.setPlainText(text)

    def _init_template_runtime_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.template_text = QTextEdit()
        self.template_text.setReadOnly(True)
        self.template_text.setStyleSheet("background-color: #1e1e1e; color: #ff00ff; font-family: Consolas;")
        layout.addWidget(self.template_text)
        self.tabs.addTab(tab, "Template Runtime")
        
        self.template_data = {
            "Loaded Templates": "0",
            "Compiled Cache": "0",
            "Last Template Version": "-",
            "Execution Cursor": "-",
            "Validation Status": "-",
            "Cache Hit Rate": "-",
            "Last Compile Time": "-"
        }
        self._update_template_display()

    def _update_template_display(self):
        lines = ["=== TEMPLATE RUNTIME ===", ""]
        for k, v in self.template_data.items():
            lines.append(f"{k.ljust(25)}: {v}")
        self.template_text.setPlainText("\n".join(lines))

    def _init_dev_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        warning = QLabel("Rule 47: Developer Tooling Is Observational.\nOnly use these explicit actions if you intend to alter runtime behavior.")
        warning.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning)
        
        btn_layout = QHBoxLayout()
        
        btn_replay = QPushButton("Replay Last Workflow (Rule 49)")
        btn_layout.addWidget(btn_replay)
        
        btn_pause = QPushButton("Pause Kernel Scheduler")
        btn_layout.addWidget(btn_pause)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.tabs.addTab(tab, "Developer Tools")

    def _update_live_status(self):
        text = "CHITTI Runtime Inspector\n────────────────────────────────────────────\n\nLIVE STATUS\n\n"
        for k, v in self.sys_state.items():
            text += f"{k:<15} {v}\n"
        text += "────────────────────────────────────────────"
        self.live_status_text.setPlainText(text)

    def _process_event(self, event: Event) -> None:
        """
        Master event router. Routes EventBus traffic to respective tabs.
        """
        # 1. Update Event Explorer (with filtering)
        self._append_event_log(event)
        
        # 2. Update Live Status & Workflow Tree based on event type
        if event.id.startswith("Workflow."):
            self._handle_workflow_event(event)
        elif event.id.startswith("Inference."):
            self._handle_inference_event(event)
        elif event.id.startswith("Expression."):
            self._handle_expression_event(event)
        elif event.id.startswith("Memory."):
            self._handle_memory_event(event)
        elif event.id.startswith("Presence."):
            self._handle_presence_event(event)
        elif event.id.startswith("Task."):
            self._handle_task_event(event)
            
        self._update_live_status()

    def _append_event_log(self, event: Event):
        # Filtering high-frequency tokens
        if event.id == "Inference.TokenGenerated":
            self.token_count += 1
            # Don't render every token in the stream, just aggregate
            return

        payload_str = str(event.payload)
        if len(payload_str) > 150:
            payload_str = payload_str[:150] + "..."
            
        color = "#ffffff"
        if "Started" in event.id or "Created" in event.id: color = "#00ccff" # INFO
        elif "Completed" in event.id or "Finished" in event.id: color = "#00ff00" # SUCCESS
        elif "Error" in event.id or "Failed" in event.id: color = "#ff0000" # ERROR
        elif "Warning" in event.id or "Retry" in event.id: color = "#ffaa00" # WARNING
        
        # Insert aggregated tokens before the next real event if any existed
        if self.token_count > 0 and event.id != "Inference.TokenGenerated":
            self.event_log.append(f'<span style="color: #555555;">[Inference.TokenGenerated] &times; {self.token_count} events collapsed</span>')
            self.token_count = 0
            
        log_msg = f'<span style="color: {color};">[{event.id}]</span> {payload_str}'
        self.event_log.append(log_msg)
        
        sb = self.event_log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _handle_workflow_event(self, event: Event):
        wf_id = event.payload.get("workflow_id", "unknown")
        
        if event.id == "Workflow.Created":
            self.sys_state["Kernel"] = f"Queued {wf_id}"
            item = QTreeWidgetItem(self.wf_tree, [f"Workflow {wf_id}", "Queued", "-"])
            self.workflows[wf_id] = item
            
        elif event.id == "Workflow.Started":
            self.sys_state["Kernel"] = f"Running {wf_id}"
            if wf_id in self.workflows:
                self.workflows[wf_id].setText(1, "Running")
                
        elif event.id == "Workflow.Completed":
            self.sys_state["Kernel"] = "Idle"
            if wf_id in self.workflows:
                self.workflows[wf_id].setText(1, "Completed")
                self.workflows[wf_id].setForeground(1, Qt.green)

    def _handle_inference_event(self, event: Event):
        if event.id == "Inference.Started":
            self.sys_state["Inference"] = "Streaming"
        elif event.id == "Inference.Completed":
            self.sys_state["Inference"] = "Idle"
            
            # Update telemetry tab
            tel = event.payload.get("telemetry", {})
            text = f"--- Inference Telemetry ---\nLatency: {tel.get('latency_ms', 0)}ms\nTokens: {tel.get('total_tokens', 0)}\n"
            self.telemetry_text.setPlainText(text)

    def _handle_expression_event(self, event: Event):
        if event.id == "Expression.StateChanged":
            act = event.payload.get("activity", "idle")
            self.sys_state["Expression"] = f"{act.capitalize()}"

    def _handle_memory_event(self, event: Event):
        self.sys_state["Memory"] = "Retrieved"
        self.memory_text.append(f"[{event.id}] {str(event.payload)}")

    def _handle_presence_event(self, event: Event):
        if event.id == "Presence.StateChanged":
            new_state = event.payload.get("new_state", "UNKNOWN")
            self.sys_state["Presence"] = new_state
            self.presence_data["Current State"] = new_state
            if new_state in ["SLIDING_IN", "VISIBLE"]:
                self.presence_data["Hidden Since"] = "-"
        elif event.id == "Presence.WakeRequested":
            self.presence_data["Wake Reason"] = event.payload.get("reason", "Unknown")
        elif event.id == "Presence.Docked":
            import time
            self.presence_data["Hidden Since"] = time.strftime("%H:%M:%S")
            
        self._update_presence_display()

    def _handle_task_event(self, event: Event):
        if event.id == "Task.Created":
            # For now, just increment queued tasks visually
            queued = int(self.task_data.get("Queued Tasks", "0"))
            self.task_data["Queued Tasks"] = str(queued + 1)
        elif event.id == "Task.Started":
            queued = max(0, int(self.task_data.get("Queued Tasks", "0")) - 1)
            running = int(self.task_data.get("Running Tasks", "0")) + 1
            self.task_data["Queued Tasks"] = str(queued)
            self.task_data["Running Tasks"] = str(running)
            context = event.payload.get("task_context")
            if context:
                self.task_data["Current Step"] = context.current_state_summary
                self.task_data["Checkpoint Count"] = str(len(context.checkpoints))
        # Additional task updates would map here
        self._update_task_orchestrator_display()

class DeveloperConsoleService(IDeveloperConsole):
    def __init__(self, event_bus: IEventBus, logger: ILoggingService) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self._state = ServiceState.STOPPED
        self._thread = None
        self._app = None
        self._window = None

    @property
    def name(self) -> str: return "RuntimeInspector"

    @property
    def state(self) -> ServiceState: return self._state

    def initialize(self) -> None:
        self.event_bus.subscribe_all(self._on_event)
        self._state = ServiceState.RUNNING
        self._thread = threading.Thread(target=self._run_ui, daemon=True)
        self._thread.start()

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        if self._app: self._app.quit()

    def health_check(self) -> Dict[str, Any]: return {}

    def _run_ui(self) -> None:
        self._app = QApplication.instance()
        if not self._app:
            self._app = QApplication(sys.argv)
        self._window = DeveloperConsoleWindow(self.event_bus)
        self._window.show()
        self._app.exec()

    def _on_event(self, event: Event) -> None:
        # Pass to GUI thread
        if self._window and self._window.bridge:
            self._window.bridge.event_signal.emit(event)
