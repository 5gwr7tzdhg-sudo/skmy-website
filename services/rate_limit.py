"""Small in-memory rate limiter for public forms and administrative login."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class InMemoryRateLimiter:
    def __init__(self):
        self._attempts = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key, limit, window_seconds):
        now = monotonic()
        with self._lock:
            attempts = self._attempts[key]
            cutoff = now - window_seconds
            while attempts and attempts[0] <= cutoff:
                attempts.popleft()
            if len(attempts) >= limit:
                return False
            attempts.append(now)
            return True


rate_limiter = InMemoryRateLimiter()
