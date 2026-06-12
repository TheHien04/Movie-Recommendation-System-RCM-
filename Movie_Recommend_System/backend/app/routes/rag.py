from flask import Blueprint, g, jsonify, request

from app.auth_utils import optional_auth
from app.middleware.rate_limit import rate_limit
from app.services.ab_test import assign_variant
from app.services.rag_service import rag_recommend

rag_bp = Blueprint("rag", __name__)


@rag_bp.route("/api/rag/chat", methods=["POST"])
@optional_auth
@rate_limit(max_requests=20)
def rag_chat():
  data = request.get_json() or {}
  query = (data.get("query") or "").strip()
  if not query:
    return jsonify({"error": "query required"}), 400

  user_key = str(g.user_id or request.remote_addr or "guest")
  variant = data.get("variant") or assign_variant(user_key)

  if variant == "B" or data.get("mode") == "rag":
    result = rag_recommend(query)
    result["variant"] = "B"
    return jsonify(result)

  from app.services.top5movie_service import recommend_movies
  user_id = getattr(g, "user_id", None)
  movies = recommend_movies(query, user_id=user_id)
  return jsonify({
    "answer": "Hybrid model recommendations based on your request.",
    "recommended_movies": movies,
    "model": "hybrid-v3",
    "personalized": bool(user_id),
    "variant": "A",
  })
