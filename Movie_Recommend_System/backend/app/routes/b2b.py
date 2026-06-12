from flask import Blueprint, jsonify, request

from app.auth_utils import admin_required
from app.middleware.rate_limit import rate_limit
from app.security.api_keys import create_api_key_record, verify_api_key
from app.services.top5movie_service import recommend_movies

b2b_bp = Blueprint("b2b", __name__)


@b2b_bp.route("/api/docs", methods=["GET"])
def api_docs():
  return jsonify({
    "name": "Cinemate B2B Recommendation API",
    "version": "1.0.0",
    "openapi": "/api/openapi.json",
    "base_url": "/api/v1",
    "authentication": "Header: X-API-Key: <your_key>",
    "endpoints": [
      {"method": "POST", "path": "/api/v1/recommend", "body": {"query": "horror movies"}},
      {"method": "GET", "path": "/api/search?q=inception"},
      {"method": "GET", "path": "/api/trending"},
      {"method": "POST", "path": "/api/rag/chat", "body": {"query": "...", "mode": "rag"}},
      {"method": "GET", "path": "/api/ml/similar/<title>"},
    ],
    "pricing_note": "Contact team for production API keys and SLA.",
  })


@b2b_bp.route("/api/v1/recommend", methods=["POST"])
@rate_limit(max_requests=30)
def b2b_recommend():
  api_key = request.headers.get("X-API-Key")
  key = verify_api_key(api_key or "")
  if not key:
    return jsonify({"error": "Invalid or missing API key"}), 403

  query = (request.get_json() or {}).get("query", "").strip()
  if not query:
    return jsonify({"error": "query required"}), 400
  return jsonify({
    "recommended_movies": recommend_movies(query),
    "api_owner": key.owner,
    "model_version": "hybrid-v3",
  })


@b2b_bp.route("/api/admin/keys", methods=["POST"])
@admin_required
def create_api_key():
  data = request.get_json() or {}
  owner = data.get("owner", "partner")
  raw_key, record = create_api_key_record(owner)
  return jsonify({
    "api_key": raw_key,
    "key_prefix": record.key_prefix,
    "owner": owner,
    "note": "Store this key securely — it cannot be retrieved again.",
  }), 201
