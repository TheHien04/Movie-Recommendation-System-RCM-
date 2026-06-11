"""Content-based filtering using TF-IDF and cosine similarity."""
from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.movie_repository import get_dataframe


class ContentBasedRecommender:
  def __init__(self):
    self._vectorizer = None
    self._matrix = None
    self._titles = None

  def _ensure_fitted(self):
    if self._matrix is not None:
      return
    df = get_dataframe()
    self._titles = df["Title"].tolist()
    self._vectorizer = TfidfVectorizer(stop_words="english", max_features=8000)
    self._matrix = self._vectorizer.fit_transform(df["content_text"])

  def recommend_from_query(self, query: str, top_n: int = 20):
    self._ensure_fitted()
    query_vec = self._vectorizer.transform([query.lower()])
    scores = cosine_similarity(query_vec, self._matrix).flatten()
    ranked = sorted(
      zip(self._titles, scores),
      key=lambda item: item[1],
      reverse=True,
    )[:top_n]
    return {title: float(score) for title, score in ranked if score > 0}

  @lru_cache(maxsize=256)
  def recommend_similar_to_movie(self, movie_title: str, top_n: int = 20):
    self._ensure_fitted()
    df = get_dataframe()
    match = df[df["title_lower"] == movie_title.lower()]
    if match.empty:
      return self.recommend_from_query(movie_title, top_n)

    idx = int(match.index[0])
    scores = cosine_similarity(self._matrix[idx], self._matrix).flatten()
    ranked_indices = np.argsort(scores)[::-1][1 : top_n + 1]
    return {
      df.iloc[i]["Title"]: float(scores[i])
      for i in ranked_indices
      if scores[i] > 0
    }
