"""Semantic embeddings for content-based retrieval (Sentence-Transformers + TF-IDF fallback)."""
from functools import lru_cache
from typing import Dict, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.movie_repository import get_dataframe
from app.ml import artifacts as artifact_store

_EMBEDDING_MODEL = None
_USE_TRANSFORMERS = None


def _can_use_sentence_transformers() -> bool:
  global _USE_TRANSFORMERS
  if _USE_TRANSFORMERS is None:
    try:
      from sentence_transformers import SentenceTransformer  # noqa: F401
      _USE_TRANSFORMERS = True
    except Exception:
      _USE_TRANSFORMERS = False
  return _USE_TRANSFORMERS


def _get_embedding_model():
  global _EMBEDDING_MODEL
  if _EMBEDDING_MODEL is None:
    from sentence_transformers import SentenceTransformer
    _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
  return _EMBEDDING_MODEL


class SemanticRecommender:
  """Transformer embeddings when available; TF-IDF cosine similarity otherwise."""

  def __init__(self):
    self._tfidf_vectorizer: Optional[TfidfVectorizer] = None
    self._tfidf_matrix = None
    self._embedding_matrix = None
    self._titles: List[str] = []

  def _ensure_fitted(self):
    if self._titles:
      return

    if artifact_store.artifacts_available():
      self._titles = artifact_store.load_titles()
      self._embedding_matrix = artifact_store.load_embedding_matrix()
      if self._embedding_matrix is None:
        self._tfidf_vectorizer, self._tfidf_matrix = artifact_store.load_tfidf_artifacts()
      return

    df = get_dataframe()
    self._titles = df["Title"].tolist()
    corpus = df["content_text"].tolist()

    if _can_use_sentence_transformers():
      model = _get_embedding_model()
      self._embedding_matrix = model.encode(corpus, show_progress_bar=False, normalize_embeddings=True)
      return

    self._tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
    self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(corpus)

  @property
  def engine(self) -> str:
    self._ensure_fitted()
    return "sentence-transformers" if self._embedding_matrix is not None else "tfidf"

  def recommend_from_query(self, query: str, top_n: int = 30) -> Dict[str, float]:
    self._ensure_fitted()
    if self._embedding_matrix is not None:
      model = _get_embedding_model()
      query_vec = model.encode([query], normalize_embeddings=True)
      scores = cosine_similarity(query_vec, self._embedding_matrix).flatten()
    else:
      query_vec = self._tfidf_vectorizer.transform([query.lower()])
      scores = cosine_similarity(query_vec, self._tfidf_matrix).flatten()

    ranked = sorted(zip(self._titles, scores), key=lambda x: x[1], reverse=True)[:top_n]
    return {title: float(score) for title, score in ranked if score > 0}

  def recommend_similar_to_movie(self, movie_title: str, top_n: int = 20) -> Dict[str, float]:
    self._ensure_fitted()
    df = get_dataframe()
    match = df[df["title_lower"] == movie_title.lower().strip()]
    if match.empty:
      return self.recommend_from_query(movie_title, top_n)

    idx = int(match.index[0])
    if self._embedding_matrix is not None:
      vec = self._embedding_matrix[idx].reshape(1, -1)
      scores = cosine_similarity(vec, self._embedding_matrix).flatten()
    else:
      scores = cosine_similarity(self._tfidf_matrix[idx], self._tfidf_matrix).flatten()

    ranked_indices = np.argsort(scores)[::-1][1 : top_n + 1]
    return {
      self._titles[i]: float(scores[i])
      for i in ranked_indices
      if scores[i] > 0
    }

  @lru_cache(maxsize=512)
  def vector_for_title(self, title: str) -> Optional[np.ndarray]:
    self._ensure_fitted()
    df = get_dataframe()
    row = df[df["Title"] == title]
    if row.empty:
      return None
    idx = int(row.index[0])
    if self._embedding_matrix is not None:
      return self._embedding_matrix[idx]
    return self._tfidf_matrix[idx].toarray().flatten()
