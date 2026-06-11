import difflib
import os
from functools import lru_cache
from urllib.parse import unquote

import pandas as pd
import requests
from dotenv import load_dotenv

from app.data.movie_repository import get_dataframe

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def get_df() -> pd.DataFrame:
  return get_dataframe()


@lru_cache(maxsize=500)
def get_movie_id_tmdb(movie_name: str):
  if not TMDB_API_KEY:
    return None
  try:
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url, timeout=10).json()
    return response["results"][0]["id"] if response.get("results") else None
  except Exception:
    return None


@lru_cache(maxsize=500)
def get_movie_trailer_tmdb(movie_id: int):
  if not TMDB_API_KEY:
    return None
  url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
  trailers = [
    video
    for video in requests.get(url, timeout=10).json().get("results", [])
    if video["type"] == "Trailer" and video["site"] == "YouTube"
  ]
  return f"https://www.youtube.com/watch?v={trailers[0]['key']}" if trailers else None


@lru_cache(maxsize=500)
def get_watch_providers_tmdb(movie_id: int):
  if not TMDB_API_KEY:
    return []
  try:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}"
    data = requests.get(url, timeout=10).json()
    us = data.get("results", {}).get("US", {})
    flatrate = us.get("flatrate", [])
    rent = us.get("rent", [])
    buy = us.get("buy", [])
    providers = []
    for group in (flatrate, rent, buy):
      for p in group:
        providers.append({
          "name": p.get("provider_name"),
          "type": "stream" if group is flatrate else ("rent" if group is rent else "buy"),
          "logo": f"https://image.tmdb.org/t/p/w45{p.get('logo_path')}" if p.get("logo_path") else None,
        })
    seen = set()
    unique = []
    for p in providers:
      key = (p["name"], p["type"])
      if key not in seen:
        seen.add(key)
        unique.append(p)
    return unique[:8]
  except Exception:
    return []


@lru_cache(maxsize=1000)
def get_movie_details(movie_name: str):
  df = get_df()
  movie_name = unquote(movie_name).lower().strip()
  matches = difflib.get_close_matches(movie_name, df["title_lower"].tolist(), n=1, cutoff=0.6)
  if not matches:
    matched_rows = df[df["title_lower"].str.contains(movie_name, case=False, na=False)]
    if not matched_rows.empty:
      matches = [matched_rows.iloc[0]["title_lower"]]

  if not matches:
    return None

  movie = df[df["title_lower"] == matches[0]].iloc[0]
  movie_id = get_movie_id_tmdb(movie["Title"])
  return {
    "title": movie["Title"],
    "overview": movie.get("Overview", "No overview available."),
    "ratingIMDB": float(movie.get("imdbRating", 0) or 0),
    "ratingRotten": float(movie.get("rottenRating", 0) or 0),
    "ratingTMDB": float(movie.get("tmdbRating", 0) or 0),
    "poster": movie.get("Poster_Link"),
    "actors": movie.get("Actors", "N/A"),
    "director": movie.get("Director", "N/A"),
    "runtime": int(movie["Runtime (min)"]) if not pd.isna(movie["Runtime (min)"]) else "N/A",
    "genre": movie.get("Genre", "N/A"),
    "year": int(movie["Year"]) if not pd.isna(movie.get("Year")) else "N/A",
    "trailer": get_movie_trailer_tmdb(movie_id) if movie_id else None,
    "watch_providers": get_watch_providers_tmdb(movie_id) if movie_id else [],
    "affiliate_search": f"https://www.google.com/search?q={movie['Title'].replace(' ', '+')}+watch+online",
  }
