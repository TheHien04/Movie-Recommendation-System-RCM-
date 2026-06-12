"""Central application configuration."""
from __future__ import annotations

import logging
import os
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_DEV_SECRET = "cinemate-dev-secret-change-in-production"


class Settings:
  SECRET_KEY: str = os.getenv("SECRET_KEY", _DEV_SECRET)
  DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
  ADMIN_API_KEY: Optional[str] = os.getenv("ADMIN_API_KEY")
  OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
  TMDB_API_KEY: Optional[str] = os.getenv("TMDB_API_KEY")
  CORS_ORIGINS: List[str] = [
    o.strip() for o in os.getenv(
      "CORS_ORIGINS",
      "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173",
    ).split(",") if o.strip()
  ]
  JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "168"))
  ML_ARTIFACT_VERSION: str = os.getenv("ML_ARTIFACT_VERSION", "v1")
  RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
  RATE_LIMIT_WINDOW_SEC: int = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
  ENV: str = os.getenv("FLASK_ENV", "development")
  SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")


settings = Settings()


def validate_production_config() -> None:
  if settings.ENV != "production":
    return
  if settings.SECRET_KEY in (_DEV_SECRET, "change-me-in-production"):
    raise RuntimeError("SECRET_KEY must be set to a strong random value in production")
  if len(settings.SECRET_KEY) < 32:
    logger.warning("SECRET_KEY is shorter than 32 characters — prefer a longer random key")
  if not settings.ADMIN_API_KEY or settings.ADMIN_API_KEY == "change-me-admin-key":
    logger.warning("ADMIN_API_KEY should be set to a strong random value in production")
