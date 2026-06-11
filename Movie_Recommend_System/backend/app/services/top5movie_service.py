import difflib
from functools import lru_cache

import requests
from dotenv import load_dotenv

from app.data.movie_repository import get_dataframe
from app.services.movie_service import get_movie_details, get_movie_id_tmdb
from app.services.nlp_service import extract_requirements
from app.services.recommend_service import get_movie_recommendations

load_dotenv()


def get_movie_details_tmdb(movie_id):
  import os

  api_key = os.getenv("TMDB_API_KEY")
  if not api_key:
    return None
  url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
  response = requests.get(url, timeout=10)
  if response.status_code == 200:
    data = response.json()
    return {
      "title": data.get("title"),
      "overview": data.get("overview"),
      "release_date": data.get("release_date"),
      "poster": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}",
    }
  return None


@lru_cache(maxsize=1000)
def find_exact_match(user_input: str):
  df = get_dataframe()
  normalized_input = user_input.strip().lower()
  matches = difflib.get_close_matches(normalized_input, df["title_lower"].tolist(), n=1, cutoff=0.8)
  if matches:
    match_score = difflib.SequenceMatcher(None, normalized_input, matches[0]).ratio()
    if match_score >= 0.8:
      return df[df["title_lower"] == matches[0]]["Title"].iloc[0]

  try:
    tmdb_id = get_movie_id_tmdb(user_input)
    if tmdb_id:
      details = get_movie_details_tmdb(tmdb_id)
      return details.get("title") if details else None
  except Exception:
    return None
  return None


@lru_cache(maxsize=1000)
def preprocess_input(user_input: str) -> str:
  original_input = user_input.strip()
  normalized_input = original_input.lower()
  df = get_dataframe()
  close_matches = difflib.get_close_matches(
    normalized_input, df["title_lower"].tolist(), n=1, cutoff=0.8
  )
  recommendation_keywords = (
    "movie", "recommend", "genre", "director", "actor", "starring",
    "horror", "comedy", "drama", "action", "sci-fi", "show me", "find",
  )
  if close_matches or any(keyword in normalized_input for keyword in recommendation_keywords):
    return original_input
  return f"movie titled {original_input}"


def _format_explanation(breakdown: dict) -> str:
  if not breakdown:
    return "Hybrid v3 ranked via semantic + SVD + neural CF with MMR diversity."
  return (
    f"Hybrid v3: semantic={breakdown.get('semantic', breakdown.get('content', 0))}, "
    f"svd={breakdown.get('collaborative', 0)}, neural={breakdown.get('neural', 0)}, "
    f"rule={breakdown.get('rule', 0)}, rating={breakdown.get('rating', 0)}"
  )


def recommend_movies(user_input: str):
  processed_input = preprocess_input(user_input)
  exact_match = find_exact_match(processed_input)
  if exact_match:
    details = get_movie_details(exact_match)
    if details:
      return [{
        "title": details["title"],
        "poster": details["poster"],
        "total_rating": details["ratingIMDB"],
        "score": 1.0,
        "explanation": "Exact title match in catalog.",
      }]

  try:
    requirements = extract_requirements(user_input)
  except Exception:
    requirements = {}

  ranked = get_movie_recommendations(user_input, requirements)
  movie_details_list = []
  for item in ranked:
    title = item["title"] if isinstance(item, dict) else item
    details = get_movie_details(title)
    if not details:
      continue
    breakdown = item.get("breakdown", {}) if isinstance(item, dict) else {}
    movie_details_list.append({
      "title": details["title"],
      "poster": details["poster"],
      "total_rating": details["ratingIMDB"],
      "score": item.get("score", 0) if isinstance(item, dict) else 0,
      "explanation": item.get("explanation") or _format_explanation(breakdown),
    })
  return movie_details_list
