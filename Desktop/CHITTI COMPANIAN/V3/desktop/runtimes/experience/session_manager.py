class SessionManager:
    """
    Manages PresentationSession creation, updates, and disposal.
    Only ExperienceRuntime should call these methods.
    """
    def create_session(self, intent_id: str):
        pass

    def update_session(self, session_id: str, updates: dict):
        pass

    def dispose_session(self, session_id: str):
        pass
