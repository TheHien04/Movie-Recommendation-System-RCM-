import os

from flask import Flask
from flask_cors import CORS

from app.config.settings import settings
from app.errors import register_error_handlers
from app.logging_config import configure_logging
from app.middleware.request_context import register_request_hooks


def create_app():
  configure_logging(settings.ENV)
  app = Flask(__name__)
  if os.getenv("ALLOW_ALL_CORS", "").lower() in ("1", "true", "yes"):
    CORS(app, resources={r"/*": {"origins": "*"}})
  else:
    CORS(app, resources={r"/*": {"origins": settings.CORS_ORIGINS}}, supports_credentials=True)

  if settings.SENTRY_DSN:
    try:
      import sentry_sdk
      from sentry_sdk.integrations.flask import FlaskIntegration

      sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[FlaskIntegration()], traces_sample_rate=0.1)
    except Exception:
      pass

  from app.database import init_db
  init_db(app)

  register_request_hooks(app)
  register_error_handlers(app)

  from app.routes.auth import auth_bp
  from app.routes.b2b import b2b_bp
  from app.routes.feedback import feedback_bp
  from app.routes.genres import genres_bp
  from app.routes.health import health_bp
  from app.routes.ml import ml_bp
  from app.routes.movie import movie_bp
  from app.routes.openapi_route import openapi_bp
  from app.routes.rag import rag_bp
  from app.routes.recommend import recommend_bp
  from app.routes.search import search_bp
  from app.routes.tmdb_proxy import tmdb_bp
  from app.routes.trending import trending_bp
  from app.routes.features import features_bp
  from app.routes.stats import stats_bp
  from app.routes.users import users_bp

  for bp in [
    health_bp, openapi_bp, ml_bp, movie_bp, recommend_bp, tmdb_bp,
    auth_bp, users_bp, search_bp, rag_bp, feedback_bp,
    trending_bp, b2b_bp, genres_bp, features_bp, stats_bp,
  ]:
    app.register_blueprint(bp)

  from app.spa import register_spa
  register_spa(app)

  return app
