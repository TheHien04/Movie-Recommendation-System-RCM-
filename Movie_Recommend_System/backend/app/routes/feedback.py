from flask import Blueprint, g, jsonify, request

from app.auth_utils import optional_auth
from app.database import db
from app.models import Feedback, UserEvent

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/api/feedback", methods=["POST"])
@optional_auth
def submit_feedback():
  data = request.get_json() or {}
  rating = int(data.get("rating", 0))
  title = (data.get("movie_title") or "").strip()
  if rating not in (1, -1) or not title:
    return jsonify({"error": "movie_title and rating (1|-1) required"}), 400

  db.session.add(Feedback(
    user_id=g.user_id,
    query=data.get("query"),
    movie_title=title,
    rating=rating,
    model_variant=data.get("variant"),
  ))
  db.session.commit()
  return jsonify({"ok": True})


@feedback_bp.route("/api/events", methods=["POST"])
@optional_auth
def track_event():
  data = request.get_json() or {}
  event_type = data.get("event_type", "click")
  db.session.add(UserEvent(
    user_id=g.user_id,
    event_type=event_type,
    movie_title=data.get("movie_title"),
    metadata_json=data.get("metadata"),
  ))
  db.session.commit()
  return jsonify({"ok": True})


@feedback_bp.route("/api/events/recent", methods=["GET"])
@optional_auth
def recent_events():
  limit = min(int(request.args.get("limit", 12)), 30)
  q = UserEvent.query.filter(UserEvent.event_type == "view")
  if g.user_id:
    q = q.filter(UserEvent.user_id == g.user_id)
  rows = q.order_by(UserEvent.created_at.desc()).limit(limit).all()
  seen = set()
  titles = []
  for row in rows:
    if row.movie_title and row.movie_title not in seen:
      seen.add(row.movie_title)
      titles.append(row.movie_title)
  return jsonify({"titles": titles[:limit]})


@feedback_bp.route("/api/feedback/stats", methods=["GET"])
def feedback_stats():
  from sqlalchemy import func
  rows = db.session.query(Feedback.model_variant, func.avg(Feedback.rating), func.count(Feedback.id)).group_by(Feedback.model_variant).all()
  return jsonify({
    "variants": [{"variant": r[0], "avg_rating": float(r[1] or 0), "count": r[2]} for r in rows],
  })
