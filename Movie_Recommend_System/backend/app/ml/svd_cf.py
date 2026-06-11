"""Matrix-factorization collaborative filtering with TruncatedSVD."""
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

from app.data.movie_repository import get_dataframe
from app.ml import artifacts as artifact_store


class SVDCollaborativeRecommender:
  """
  Build a genre-user rating matrix, factorize with SVD,
  and recommend from latent taste vectors.
  """

  def __init__(self, n_components: int = 48):
    self.n_components = n_components
    self._svd = None
    self._item_factors = None
    self._titles: List[str] = []
    self._title_to_idx: Dict[str, int] = {}

  def _ensure_fitted(self):
    if self._item_factors is not None:
      return

    if artifact_store.artifacts_available():
      self._item_factors, self._titles, self._title_to_idx = artifact_store.load_svd_artifacts()
      self._svd = object()
      return

    df = get_dataframe()
    self._titles = df["Title"].tolist()
    self._title_to_idx = {title: idx for idx, title in enumerate(self._titles)}

    genre_users: Dict[str, Dict[int, float]] = {}
    for idx, row in df.iterrows():
      rating = float(row.get("imdbRating") or 0)
      if rating <= 0:
        continue
      for genre in str(row["Genre"]).split(","):
        genre = genre.strip().lower()
        if genre:
          genre_users.setdefault(genre, {})[idx] = max(genre_users.get(genre, {}).get(idx, 0), rating)

    user_ids = sorted(genre_users.keys())
    matrix = np.zeros((len(user_ids), len(df)))
    for user_idx, genre in enumerate(user_ids):
      for movie_idx, rating in genre_users[genre].items():
        matrix[user_idx, movie_idx] = rating

    n_components = min(self.n_components, max(2, min(matrix.shape) - 1))
    self._svd = TruncatedSVD(n_components=n_components, random_state=42)
    self._item_factors = normalize(self._svd.fit_transform(matrix.T))

  def _profile_from_genres(self, genres: Tuple[str, ...]) -> np.ndarray:
    self._ensure_fitted()
    df = get_dataframe()
    mask = pd.Series([False] * len(df))
    for genre in genres:
      mask |= df["Genre"].str.contains(genre.lower(), na=False)
    indices = df[mask].index.tolist()
    if not indices:
      return self._item_factors.mean(axis=0)
    movie_indices = [self._title_to_idx[df.loc[i, "Title"]] for i in indices if df.loc[i, "Title"] in self._title_to_idx]
    if not movie_indices:
      return self._item_factors.mean(axis=0)
    return normalize(self._item_factors[movie_indices].mean(axis=0, keepdims=True))[0]

  def recommend_from_genres(self, genres: Tuple[str, ...], top_n: int = 30) -> Dict[str, float]:
    self._ensure_fitted()
    profile = self._profile_from_genres(genres)
    scores = self._item_factors @ profile
    ranked_idx = np.argsort(scores)[::-1][:top_n]
    return {self._titles[i]: float(scores[i]) for i in ranked_idx if scores[i] > 0}

  def recommend_from_seed_titles(self, seed_titles: Tuple[str, ...], top_n: int = 30) -> Dict[str, float]:
    self._ensure_fitted()
    seed_indices = [self._title_to_idx[t] for t in seed_titles if t in self._title_to_idx]
    if not seed_indices:
      return {}
    profile = normalize(self._item_factors[seed_indices].mean(axis=0, keepdims=True))[0]
    scores = self._item_factors @ profile
    results: Dict[str, float] = {}
    for idx in np.argsort(scores)[::-1]:
      title = self._titles[idx]
      if title in seed_titles:
        continue
      if scores[idx] <= 0:
        break
      results[title] = float(scores[idx])
      if len(results) >= top_n:
        break
    return results
