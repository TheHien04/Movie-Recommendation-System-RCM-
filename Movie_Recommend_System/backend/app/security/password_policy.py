"""Password strength validation."""
from __future__ import annotations

from typing import Optional


def validate_password(password: str) -> Optional[str]:
  if len(password) < 8:
    return "Password must be at least 8 characters"
  if not any(c.isalpha() for c in password):
    return "Password must include at least one letter"
  if not any(c.isdigit() for c in password):
    return "Password must include at least one number"
  return None
