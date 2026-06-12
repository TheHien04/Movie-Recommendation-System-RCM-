import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

from app.config.settings import settings

db = SQLAlchemy()


def _database_uri() -> str:
  url = settings.DATABASE_URL
  if not url:
    db_path = os.path.join(os.path.dirname(__file__), "../data/cinemate.db")
    return f"sqlite:///{db_path}"
  if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
  return url


def _upgrade_schema():
  """Lightweight SQLite migrations for additive schema changes."""
  inspector = inspect(db.engine)
  if "api_keys" not in inspector.get_table_names():
    return
  columns = {col["name"] for col in inspector.get_columns("api_keys")}
  statements = []
  if "key_hash" not in columns:
    statements.append("ALTER TABLE api_keys ADD COLUMN key_hash VARCHAR(64)")
  if "key_prefix" not in columns:
    statements.append("ALTER TABLE api_keys ADD COLUMN key_prefix VARCHAR(12)")
  with db.engine.begin() as conn:
    for stmt in statements:
      conn.execute(text(stmt))


def init_db(app):
  uri = _database_uri()
  app.config["SQLALCHEMY_DATABASE_URI"] = uri
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  if uri.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
      "pool_pre_ping": True,
      "pool_recycle": 300,
    }
  app.config["SECRET_KEY"] = settings.SECRET_KEY
  db.init_app(app)
  with app.app_context():
    import app.models  # noqa: F401 — register all tables before create_all
    db.create_all()
    _upgrade_schema()
