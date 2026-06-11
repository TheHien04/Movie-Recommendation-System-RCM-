from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.config.settings import settings

SECRET = settings.SECRET_KEY


def hash_password(password: str) -> str:
  return generate_password_hash(password, method="pbkdf2:sha256")


def verify_password(password_hash: str, password: str) -> bool:
  return check_password_hash(password_hash, password)


def create_token(user_id: int, email: str) -> str:
  now = datetime.now(timezone.utc)
  payload = {
    "sub": str(user_id),
    "email": email,
    "iat": int(now.timestamp()),
    "exp": int((now + timedelta(hours=settings.JWT_EXPIRY_HOURS)).timestamp()),
  }
  return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
  return jwt.decode(token, SECRET, algorithms=["HS256"])


def get_bearer_token():
  auth = request.headers.get("Authorization", "")
  if auth.startswith("Bearer "):
    return auth[7:]
  return None


def login_required(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    token = get_bearer_token()
    if not token:
      return jsonify({"error": "Authentication required"}), 401
    try:
      payload = decode_token(token)
      g.user_id = int(payload["sub"])
      g.user_email = payload["email"]
    except jwt.ExpiredSignatureError:
      return jsonify({"error": "Token expired"}), 401
    except Exception:
      return jsonify({"error": "Invalid token"}), 401
    return f(*args, **kwargs)
  return wrapper


def optional_auth(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    g.user_id = None
    g.user_email = None
    token = get_bearer_token()
    if token:
      try:
        payload = decode_token(token)
        g.user_id = int(payload["sub"])
        g.user_email = payload["email"]
      except Exception:
        pass
    return f(*args, **kwargs)
  return wrapper


def admin_required(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    admin_key = request.headers.get("X-Admin-Key", "")
    expected = settings.ADMIN_API_KEY
    if not expected or admin_key != expected:
      return jsonify({"error": "Admin authentication required"}), 403
    return f(*args, **kwargs)
  return wrapper
