"""Central application configuration."""
from __future__ import annotations

import os
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


class Settings:
  SECRET_KEY: str = os.getenv("SECRET_KEY", "cinemate-dev-secret-change-in-production")
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
