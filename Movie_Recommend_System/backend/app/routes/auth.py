from flask import Blueprint, g, jsonify, request

from app.auth_utils import create_token, hash_password, login_required, verify_password
from app.database import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
  data = request.get_json() or {}
  email = (data.get("email") or "").strip().lower()
  password = data.get("password") or ""
  name = data.get("display_name") or email.split("@")[0]

  if not email or len(password) < 6:
    return jsonify({"error": "Email and password (6+ chars) required"}), 400
  if User.query.filter_by(email=email).first():
    return jsonify({"error": "Email already registered"}), 409

  user = User(email=email, password_hash=hash_password(password), display_name=name)
  db.session.add(user)
  db.session.commit()
  token = create_token(user.id, user.email)
  return jsonify({"token": token, "user": _user_json(user)}), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
  data = request.get_json() or {}
  email = (data.get("email") or "").strip().lower()
  password = data.get("password") or ""
  user = User.query.filter_by(email=email).first()
  if not user or not verify_password(user.password_hash, password):
    return jsonify({"error": "Invalid credentials"}), 401
  return jsonify({"token": create_token(user.id, user.email), "user": _user_json(user)})


@auth_bp.route("/api/auth/me", methods=["GET"])
@login_required
def me():
  user = User.query.get(g.user_id)
  if not user:
    return jsonify({"error": "User not found"}), 404
  return jsonify(_user_json(user))


def _user_json(user: User) -> dict:
  return {
    "id": user.id,
    "email": user.email,
    "display_name": user.display_name,
    "created_at": user.created_at.isoformat() if user.created_at else None,
  }
