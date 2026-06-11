import os

import requests
from flask import Blueprint, jsonify

from app.data.movie_repository import get_dataframe
from app.services.personalization_service import get_personalized_feed

trending_bp = Blueprint("trending", __name__)


@trending_bp.route("/api/trending", methods=["GET"])
def trending_movies():
  api_key = os.getenv("TMDB_API_KEY")
  tmdb_titles = []
  if api_key:
    try:
      url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}"
      data = requests.get(url, timeout=10).json()
      tmdb_titles = [m["title"] for m in data.get("results", [])[:10]]
    except Exception:
      pass

  df = get_dataframe()
  cards = []
  for title in tmdb_titles:
    row = df[df["Title"].str.lower() == title.lower()]
    if not row.empty:
      r = row.iloc[0]
      cards.append({
        "title": r["Title"],
        "poster": r.get("Poster_Link"),
        "genre": r.get("Genre"),
        "imdb_rating": float(r.get("imdbRating") or 0),
        "description": r.get("Overview"),
        "source": "tmdb-trending",
      })

  if len(cards) < 6:
    for _, row in df.nlargest(6, "imdbRating").iterrows():
      if row["Title"] not in [c["title"] for c in cards]:
        cards.append({
          "title": row["Title"],
          "poster": row.get("Poster_Link"),
          "genre": row.get("Genre"),
          "imdb_rating": float(row.get("imdbRating") or 0),
          "description": row.get("Overview"),
          "source": "catalog-top",
        })

  return jsonify({"trending": cards[:10]})


@trending_bp.route("/api/personalized", methods=["GET"])
def personalized():
  from app.auth_utils import decode_token, get_bearer_token
  user_id = None
  token = get_bearer_token()
  if token:
    try:
      user_id = int(decode_token(token)["sub"])
    except Exception:
      pass
  return jsonify({"movies": get_personalized_feed(user_id)})
