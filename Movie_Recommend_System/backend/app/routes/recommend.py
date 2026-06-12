from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin

from app.auth_utils import optional_auth
from app.middleware.rate_limit import rate_limit
from app.ml import artifacts as artifact_store
from app.ml import hybrid_recommender
from app.services.ab_test import assign_variant
from app.services.rag_service import rag_recommend
from app.services.top5movie_service import recommend_movies

recommend_bp = Blueprint("recommend", __name__)


def _model_meta() -> dict:
  if artifact_store.artifacts_available():
    manifest = artifact_store.load_manifest()
    return {"model_version": manifest.get("version"), "model_family": manifest.get("model_family")}
  return {"model_version": "runtime-fit", "model_family": "hybrid-v3"}


@recommend_bp.route("/recommend", methods=["POST"])
@cross_origin()
@optional_auth
@rate_limit(max_requests=30)
def recommend():
  data = request.get_json() or {}
  user_input = data.get("query", "").strip()
  if not user_input:
    return jsonify({"error": "Query is required"}), 400

  user_key = str(g.user_id or request.remote_addr or "guest")
  variant = data.get("variant") or assign_variant(user_key)

  meta = _model_meta()
  if variant == "B":
    result = rag_recommend(user_input)
    return jsonify({
      "recommended_movies": result["recommended_movies"],
      "answer": result.get("answer"),
      "model": result["model"],
      "variant": "B",
      "engines": {"retrieval": result.get("retrieval_engine")},
      **meta,
    })

  user_id = getattr(g, "user_id", None)
  return jsonify({
    "recommended_movies": recommend_movies(user_input, user_id=user_id),
    "model": "hybrid-v3",
    "personalized": bool(user_id),
    "variant": "A",
    "engines": hybrid_recommender.engines,
    **meta,
  })
