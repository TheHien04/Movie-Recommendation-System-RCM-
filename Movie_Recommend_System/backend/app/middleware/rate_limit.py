"""In-memory sliding-window rate limiter (per IP)."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from functools import wraps

from flask import jsonify, request

from app.config.settings import settings

_buckets: dict[str, deque[float]] = defaultdict(deque)


def _client_ip() -> str:
  forwarded = request.headers.get("X-Forwarded-For", "")
  if forwarded:
    return forwarded.split(",")[0].strip()
  return request.remote_addr or "unknown"


def rate_limit(max_requests: int | None = None, window_sec: int | None = None):
  limit = max_requests or settings.RATE_LIMIT_REQUESTS
  window = window_sec or settings.RATE_LIMIT_WINDOW_SEC

  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if request.environ.get("werkzeug.server.testing"):
        return f(*args, **kwargs)

      ip = _client_ip()
      now = time.time()
      bucket = _buckets[ip]
      while bucket and now - bucket[0] > window:
        bucket.popleft()
      if len(bucket) >= limit:
        return jsonify({"error": "Rate limit exceeded", "retry_after_sec": window}), 429
      bucket.append(now)
      return f(*args, **kwargs)
    return wrapper
  return decorator
