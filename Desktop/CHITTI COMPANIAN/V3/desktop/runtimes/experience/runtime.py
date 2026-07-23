from desktop.runtimes.experience.session_manager import SessionManager
from desktop.runtimes.experience.interaction_router import InteractionRouter

class ExperienceRuntime:
    """
    Rule 346: Runtime Owns Concurrency.
    The single owner of session lifecycle, streaming orchestration, interaction routing,
    and replay coordination. Experiences must never launch async tasks themselves.
    """
    def __init__(self):
        self.session_manager = SessionManager()
        self.interaction_router = InteractionRouter()
        
    def execute_intent(self, intent: str, recipe_id: str, data: dict):
        print(f"[ExperienceRuntime] Executing intent {intent} via {recipe_id}")
        session = self.session_manager.create_session(intent)
        # Invoke recipe -> Update session -> Dispose (if transient)
        
    def handle_interaction(self, event):
        self.interaction_router.route(event)
        
    def restore_session(self, session_id: str):
        """
        Restores a current active session (e.g. after frontend crash or browser refresh)
        without replaying historical snapshots or re-executing workflows.
        """
        print(f"[ExperienceRuntime] Restoring active session {session_id}")

