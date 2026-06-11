"""Item-based collaborative filtering from genre-user rating matrix."""
from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from app.data.movie_repository import get_dataframe


class CollaborativeRecommender:
  """
  Item-item CF: each genre acts as a virtual user rating movies in that genre
  with normalized IMDb scores. Similar movies co-rated highly by genre-users.
  """

  def __init__(self):
    self._item_similarity = None
    self._title_to_idx = None
    self._titles = None

  def _ensure_fitted(self):
    if self._item_similarity is not None:
      return

    df = get_dataframe()
    self._titles = df["Title"].tolist()
    self._title_to_idx = {title: idx for idx, title in enumerate(self._titles)}

    genre_users: dict[str, dict[int, float]] = {}
    for idx, row in df.iterrows():
      rating = float(row.get("imdbRating") or 0)
      if rating <= 0:
        continue
      for genre in str(row["Genre"]).split(","):
        genre = genre.strip()
        if not genre:
          continue
        genre_users.setdefault(genre, {})[idx] = rating

    if not genre_users:
      self._item_similarity = np.eye(len(df))
      return

    user_ids = sorted(genre_users.keys())
    matrix = np.zeros((len(user_ids), len(df)))
    for user_idx, genre in enumerate(user_ids):
      for movie_idx, rating in genre_users[genre].items():
        matrix[user_idx, movie_idx] = rating

    item_vectors = matrix.T
    norms = np.linalg.norm(item_vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = item_vectors / norms
    self._item_similarity = cosine_similarity(normalized)

  @lru_cache(maxsize=256)
  def recommend_from_seed_titles(self, seed_titles, top_n: int = 20):
    self._ensure_fitted()
    if not seed_titles:
      return {}

    seed_indices = [
      self._title_to_idx[title]
      for title in seed_titles
      if title in self._title_to_idx
    ]
    if not seed_indices:
      return {}

    aggregate = self._item_similarity[seed_indices].mean(axis=0)
    ranked_indices = np.argsort(aggregate)[::-1]

    results = {}
    for idx in ranked_indices:
      title = self._titles[idx]
      if title in seed_titles:
        continue
      score = float(aggregate[idx])
      if score <= 0:
        break
      results[title] = score
      if len(results) >= top_n:
        break
    return results

  def recommend_from_genres(self, genres, top_n: int = 20):
    df = get_dataframe()
    mask = pd.Series([False] * len(df))
    for genre in genres:
      mask |= df["Genre"].str.contains(genre.lower(), na=False)
    seeds = tuple(df[mask]["Title"].head(5).tolist())
    return self.recommend_from_seed_titles(seeds, top_n)
