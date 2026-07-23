import threading
import time
from collections import deque
from typing import Optional, Dict, Any, Callable, Awaitable
from desktop.runtimes.expression.events import ExpressionStarted, ExpressionFinished, ExpressionInterrupted
import logging

logger = logging.getLogger(__name__)

class ExpressionScheduler:
    """
    Decides *when* and *if* an expression should play.
    Enforces interruptibility and minimum durations based on the expression manifest.
    (Rule 37: Expression Runtime Coordination)
    """
    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self._queue = deque()
        self._current_expr: Optional[Dict[str, Any]] = None
        self._expr_start_time: float = 0.0
        self._thread: Optional[threading.Thread] = None
        self._running = False
        
    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def schedule(self, expr_manifest: Dict[str, Any]):
        """Called by ExpressionRuntime when a new expression is requested."""
        self._queue.append(expr_manifest)
        
        if self._current_expr is None:
            self._force_next()
        elif expr_manifest.get("interruptible") == False and expr_manifest.get("id") == "error":
            # Priority override example (Errors interrupt everything)
            self._force_next()
        elif self._current_expr.get("interruptible", True):
            elapsed = (time.time() - self._expr_start_time) * 1000
            min_duration = self._current_expr.get("minimum_duration", 0)
            if elapsed >= min_duration:
                self._force_next()

    def _force_next(self):
        """Immediately bypasses queue wait times and applies the most recent expression."""
        if not self._queue:
            return
            
        # Get the latest requested expression (LIFO for expressions usually makes sense, or we could use priority)
        next_expr = self._queue.pop()
        self._queue.clear() # Drop intermediate expressions that were skipped
        
        self._apply_expression(next_expr)

    def _apply_expression(self, expr_manifest: Dict[str, Any]):
        previous_expr_id = self._current_expr.get("id") if self._current_expr else None
        
        # Check if we are interrupting a non-interruptible expression early (or just logging it)
        if self._current_expr and not self._current_expr.get("interruptible", True):
            elapsed = (time.time() - self._expr_start_time) * 1000
            if elapsed < self._current_expr.get("minimum_duration", 0):
                if hasattr(self.event_bus, "publish"):
                    self.event_bus.publish(ExpressionInterrupted(
                        previous_expression_id=previous_expr_id,
                        by_expression_id=expr_manifest.get("id")
                    ))
        
        self._current_expr = expr_manifest
        self._expr_start_time = time.time()
        
        logger.info(f"[ExpressionScheduler] Starting expression: {expr_manifest.get('id')}")
        
        if hasattr(self.event_bus, "publish"):
            self.event_bus.publish(ExpressionStarted(
                expression_id=expr_manifest.get("id"),
                outputs=expr_manifest.get("outputs", {}),
                interruptible=expr_manifest.get("interruptible", True)
            ))

    def _process_queue(self):
        """Background loop to naturally drain the queue when minimum durations are met."""
        while self._running:
            time.sleep(0.05) # 50ms tick
            
            if not self._current_expr:
                continue
                
            elapsed = (time.time() - self._expr_start_time) * 1000
            min_duration = self._current_expr.get("minimum_duration", 0)
            
            if elapsed >= min_duration:
                # If current state finished its minimum duration, we can emit Finished if it was non-interruptible
                if not self._current_expr.get("interruptible", True):
                    # We only emit Finished once per non-interruptible expression.
                    # We can mark it as interruptible now so we don't spam.
                    self._current_expr["interruptible"] = True
                    if hasattr(self.event_bus, "publish"):
                        self.event_bus.publish(ExpressionFinished(expression_id=self._current_expr.get("id")))
                
                if self._queue:
                    self._force_next()
