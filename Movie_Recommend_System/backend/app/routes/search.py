import difflib

from flask import Blueprint, jsonify, request

from app.data.movie_repository import get_dataframe
from app.ml.embeddings import SemanticRecommender

search_bp = Blueprint("search", __name__)


@search_bp.route("/api/search", methods=["GET"])
def search_movies():
  q = (request.args.get("q") or "").strip()
  limit = min(int(request.args.get("limit", 12)), 30)
  if not q:
    return jsonify({"results": []})

  df = get_dataframe()
  semantic = SemanticRecommender()
  semantic_hits = semantic.recommend_from_query(q, top_n=limit)

  fuzzy = difflib.get_close_matches(q.lower(), df["title_lower"].tolist(), n=limit, cutoff=0.5)
  title_set = list(dict.fromkeys(list(semantic_hits.keys()) + [
    df[df["title_lower"] == t]["Title"].iloc[0] for t in fuzzy if not df[df["title_lower"] == t].empty
  ]))[:limit]

  results = []
  for title in title_set:
    row = df[df["Title"] == title].iloc[0]
    results.append({
      "title": row["Title"],
      "poster": row.get("Poster_Link"),
      "genre": row.get("Genre"),
      "imdb_rating": float(row.get("imdbRating") or 0),
      "year": int(row["Year"]) if str(row.get("Year", "")).replace(".", "").isdigit() else row.get("Year"),
      "score": round(float(semantic_hits.get(title, 0)), 4),
    })

  return jsonify({"query": q, "results": results, "engine": semantic.engine})
