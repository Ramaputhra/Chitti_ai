import logging
import time
from typing import Dict, Any, Optional
import urllib.request
import urllib.error
import json
from desktop.models.remote_provider import ProviderState

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Prevents the system from repeatedly attempting to contact a failing provider.
    """
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        
        self.failure_count = 0
        self.last_failure_time = 0.0
        self._is_open = False

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self._is_open = True
            logger.warning("Circuit breaker OPENED due to repeated failures.")

    def record_success(self):
        self.failure_count = 0
        self._is_open = False
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        if not self._is_open:
            return True
        # If open, check cooldown
        if time.time() - self.last_failure_time > self.cooldown_seconds:
            # Half-open state
            logger.info("Circuit breaker HALF-OPEN, testing provider again.")
            return True
        return False

class RemoteSession:
    """
    Manages HTTP connections, headers, and authentication for remote providers.
    Designed to support pooling and streaming.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.circuit_breaker = CircuitBreaker()
        # In a fully fleshed out Python 3 app, this would wrap requests.Session or aiohttp.ClientSession
        # Here we abstract it so the adapter just uses the session to post/get.

    def post(self, url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Dict[str, Any]:
        """Synchronous post for demonstration; would be async in production."""
        if not self.circuit_breaker.can_execute():
            raise ConnectionError("Circuit breaker is OPEN. Provider is on cooldown.")

        _headers = {"Content-Type": "application/json"}
        if self.api_key:
            _headers["Authorization"] = f"Bearer {self.api_key}"
        if headers:
            _headers.update(headers)

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=_headers, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                self.circuit_breaker.record_success()
                return result
        except urllib.error.URLError as e:
            self.circuit_breaker.record_failure()
            logger.error(f"RemoteSession post failed: {e}")
            raise ConnectionError(f"Failed to connect: {e}")
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"RemoteSession unexpected error: {e}")
            raise

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Dict[str, Any]:
        """Synchronous get for health checks/capabilities."""
        if not self.circuit_breaker.can_execute():
            raise ConnectionError("Circuit breaker is OPEN.")

        _headers = {}
        if self.api_key:
            _headers["Authorization"] = f"Bearer {self.api_key}"
        if headers:
            _headers.update(headers)

        req = urllib.request.Request(url, headers=_headers, method='GET')
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                self.circuit_breaker.record_success()
                return result
        except urllib.error.URLError as e:
            self.circuit_breaker.record_failure()
            raise ConnectionError(f"Failed to connect: {e}")
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
