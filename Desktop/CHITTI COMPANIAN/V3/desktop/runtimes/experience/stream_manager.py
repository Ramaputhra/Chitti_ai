class StreamController:
    """
    Central owner of streaming, throttling, cancellation, timeout, batching, and retries.
    Experiences rely on this instead of managing async tasks themselves.
    """
    def start_stream(self, session_id: str, recipe_id: str):
        print(f"[StreamController] Starting stream for {session_id}")

    def pause_stream(self, session_id: str):
        pass

    def cancel_stream(self, session_id: str):
        pass

    def throttle(self, session_id: str, rate_limit: float):
        pass
