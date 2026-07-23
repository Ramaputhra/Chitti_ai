import queue
import time

class FeedbackGovernance:
    def __init__(self, max_depth=1000, max_rate_per_sec=10):
        self.max_depth = max_depth
        self.max_rate_per_sec = max_rate_per_sec
        self.q = queue.Queue(maxsize=max_depth)
        self.last_process_time = 0.0

    def submit(self, feedback_event):
        if self.q.full():
            if feedback_event.get("classification") in ["SUCCESS", "PARTIAL_SUCCESS"]:
                return False
            else:
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass
                try:
                    self.q.put_nowait(feedback_event)
                except queue.Full:
                    pass
                return True
        else:
            self.q.put(feedback_event)
            return True

    def get_next(self):
        now = time.time()
        elapsed = now - self.last_process_time
        min_interval = 1.0 / self.max_rate_per_sec
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
            
        try:
            item = self.q.get(timeout=1.0)
            self.last_process_time = time.time()
            return item
        except queue.Empty:
            return None
