import threading
import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        threshold = now - self.window_seconds

        with self._lock:
            entries = self._hits[key]
            while entries and entries[0] <= threshold:
                entries.popleft()

            if len(entries) >= self.max_requests:
                return False

            entries.append(now)
            return True
