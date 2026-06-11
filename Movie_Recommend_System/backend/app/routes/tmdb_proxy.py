import os

import requests
from flask import Blueprint, jsonify, request

from app.middleware.rate_limit import rate_limit

tmdb_bp = Blueprint("tmdb", __name__)
BASE_URL = "https://api.themoviedb.org/3/"
ALLOWED_PREFIXES = ("search/movie", "movie/", "configuration")


@tmdb_bp.route("/api/tmdb/<path:endpoint>", methods=["GET"])
@rate_limit(max_requests=40)
def tmdb_proxy(endpoint):
  if not any(endpoint.startswith(prefix) for prefix in ALLOWED_PREFIXES):
    return jsonify({"error": "Endpoint not allowed"}), 403

  api_key = os.getenv("TMDB_API_KEY")
  if not api_key:
    return jsonify({"error": "TMDB_API_KEY not configured"}), 503

  params = dict(request.args)
  params["api_key"] = api_key
  response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=15)
  return jsonify(response.json()), response.status_code
