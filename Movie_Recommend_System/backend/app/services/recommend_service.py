"""Recommendation orchestration: rule filters + hybrid ML + optional AI fallback."""
from __future__ import annotations

import difflib
import os
from functools import lru_cache
from typing import List, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

from app.data.movie_repository import get_dataframe
from app.ml.hybrid import HybridRecommender
from app.services.nlp_service import extract_requirements

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

hybrid = HybridRecommender()


def get_df() -> pd.DataFrame:
  df = get_dataframe()
  return df


@lru_cache(maxsize=500)
def filter_local_movies(actors: Tuple[str], genres: Tuple[str], directors: Tuple[str]) -> Tuple[str, ...]:
  df = get_df()
  mask = pd.Series([True] * len(df))

  if directors:
    director_mask = pd.Series([False] * len(df))
    all_directors = set()
    for director_list in df["Director"].str.split(", "):
      if isinstance(director_list, list):
        all_directors.update(director_list)
    for director_query in directors:
      closest = difflib.get_close_matches(director_query.lower(), list(all_directors), n=1, cutoff=0.7)
      if closest:
        director_mask |= df["Director"].str.contains(closest[0], na=False)
    mask &= director_mask

  if actors:
    actor_mask = pd.Series([False] * len(df))
    all_actors = set()
    for actor_list in df["Actors"].str.lower().str.split(", "):
      if isinstance(actor_list, list):
        all_actors.update(actor_list)
    for actor in actors:
      closest = difflib.get_close_matches(actor.lower(), list(all_actors), n=1, cutoff=0.7)
      if closest:
        actor_mask |= df["Actors"].str.contains(closest[0], na=False)
    mask &= actor_mask

  if genres:
    genre_mask = pd.Series([False] * len(df))
    all_genres = set()
    for genre_list in df["Genre"].str.lower().str.split(", "):
      if isinstance(genre_list, list):
        all_genres.update(genre_list)
    for genre in genres:
      closest = difflib.get_close_matches(genre.lower(), list(all_genres), n=1, cutoff=0.6)
      if closest:
        genre_mask |= df["Genre"].str.contains(closest[0], na=False)
    mask &= genre_mask

  return tuple(df[mask]["Title"].tolist()) if mask.any() else tuple()


def _local_movies_by_actor(actor_name: str) -> Tuple[str, ...]:
  df = get_df()
  query = actor_name.lower().strip()
  mask = df["Actors"].str.lower().str.contains(query, na=False)
  if not mask.any():
    all_actors = set()
    for actor_list in df["Actors"].str.lower().str.split(", "):
      if isinstance(actor_list, list):
        all_actors.update(actor_list)
    closest = difflib.get_close_matches(query, list(all_actors), n=1, cutoff=0.7)
    if closest:
      mask = df["Actors"].str.lower().str.contains(closest[0], na=False)
  titles = df[mask].sort_values("imdbRating", ascending=False)["Title"].tolist()
  return tuple(titles[:10])


@lru_cache(maxsize=200)
def get_movies_by_actor(actor_name: str) -> Tuple[str, ...]:
  local = _local_movies_by_actor(actor_name)
  if not TMDB_API_KEY:
    return local
  try:
    url = f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={actor_name}"
    response = requests.get(url, timeout=10).json()
    if not response.get("results"):
      return local
    actor_id = response["results"][0]["id"]
    movies_url = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key={TMDB_API_KEY}"
    movies_response = requests.get(movies_url, timeout=10).json()
    tmdb_titles = tuple(movie["title"] for movie in movies_response.get("cast", [])[:10])
    return tuple(dict.fromkeys(list(tmdb_titles) + list(local)))
  except Exception:
    return local


def _ai_fallback_titles(user_input: str) -> List[str]:
  from app.services.nlp_service import get_openai_client

  df = get_df()
  prompt = f"""
  Danh sách phim: {', '.join(df['Title'].tolist()[:200])}
  Yêu cầu: {user_input}
  Chỉ trả về tên phim, mỗi dòng một tên.
  """
  response = get_openai_client().chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
  )
  titles = []
  for line in response.choices[0].message.content.split("\n"):
    line = line.strip().lstrip("-•0123456789. ")
    if not line:
      continue
    closest = difflib.get_close_matches(line, df["Title"].tolist(), n=1, cutoff=0.6)
    if closest:
      titles.append(closest[0])
  return list(dict.fromkeys(titles))


def get_movie_recommendations(user_input: str, requirements: dict, user_id: int | None = None) -> List[dict]:
  actors = tuple(requirements.get("actors", []))
  genres = tuple(requirements.get("genres", []))
  directors = tuple(requirements.get("directors", []))

  rule_titles = list(filter_local_movies(actors, genres, directors))
  for actor in requirements.get("actors", []):
    rule_titles.extend(get_movies_by_actor(actor))

  avoid_titles: List[str] = []
  if user_id:
    from app.services.user_signals import get_user_signals

    signals = get_user_signals(user_id)
    rule_titles.extend(signals["seed_titles"])
    avoid_titles = signals["avoid_titles"]
    if signals["genre_weights"] and not genres:
      requirements = dict(requirements)
      requirements["genres"] = [g for g, _ in signals["genre_weights"].most_common(2)]

  df = get_df()
  rule_titles = [title for title in dict.fromkeys(rule_titles) if title in df["Title"].values]

  hybrid_results = hybrid.recommend(
    user_input=user_input,
    requirements=requirements,
    rule_titles=rule_titles,
    avoid_titles=avoid_titles,
    top_n=5,
  )

  if hybrid_results:
    return hybrid_results

  try:
    fallback_titles = _ai_fallback_titles(user_input)
    return [{"title": title, "score": 0.0, "breakdown": {}} for title in fallback_titles[:5]]
  except Exception:
    top = df.nlargest(5, "imdbRating")
    return [{"title": row["Title"], "score": 0.0, "breakdown": {}} for _, row in top.iterrows()]
