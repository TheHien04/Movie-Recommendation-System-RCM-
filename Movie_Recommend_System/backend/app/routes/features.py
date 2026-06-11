"""Product features: mood discovery, movie compare, advanced search."""
from urllib.parse import unquote

from flask import Blueprint, jsonify, request

from app.data.movie_repository import get_dataframe
from app.ml import hybrid_recommender
from app.ml.embeddings import SemanticRecommender
from app.services.movie_service import get_movie_details
from app.services.top5movie_service import recommend_movies

features_bp = Blueprint("features", __name__)

MOODS = {
  "happy": {"label": "Happy & Uplifting", "query": "feel-good uplifting comedy family movies"},
  "romantic": {"label": "Romantic", "query": "romantic love story drama movies"},
  "thrilling": {"label": "Thrilling", "query": "action adventure thriller suspense movies"},
  "scared": {"label": "Horror & Scary", "query": "horror scary supernatural thriller movies"},
  "mind-bending": {"label": "Mind-Bending", "query": "philosophical sci-fi twist ending movies"},
  "inspiring": {"label": "Inspiring", "query": "inspiring biographical drama underdog movies"},
  "nostalgic": {"label": "Nostalgic", "query": "classic iconic timeless movies"},
  "cozy": {"label": "Cozy Night In", "query": "warm comfort drama slice of life movies"},
}


@features_bp.route("/api/moods", methods=["GET"])
def list_moods():
  return jsonify({
    "moods": [{"id": k, "label": v["label"], "query": v["query"]} for k, v in MOODS.items()],
  })


@features_bp.route("/api/moods/<mood_id>/recommend", methods=["GET"])
def mood_recommend(mood_id):
  mood = MOODS.get(mood_id)
  if not mood:
    return jsonify({"error": "Unknown mood"}), 404
  return jsonify({
    "mood": mood_id,
    "label": mood["label"],
    "query": mood["query"],
    "recommended_movies": recommend_movies(mood["query"]),
    "model": "hybrid-v3",
  })


@features_bp.route("/api/compare", methods=["POST"])
def compare_movies():
  data = request.get_json() or {}
  titles = [str(t).strip() for t in data.get("titles", []) if str(t).strip()]
  if len(titles) < 2:
    return jsonify({"error": "Provide at least 2 titles in titles[]"}), 400
  titles = titles[:3]

  movies = []
  for title in titles:
    details = get_movie_details(title)
    if details:
      movies.append(details)
    else:
      movies.append({"title": title, "error": "not found"})

  semantic = SemanticRecommender()
  similarity_matrix = []
  if len(movies) >= 2 and all("error" not in m for m in movies):
    for i, a in enumerate(movies):
      row = []
      va = semantic.vector_for_title(a["title"])
      for j, b in enumerate(movies):
        vb = semantic.vector_for_title(b["title"])
        if va is not None and vb is not None:
          import numpy as np
          sim = float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))
          row.append(round(sim, 4))
        else:
          row.append(1.0 if i == j else 0.0)
      similarity_matrix.append(row)

  return jsonify({
    "movies": movies,
    "similarity_matrix": similarity_matrix,
    "engine": semantic.engine,
  })


@features_bp.route("/api/search/advanced", methods=["GET"])
def advanced_search():
  q = (request.args.get("q") or "").strip()
  genre = (request.args.get("genre") or "").strip().lower()
  min_rating = float(request.args.get("min_rating") or 0)
  year_from = request.args.get("year_from")
  year_to = request.args.get("year_to")
  limit = min(int(request.args.get("limit", 20)), 40)

  df = get_dataframe()
  results = []

  from app.ml.embeddings import SemanticRecommender
  semantic = SemanticRecommender()
  hits = semantic.recommend_from_query(q or genre or "popular movies", top_n=limit * 2)

  for title, score in hits.items():
    row = df[df["Title"] == title]
    if row.empty:
      continue
    movie = row.iloc[0]
    if genre and genre not in str(movie.get("Genre", "")).lower():
      continue
    imdb = float(movie.get("imdbRating") or 0)
    if imdb < min_rating:
      continue
    try:
      year = int(movie.get("Year"))
      if year_from and year < int(year_from):
        continue
      if year_to and year > int(year_to):
        continue
    except (TypeError, ValueError):
      pass
    year_val = movie.get("Year")
    try:
      year_val = int(year_val)
    except (TypeError, ValueError):
      year_val = None
    results.append({
      "title": title,
      "poster": movie.get("Poster_Link"),
      "genre": movie.get("Genre"),
      "imdb_rating": imdb,
      "year": year_val,
      "score": round(score, 4),
    })
    if len(results) >= limit:
      break

  return jsonify({"query": q, "filters": {"genre": genre, "min_rating": min_rating}, "results": results})


@features_bp.route("/api/ml/explain/<path:title>", methods=["GET"])
def explain_movie(title):
  seed = unquote(title).strip()
  details = get_movie_details(seed)
  if not details:
    return jsonify({"error": "Movie not found"}), 404

  genres = [g.strip().lower() for g in str(details.get("genre", "")).split(",") if g.strip()]
  query = f"movies like {seed} {details.get('genre', '')}"
  ranked = hybrid_recommender.recommend(
    query,
    requirements={"genres": genres[:2]},
    rule_titles=[seed],
    top_n=30,
  )
  match = next((r for r in ranked if r["title"].lower() == seed.lower()), None)
  if not match and ranked:
    match = ranked[0]

  return jsonify({
    "title": seed,
    "hybrid_score": match.get("score") if match else None,
    "breakdown": match.get("breakdown") if match else {},
    "explanation": match.get("explanation") if match else "",
    "similar_in_ranking": [r["title"] for r in ranked[:5]],
  })
