from urllib.parse import unquote

from flask import Blueprint, jsonify, request

from app.data.movie_repository import get_dataframe
from app.services.movie_service import get_movie_details

movie_bp = Blueprint("movie", __name__)


def _cors_headers():
  return {"Access-Control-Allow-Origin": "*"}


@movie_bp.route("/random_movies", methods=["GET"])
def get_random_movies():
  df = get_dataframe()
  top_movies = df.nlargest(min(1000, len(df)), "imdbRating")
  selected_movies = top_movies.sample(n=min(3, len(top_movies)))

  movies_list = [
    {
      "title": row["Title"],
      "poster": row["Poster_Link"],
      "genre": row["Genre"],
      "actors": row["Actors"],
      "imdb_rating": row["imdbRating"],
      "rotten_rating": row["rottenRating"],
      "description": row["Overview"],
      "year": row["Year"],
      "director": row["Director"],
      "runtime": row["Runtime (min)"],
    }
    for _, row in selected_movies.iterrows()
  ]
  return jsonify({"movies": movies_list}), 200, _cors_headers()


@movie_bp.route("/api/movies/batch", methods=["POST"])
def batch_movies():
  titles = (request.get_json() or {}).get("titles", [])
  if not isinstance(titles, list):
    return jsonify({"error": "titles must be a list"}), 400

  df = get_dataframe()
  movies = []
  for raw in titles[:50]:
    title = str(raw).strip()
    if not title:
      continue
    row = df[df["Title"] == title]
    if row.empty:
      movies.append({"title": title})
      continue
    movie = row.iloc[0]
    try:
      year_out = int(movie.get("Year"))
    except (TypeError, ValueError):
      year_out = None
    movies.append({
      "title": movie["Title"],
      "poster": movie.get("Poster_Link"),
      "genre": movie.get("Genre"),
      "imdb_rating": float(movie.get("imdbRating") or 0),
      "year": year_out,
    })
  return jsonify({"movies": movies})


@movie_bp.route("/movie/<path:movie_title>", methods=["GET"])
def get_movie_info(movie_title):
  try:
    decoded_title = unquote(movie_title)
    movie = get_movie_details(decoded_title)
    if movie:
      return jsonify(movie), 200, _cors_headers()
    return jsonify({"error": "Movie not found"}), 404, _cors_headers()
  except Exception as exc:
    return jsonify({"error": str(exc)}), 500, _cors_headers()
