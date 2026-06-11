import json
from pathlib import Path

from flask import Blueprint, jsonify

from app.ml import artifacts as artifact_store
from app.ml import hybrid_recommender
from app.ml.hybrid import load_hybrid_weights
from app.ml.metrics import evaluate_ranking

ml_bp = Blueprint("ml", __name__)
TEST_CASES = Path(__file__).resolve().parents[2].parent / "data" / "test_cases.json"


@ml_bp.route("/api/ml/info", methods=["GET"])
def ml_info():
  manifest = artifact_store.load_manifest() if artifact_store.artifacts_available() else {}
  return jsonify({
    "pipeline": "Hybrid Recommender v3",
    "components": [
      "Transformer semantic retrieval (Sentence-BERT / TF-IDF fallback)",
      "TruncatedSVD matrix factorization",
      "NeuMF neural collaborative filtering (PyTorch)",
      "Rule-based NLP constraints",
      "MMR diversification",
      "Grid-search hyperparameter tuning",
      "Offline NDCG / MAP evaluation gate",
    ],
    "engines": hybrid_recommender.engines,
    "weights": load_hybrid_weights(),
    "artifacts": manifest,
    "model_card": "/MODEL_CARD.md",
  })


@ml_bp.route("/api/ml/evaluate", methods=["GET"])
def ml_evaluate():
  if not TEST_CASES.exists():
    return jsonify({"error": "test_cases.json not found"}), 404
  cases = json.loads(TEST_CASES.read_text(encoding="utf-8"))
  k = 5
  rows = []
  for case in cases:
    ranked = hybrid_recommender.recommend(case["input"], top_n=k)
    titles = [r["title"] for r in ranked]
    rows.append({
      "input": case["input"],
      **evaluate_ranking(titles, case.get("expected_movies", []), k=k),
      "recommended": titles,
    })
  return jsonify({
    "k": k,
    "cases": len(rows),
    "avg_ndcg": round(sum(r[f"ndcg@{k}"] for r in rows) / len(rows), 4) if rows else 0,
    "results": rows,
  })


@ml_bp.route("/api/ml/similar/<path:title>", methods=["GET"])
def similar_movies(title):
  from urllib.parse import unquote

  from app.data.movie_repository import get_dataframe
  from app.ml.embeddings import SemanticRecommender

  seed = unquote(title).strip()
  semantic = SemanticRecommender()
  scores = semantic.recommend_similar_to_movie(seed, top_n=12)
  df = get_dataframe()

  similar = []
  for movie_title, score in scores.items():
    if movie_title.lower() == seed.lower():
      continue
    row = df[df["Title"] == movie_title]
    if row.empty:
      continue
    movie = row.iloc[0]
    similar.append({
      "title": movie_title,
      "score": round(score, 4),
      "poster": movie.get("Poster_Link"),
      "imdb_rating": float(movie.get("imdbRating") or 0),
    })
    if len(similar) >= 8:
      break

  return jsonify({
    "seed": seed,
    "engine": semantic.engine,
    "similar": similar,
  })
