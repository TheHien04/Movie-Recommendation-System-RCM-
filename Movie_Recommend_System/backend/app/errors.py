"""Global API error handlers."""
import logging

from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
  @app.errorhandler(400)
  def bad_request(err):
    return jsonify({"error": "Bad request", "detail": str(err)}), 400

  @app.errorhandler(404)
  def not_found(err):
    return jsonify({"error": "Not found"}), 404

  @app.errorhandler(429)
  def too_many(err):
    return jsonify({"error": "Too many requests"}), 429

  @app.errorhandler(500)
  def server_error(err):
    logger.exception("Unhandled server error: %s", err)
    return jsonify({"error": "Internal server error"}), 500
