from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from desktop.models.events import DomainEvent

# --- Enums ---

class AdapterHealth(Enum):
    READY = "READY"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    DEGRADED = "DEGRADED"

class RecoveryPolicy(Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    DISCARD = "DISCARD"
    RESTORE = "RESTORE"

class AdapterLifecycle(Enum):
    DISCOVERED = "DISCOVERED"
    LOADED = "LOADED"
    READY = "READY"
    BUSY = "BUSY"
    UNLOADING = "UNLOADING"
    FAILED = "FAILED"

class ActionType(Enum):
    OPEN_RESOURCE = "OPEN_RESOURCE"
    SELECT = "SELECT"
    INPUT_TEXT = "INPUT_TEXT"
    COPY = "COPY"
    PASTE = "PASTE"
    SAVE = "SAVE"
    EXPORT = "EXPORT"
    NAVIGATE = "NAVIGATE"
    GO_BACK = "GO_BACK"
    GO_FORWARD = "GO_FORWARD"
    REFRESH = "REFRESH"
    STOP_LOADING = "STOP_LOADING"
    SEARCH = "SEARCH"
    DOWNLOAD = "DOWNLOAD"
    UPLOAD = "UPLOAD"
    EXECUTE = "EXECUTE"
    CLOSE = "CLOSE"
    MOVE = "MOVE"
    RESIZE = "RESIZE"
    READ_RESOURCE = "READ_RESOURCE"
    WRITE_RESOURCE = "WRITE_RESOURCE"
    LIST = "LIST"
    WATCH = "WATCH"
    QUERY_METADATA = "QUERY_METADATA"
    STREAM = "STREAM"
    FOCUS = "FOCUS"
    ATTACH = "ATTACH"
    DETACH = "DETACH"
    SEND = "SEND"
    REPLY = "REPLY"
    FORWARD = "FORWARD"
    SUBSCRIBE = "SUBSCRIBE"
    UNSUBSCRIBE = "UNSUBSCRIBE"
    AUTHENTICATE = "AUTHENTICATE"

class ActionStatus(Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    RETRYABLE = "RETRYABLE"

class ArtifactCategory(Enum):
    FILE = "FILE"
    IMAGE = "IMAGE"
    PDF = "PDF"
    TEXT = "TEXT"
    JSON = "JSON"
    HTML = "HTML"
    SCREENSHOT = "SCREENSHOT"
    DOWNLOAD = "DOWNLOAD"
    EXPORT = "EXPORT"
    LOG = "LOG"

# --- Core Models ---

@dataclass(frozen=True)
class EnvironmentTarget:
    adapter_id: str
    resource_id: Optional[str] = None
    window_id: Optional[str] = None
    tab_id: Optional[str] = None
    device_id: Optional[str] = None
    workspace_id: Optional[str] = None

@dataclass(frozen=True)
class EnvironmentAction:
    action_type: ActionType
    target: EnvironmentTarget
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AdapterManifest:
    id: str
    version: str
    capabilities: List[str] # What can you do? (e.g. Navigate, Screenshot)
    permissions: List[str]  # What are you allowed to touch? (e.g. Internet, File Upload)
    platforms: List[str]
    execution_mode: str = "asynchronous"

@dataclass
class EnvironmentResource:
    """Rule 356: Stable logical reference for any environment object."""
    id: str
    uri: str
    type: str
    title: str
    state: str
    owner_adapter: str
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BrowserElementReference(EnvironmentResource):
    """Rule 355: Semantic reference, not a raw locator."""
    selector: str = ""
    role: str = ""
    text: str = ""
    bounding_box: Dict[str, float] = field(default_factory=dict)
    confidence: float = 1.0

@dataclass
class DesktopObjectReference(EnvironmentResource):
    """Rule 355: Semantic reference for desktop automation."""
    window_id: str = ""
    control_id: str = ""
    automation_id: str = ""
    role: str = ""
    bounds: Dict[str, float] = field(default_factory=dict)
    confidence: float = 1.0

@dataclass
class FileReference(EnvironmentResource):
    """File path OS leakage is contained in the engine. This is purely logical."""
    size_bytes: int = 0
    mime_type: str = ""
    last_modified: float = 0.0

@dataclass
class EnvironmentArtifact:
    """Output from an action (screenshots, downloads, exports)."""
    id: str
    category: ArtifactCategory
    uri: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    content: Optional[Any] = None

@dataclass
class IDEResource(EnvironmentResource):
    """Rule 359: Developer Resources are Abstract."""
    pass

@dataclass
class WorkspaceResource(IDEResource): pass
@dataclass
class ProjectResource(IDEResource): pass
@dataclass
class EditorResource(IDEResource): pass
@dataclass
class DocumentResource(IDEResource): pass
@dataclass
class TerminalResource(IDEResource): pass
@dataclass
class SymbolResource(IDEResource): pass
@dataclass
class BreakpointResource(IDEResource): pass
@dataclass
class DiagnosticResource(IDEResource): pass
@dataclass
class ExtensionResource(IDEResource): pass

@dataclass
class WorkspaceState:
    opened_workspaces: List[str] = field(default_factory=list)
    opened_documents: List[str] = field(default_factory=list)
    active_editor: str = ""
    cursor_locations: Dict[str, Any] = field(default_factory=dict)
    terminal_sessions: List[str] = field(default_factory=list)
    git_branch: str = ""
    debug_session: str = ""
    language_services: Dict[str, str] = field(default_factory=dict)

@dataclass
class AuthenticationContext:
    """Prepares for OAuth, API Keys, JWT, Enterprise SSO."""
    auth_type: str
    token: str = ""
    refresh_token: str = ""
    expires_at: float = 0.0
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MailMessageResource(EnvironmentResource): pass
@dataclass
class MailFolderResource(EnvironmentResource): pass
@dataclass
class CalendarResource(EnvironmentResource): pass
@dataclass
class CalendarEventResource(EnvironmentResource): pass
@dataclass
class ContactResource(EnvironmentResource): pass
@dataclass
class APIEndpointResource(EnvironmentResource): pass
@dataclass
class WebhookResource(EnvironmentResource): pass
@dataclass
class APIResponseResource(EnvironmentResource): pass

@dataclass
class EnvironmentActionResult:
    """Normalized response for all environment interactions."""
    status: ActionStatus
    latency: float
    verification_status: str = "NONE"
    evidence: List[str] = field(default_factory=list)
    resource: Optional[EnvironmentResource] = None
    artifacts: List[EnvironmentArtifact] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class BrowserState:
    """Normalized snapshot instead of querying Playwright continuously."""
    current_url: str
    title: str
    loading_state: bool
    active_tab: str
    tab_count: int
    download_state: str
    dialog_state: str

@dataclass
class EnvironmentDialog:
    """Generic representation of prompts, alerts, confirms, file pickers."""
    dialog_id: str
    dialog_type: str # alert, confirm, prompt, file_picker, permission
    message: str
    default_value: str = ""

@dataclass
class EnvironmentSession:
    session_id: str
    recovery_policy: RecoveryPolicy = RecoveryPolicy.AUTO
    context_data: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

@dataclass
class EnvironmentContext:
    reasoning_plan_id: str
    workflow_id: str
    execution_id: str
    session_id: str
    presentation_session_id: Optional[str] = None
    cancellation_token: Any = None
    timeout_ms: int = 30000
    user_profile: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)

@dataclass
class EnvironmentResourceLock:
    lock_id: str
    hierarchy_path: str # e.g. "Browser/Chrome/Tab4"
    owner_workflow_id: str
    is_acquired: bool = False

@dataclass
class EnvironmentFingerprint:
    """
    Phase 3 Contract #5: Captures the physical state of the OS/UI at goal initiation
    to ensure safe deterministic replay conditions.
    """
    fingerprint_id: str
    os_platform: str
    screen_resolution: str
    active_window: str
    timestamp: float
    version: str = "1.0"
    connected_monitors: Optional[List[str]] = None
    running_processes: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fingerprint_id": self.fingerprint_id,
            "os_platform": self.os_platform,
            "screen_resolution": self.screen_resolution,
            "active_window": self.active_window,
            "timestamp": self.timestamp,
            "version": self.version,
            "connected_monitors": self.connected_monitors,
            "running_processes": self.running_processes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentFingerprint':
        if not data:
            return None
        return cls(
            fingerprint_id=data.get("fingerprint_id", ""),
            os_platform=data.get("os_platform", ""),
            screen_resolution=data.get("screen_resolution", ""),
            active_window=data.get("active_window", ""),
            timestamp=data.get("timestamp", 0.0),
            version=data.get("version", "1.0"),
            connected_monitors=data.get("connected_monitors"),
            running_processes=data.get("running_processes"),
        )

# --- Events ---

@dataclass
class EnvironmentEvent(DomainEvent):
    session_id: str
    timestamp: float

@dataclass
class EnvironmentSessionStarted(EnvironmentEvent): pass
@dataclass
class EnvironmentSessionRestored(EnvironmentEvent): pass
@dataclass
class EnvironmentLockAcquired(EnvironmentEvent): lock_id: str
@dataclass
class EnvironmentLockReleased(EnvironmentEvent): lock_id: str
@dataclass
class EnvironmentActionQueued(EnvironmentEvent): action_id: str
@dataclass
class EnvironmentActionStarted(EnvironmentEvent): action_id: str
@dataclass
class EnvironmentActionCompleted(EnvironmentEvent): action_id: str
@dataclass
class EnvironmentActionFailed(EnvironmentEvent): 
    action_id: str
    error: str
@dataclass
class EnvironmentAdapterBusy(EnvironmentEvent): adapter_id: str
