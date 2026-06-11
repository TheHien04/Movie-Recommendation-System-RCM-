"""Structured JSON logging for production observability."""
import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
  def format(self, record: logging.LogRecord) -> str:
    payload = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "level": record.levelname,
      "logger": record.name,
      "message": record.getMessage(),
    }
    if record.exc_info:
      payload["exception"] = self.formatException(record.exc_info)
    for key in ("request_id", "user_id", "path", "method", "status_code", "duration_ms"):
      if hasattr(record, key):
        payload[key] = getattr(record, key)
    return json.dumps(payload, ensure_ascii=False)


def configure_logging(env: str = "development") -> None:
  root = logging.getLogger()
  root.handlers.clear()
  handler = logging.StreamHandler(sys.stdout)
  if env == "production":
    handler.setFormatter(JsonFormatter())
    root.setLevel(logging.INFO)
  else:
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    root.setLevel(logging.DEBUG)
  root.addHandler(handler)
