from flask import Blueprint, jsonify
from sqlalchemy import text

from app.config.settings import settings
from app.data.movie_repository import get_validation_report
from app.database import db
from app.ml import artifacts as artifact_store

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health():
  return jsonify(_health_payload()), 200


@health_bp.route("/api/health/ready", methods=["GET"])
def readiness():
  payload = _health_payload()
  ready = payload["checks"]["database"] and payload["checks"]["dataset"]
  return jsonify(payload), 200 if ready else 503


@health_bp.route("/api/health/live", methods=["GET"])
def liveness():
  return jsonify({"status": "alive"}), 200


def _health_payload() -> dict:
  db_ok = False
  try:
    db.session.execute(text("SELECT 1"))
    db_ok = True
  except Exception:
    db_ok = False

  validation = None
  dataset_ok = False
  try:
    validation = get_validation_report()
    dataset_ok = bool(validation and validation.valid)
  except Exception:
    dataset_ok = False

  manifest = None
  if artifact_store.artifacts_available():
    try:
      manifest = artifact_store.load_manifest()
    except Exception:
      manifest = None

  return {
    "status": "ok" if db_ok and dataset_ok else "degraded",
    "environment": settings.ENV,
    "openai_configured": bool(settings.OPENAI_API_KEY),
    "tmdb_configured": bool(settings.TMDB_API_KEY),
    "model_version": manifest.get("version") if manifest else "runtime-fit",
    "model_family": manifest.get("model_family") if manifest else "hybrid-v3",
    "checks": {
      "database": db_ok,
      "dataset": dataset_ok,
      "ml_artifacts": artifact_store.artifacts_available(),
    },
    "dataset": {
      "row_count": validation.row_count if validation else 0,
      "data_hash": validation.data_hash if validation else None,
    },
    "offline_eval": manifest.get("offline_eval") if manifest else None,
  }
