import threading

class CancellationToken:
    """
    Thread-safe cooperative cancellation token.
    (Rule 41: Cooperative Cancellation)
    Passed to Capabilities to allow them to gracefully terminate execution.
    """
    def __init__(self):
        self._is_cancelled = False
        self._lock = threading.Lock()
        
    def cancel(self):
        """Signals to the running capability that it should terminate."""
        with self._lock:
            self._is_cancelled = True
            
    @property
    def is_cancelled(self) -> bool:
        """Capabilities should frequently check this property during long operations."""
        with self._lock:
            return self._is_cancelled
