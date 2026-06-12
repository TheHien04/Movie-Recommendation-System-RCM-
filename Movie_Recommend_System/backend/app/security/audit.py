"""Security audit logging."""
from __future__ import annotations

import logging

logger = logging.getLogger("security.audit")


def log_auth_failure(event: str, email: str, ip: str) -> None:
  logger.warning(
    "security_event=%s email=%s ip=%s",
    event,
    email or "unknown",
    ip or "unknown",
  )
