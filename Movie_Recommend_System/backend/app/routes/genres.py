from flask import Blueprint, jsonify

from app.data.movie_repository import get_dataframe

genres_bp = Blueprint("genres", __name__)

GENRE_GROUPS = {
  "Action": ["Action", "Adventure"],
  "Sci-Fi": ["Science Fiction", "Fantasy"],
  "Drama": ["Drama", "History", "Biography", "War"],
  "Thriller": ["Thriller", "Crime", "Mystery"],
  "Comedy": ["Comedy", "Romance"],
  "Horror": ["Horror"],
  "Animation": ["Animation", "Family"],
}


@genres_bp.route("/api/genres", methods=["GET"])
def browse_by_genre():
  df = get_dataframe()
  grouped = {label: [] for label in GENRE_GROUPS}

  for _, row in df.sort_values("imdbRating", ascending=False).iterrows():
    movie_genres = [g.strip().lower() for g in str(row["Genre"]).split(",")]
    for label, keys in GENRE_GROUPS.items():
      if len(grouped[label]) >= 8:
        continue
      key_set = {k.lower() for k in keys}
      if any(g in key_set for g in movie_genres):
        grouped[label].append({
          "title": row["Title"],
          "poster": row.get("Poster_Link"),
          "genre": row.get("Genre"),
          "imdb_rating": float(row.get("imdbRating") or 0),
          "overview": row.get("Overview"),
          "year": int(row["Year"]) if str(row.get("Year", "")).replace(".", "").isdigit() else row.get("Year"),
        })

  return jsonify({
    "genres": [
      {"name": name, "movies": movies}
      for name, movies in grouped.items()
      if movies
    ],
  })
