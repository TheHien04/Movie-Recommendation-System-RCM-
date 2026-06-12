"""Serve Vite production build from Flask (single-service Render deploy)."""
from __future__ import annotations

from pathlib import Path

from flask import abort, send_from_directory

DIST = Path(__file__).resolve().parents[2] / "web" / "dist"
API_PREFIXES = ("api/", "recommend", "movie/", "random_movies")


def register_spa(app) -> None:
  if not DIST.exists():
    return

  @app.route("/assets/<path:filename>")
  def vite_assets(filename: str):
    return send_from_directory(DIST / "assets", filename)

  @app.route("/favicon.svg")
  def favicon():
    return send_from_directory(DIST, "favicon.svg")

  @app.route("/manifest.json")
  def manifest():
    return send_from_directory(DIST, "manifest.json")

  @app.route("/sw.js")
  def service_worker():
    return send_from_directory(DIST, "sw.js")

  @app.route("/api-endpoint.txt")
  def api_endpoint():
    endpoint_file = DIST / "api-endpoint.txt"
    if endpoint_file.is_file():
      return send_from_directory(DIST, "api-endpoint.txt")
    return "https://cinemate-live.onrender.com\n", 200, {"Content-Type": "text/plain"}

  @app.get("/<path:path>")
  def spa_catchall(path: str):
    if any(path.startswith(prefix) for prefix in API_PREFIXES):
      abort(404)
    file_path = DIST / path
    if file_path.is_file():
      return send_from_directory(DIST, path)
    return send_from_directory(DIST, "index.html")

  @app.get("/")
  def spa_index():
    return send_from_directory(DIST, "index.html")
