"""API key hashing and verification."""
from __future__ import annotations

import hashlib
import secrets
from typing import Optional, Tuple

from app.database import db
from app.models import ApiKey


def hash_api_key(raw_key: str) -> str:
  return hashlib.sha256(raw_key.encode()).hexdigest()


def key_prefix(raw_key: str) -> str:
  return raw_key[:8]


def verify_api_key(raw_key: str) -> Optional[ApiKey]:
  if not raw_key:
    return None
  hashed = hash_api_key(raw_key)
  record = ApiKey.query.filter_by(key_hash=hashed, active=True).first()
  if record:
    return record
  return ApiKey.query.filter_by(key=raw_key, active=True).first()


def create_api_key_record(owner: str) -> Tuple[str, ApiKey]:
  raw = secrets.token_hex(24)
  record = ApiKey(
    key=None,
    key_hash=hash_api_key(raw),
    key_prefix=key_prefix(raw),
    owner=owner,
    active=True,
  )
  db.session.add(record)
  db.session.commit()
  return raw, record
