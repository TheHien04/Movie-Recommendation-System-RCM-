import json

from flask import Blueprint, g, jsonify, request

from app.auth_utils import login_required, optional_auth
from app.database import db
from app.models import ChatMessage, User, UserRating, WatchlistItem

users_bp = Blueprint("users", __name__)


@users_bp.route("/api/users/watchlist", methods=["GET"])
@login_required
def get_watchlist():
  items = WatchlistItem.query.filter_by(user_id=g.user_id).order_by(WatchlistItem.created_at.desc()).all()
  return jsonify({"watchlist": [i.movie_title for i in items]})


@users_bp.route("/api/users/watchlist", methods=["POST"])
@login_required
def add_watchlist():
  title = (request.get_json() or {}).get("title", "").strip()
  if not title:
    return jsonify({"error": "title required"}), 400
  exists = WatchlistItem.query.filter_by(user_id=g.user_id, movie_title=title).first()
  if not exists:
    db.session.add(WatchlistItem(user_id=g.user_id, movie_title=title))
    db.session.commit()
  return jsonify({"ok": True})


@users_bp.route("/api/users/watchlist/<path:title>", methods=["DELETE"])
@login_required
def remove_watchlist(title):
  WatchlistItem.query.filter_by(user_id=g.user_id, movie_title=title).delete()
  db.session.commit()
  return jsonify({"ok": True})


@users_bp.route("/api/users/watchlist/sync", methods=["POST"])
@login_required
def sync_watchlist():
  titles = (request.get_json() or {}).get("titles", [])
  for title in titles:
    if not WatchlistItem.query.filter_by(user_id=g.user_id, movie_title=title).first():
      db.session.add(WatchlistItem(user_id=g.user_id, movie_title=title))
  db.session.commit()
  return jsonify({"ok": True, "count": len(titles)})


@users_bp.route("/api/users/chat", methods=["GET"])
@login_required
def get_chat_history():
  msgs = ChatMessage.query.filter_by(user_id=g.user_id).order_by(ChatMessage.created_at.asc()).limit(100).all()
  return jsonify({
    "messages": [{
      "role": m.role,
      "content": m.content,
      "movies": json.loads(m.movies_json) if m.movies_json else [],
      "created_at": m.created_at.isoformat(),
    } for m in msgs],
  })


@users_bp.route("/api/users/chat", methods=["POST"])
@login_required
def save_chat():
  data = request.get_json() or {}
  db.session.add(ChatMessage(
    user_id=g.user_id,
    role=data.get("role", "user"),
    content=data.get("content", ""),
    movies_json=json.dumps(data.get("movies", [])),
  ))
  db.session.commit()
  return jsonify({"ok": True})


@users_bp.route("/api/users/profile", methods=["GET"])
@login_required
def profile():
  user = db.session.get(User, g.user_id)
  watch_count = WatchlistItem.query.filter_by(user_id=g.user_id).count()
  chat_count = ChatMessage.query.filter_by(user_id=g.user_id).count()
  rating_count = UserRating.query.filter_by(user_id=g.user_id).count()
  return jsonify({
    "user": {"id": user.id, "email": user.email, "display_name": user.display_name},
    "stats": {"watchlist": watch_count, "chat_messages": chat_count, "ratings": rating_count},
  })


@users_bp.route("/api/users/ratings", methods=["GET"])
@login_required
def get_ratings():
  items = UserRating.query.filter_by(user_id=g.user_id).order_by(UserRating.updated_at.desc()).all()
  return jsonify({
    "ratings": [{"movie_title": r.movie_title, "rating": r.rating, "updated_at": r.updated_at.isoformat()} for r in items],
  })


@users_bp.route("/api/users/ratings", methods=["POST"])
@login_required
def set_rating():
  data = request.get_json() or {}
  title = (data.get("movie_title") or "").strip()
  rating = int(data.get("rating", 0))
  if not title or rating < 1 or rating > 5:
    return jsonify({"error": "movie_title and rating (1-5) required"}), 400

  row = UserRating.query.filter_by(user_id=g.user_id, movie_title=title).first()
  if row:
    row.rating = rating
  else:
    db.session.add(UserRating(user_id=g.user_id, movie_title=title, rating=rating))
  db.session.commit()
  return jsonify({"ok": True, "movie_title": title, "rating": rating})


@users_bp.route("/api/users/ratings/<path:title>", methods=["DELETE"])
@login_required
def delete_rating(title):
  UserRating.query.filter_by(user_id=g.user_id, movie_title=title).delete()
  db.session.commit()
  return jsonify({"ok": True})
