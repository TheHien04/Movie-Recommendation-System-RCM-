from datetime import datetime

from app.database import db


class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(255), unique=True, nullable=False)
  password_hash = db.Column(db.String(255), nullable=False)
  display_name = db.Column(db.String(120))
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  watchlist = db.relationship("WatchlistItem", backref="user", lazy=True)
  chats = db.relationship("ChatMessage", backref="user", lazy=True)
  feedback = db.relationship("Feedback", backref="user", lazy=True)
  events = db.relationship("UserEvent", backref="user", lazy=True)
  ratings = db.relationship("UserRating", backref="user", lazy=True)


class UserRating(db.Model):
  __tablename__ = "user_ratings"
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  movie_title = db.Column(db.String(500), nullable=False)
  rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  __table_args__ = (db.UniqueConstraint("user_id", "movie_title", name="uq_user_movie_rating"),)


class WatchlistItem(db.Model):
  __tablename__ = "watchlist"
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  movie_title = db.Column(db.String(500), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
  __tablename__ = "chat_messages"
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  role = db.Column(db.String(20), nullable=False)
  content = db.Column(db.Text, nullable=False)
  movies_json = db.Column(db.Text)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
  __tablename__ = "feedback"
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
  query = db.Column(db.Text)
  movie_title = db.Column(db.String(500), nullable=False)
  rating = db.Column(db.Integer, nullable=False)  # 1 or -1
  model_variant = db.Column(db.String(50))
  created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserEvent(db.Model):
  __tablename__ = "user_events"
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
  event_type = db.Column(db.String(50), nullable=False)
  movie_title = db.Column(db.String(500))
  metadata_json = db.Column(db.Text)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ApiKey(db.Model):
  __tablename__ = "api_keys"
  id = db.Column(db.Integer, primary_key=True)
  key = db.Column(db.String(64), unique=True, nullable=True)  # legacy plaintext keys
  key_hash = db.Column(db.String(64), unique=True, nullable=True)
  key_prefix = db.Column(db.String(12), nullable=True)
  owner = db.Column(db.String(120))
  active = db.Column(db.Boolean, default=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
