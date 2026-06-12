"""Request ID + timing + security headers."""
import logging
import time
import uuid

from flask import g, request

from app.config.settings import settings

logger = logging.getLogger(__name__)

_SPA_CSP = (
  "default-src 'self'; "
  "script-src 'self'; "
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
  "font-src 'self' https://fonts.gstatic.com; "
  "img-src 'self' https: data: blob:; "
  "connect-src 'self' https:; "
  "frame-ancestors 'none'"
)


def register_request_hooks(app):
  @app.before_request
  def _start_timer():
    g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    g._start_time = time.perf_counter()

  @app.after_request
  def _add_headers(response):
    response.headers["X-Request-ID"] = getattr(g, "request_id", "")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.ENV == "production":
      response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if not request.path.startswith("/api"):
      response.headers["Content-Security-Policy"] = _SPA_CSP
    if request.path.startswith("/api"):
      duration_ms = round((time.perf_counter() - getattr(g, "_start_time", time.perf_counter())) * 1000, 2)
      logger.info(
        "%s %s %s",
        request.method,
        request.path,
        response.status_code,
        extra={
          "request_id": getattr(g, "request_id", ""),
          "method": request.method,
          "path": request.path,
          "status_code": response.status_code,
          "duration_ms": duration_ms,
        },
      )
    return response
