"""Public stats, leaderboard, and admin dashboard."""
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.auth_utils import admin_required
from app.data.movie_repository import get_dataframe
from app.database import db
from app.ml import hybrid_recommender
from app.models import Feedback, User, UserEvent, UserRating, WatchlistItem

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/api/stats/public", methods=["GET"])
def public_stats():
  df = get_dataframe()
  genres = set()
  for g in df["Genre"].dropna().astype(str):
    for part in g.split(","):
      part = part.strip()
      if part:
        genres.add(part)
  return jsonify({
    "movie_count": len(df),
    "genre_count": len(genres),
    "model": "hybrid-v3",
    "engines": hybrid_recommender.engines,
  })


@stats_bp.route("/api/leaderboard", methods=["GET"])
def leaderboard():
  genre = (request.args.get("genre") or "").strip().lower()
  limit = min(int(request.args.get("limit", 20)), 50)
  df = get_dataframe().copy()
  df["imdbRating"] = df["imdbRating"].fillna(0).astype(float)

  if genre:
    df = df[df["Genre"].astype(str).str.lower().str.contains(genre, na=False)]

  df = df.sort_values("imdbRating", ascending=False).head(limit)
  rows = []
  for _, row in df.iterrows():
    year_val = row.get("Year")
    try:
      year_val = int(year_val)
    except (TypeError, ValueError):
      year_val = None
    rows.append({
      "title": row["Title"],
      "poster": row.get("Poster_Link"),
      "genre": row.get("Genre"),
      "imdb_rating": float(row.get("imdbRating") or 0),
      "year": year_val,
      "director": row.get("Director"),
    })
  return jsonify({"genre": genre or "all", "movies": rows})


@stats_bp.route("/api/admin/dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
  feedback_rows = (
    db.session.query(Feedback.model_variant, func.avg(Feedback.rating), func.count(Feedback.id))
    .group_by(Feedback.model_variant)
    .all()
  )
  event_rows = (
    db.session.query(UserEvent.event_type, func.count(UserEvent.id))
    .group_by(UserEvent.event_type)
    .all()
  )
  return jsonify({
    "users": db.session.query(User).count(),
    "watchlist_items": db.session.query(WatchlistItem).count(),
    "ratings": db.session.query(UserRating).count(),
    "feedback_total": db.session.query(Feedback).count(),
    "feedback_by_variant": [
      {"variant": r[0], "avg_rating": float(r[1] or 0), "count": r[2]} for r in feedback_rows
    ],
    "events_by_type": [{"event_type": r[0], "count": r[1]} for r in event_rows],
    "model": "hybrid-v3",
  })
