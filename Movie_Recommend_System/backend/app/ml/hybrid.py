"""Hybrid recommender v3: semantic CBF + SVD-CF + Neural CF + rules + MMR."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from app.data.movie_repository import get_dataframe
from app.ml.embeddings import SemanticRecommender
from app.ml.mmr import maximal_marginal_relevance
from app.ml.ncf import NeuralCFRecommender
from app.ml.svd_cf import SVDCollaborativeRecommender

DEFAULT_WEIGHTS = {
  "semantic": 0.32,
  "collaborative": 0.18,
  "neural": 0.18,
  "rule": 0.18,
  "rating": 0.09,
  "popularity_penalty": 0.05,
}

_WEIGHTS_CACHE: Optional[Dict[str, float]] = None


def _weights_path() -> Path:
  from app.ml.artifacts import get_artifact_dir
  return get_artifact_dir() / "hybrid_weights.json"


def load_hybrid_weights() -> Dict[str, float]:
  global _WEIGHTS_CACHE
  if _WEIGHTS_CACHE is not None:
    return _WEIGHTS_CACHE

  path = _weights_path()
  if path.exists():
    raw = json.loads(path.read_text(encoding="utf-8"))
    _WEIGHTS_CACHE = {k: float(v) for k, v in raw.items() if not k.startswith("_")}
    return _WEIGHTS_CACHE

  _WEIGHTS_CACHE = dict(DEFAULT_WEIGHTS)
  return _WEIGHTS_CACHE


def set_hybrid_weights(weights: Dict[str, float]) -> None:
  global _WEIGHTS_CACHE
  _WEIGHTS_CACHE = dict(weights)


def save_hybrid_weights(weights: Dict[str, float]) -> None:
  path = _weights_path()
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(weights, indent=2), encoding="utf-8")
  set_hybrid_weights(weights)


class HybridRecommender:
  def __init__(self):
    self.semantic = SemanticRecommender()
    self.cf = SVDCollaborativeRecommender()
    self.ncf = NeuralCFRecommender()

  @property
  def engines(self) -> dict:
    return {
      "content_engine": self.semantic.engine,
      "collaborative_engine": "truncated-svd",
      "neural_engine": "neumf-pytorch" if self.ncf.available else "unavailable",
      "diversification": "mmr",
      "fusion": "weighted-hybrid-v3",
    }

  def recommend(
    self,
    user_input: str,
    requirements: Optional[dict] = None,
    rule_titles: Optional[List[str]] = None,
    top_n: int = 5,
  ) -> List[dict]:
    requirements = requirements or {}
    rule_titles = rule_titles or []
    weights = load_hybrid_weights()
    df = get_dataframe()

    semantic_scores = self.semantic.recommend_from_query(user_input, top_n=40)
    cf_scores = self.cf.recommend_from_genres(tuple(requirements.get("genres", [])), top_n=40)
    neural_scores = self.ncf.recommend_from_query(user_input, top_n=40) if self.ncf.available else {}

    if rule_titles:
      cf_from_rules = self.cf.recommend_from_seed_titles(tuple(rule_titles[:6]), top_n=40)
      for title, score in cf_from_rules.items():
        cf_scores[title] = max(cf_scores.get(title, 0), score)
      if self.ncf.available:
        ncf_rules = self.ncf.recommend_from_seed_titles(tuple(rule_titles[:6]), top_n=40)
        for title, score in ncf_rules.items():
          neural_scores[title] = max(neural_scores.get(title, 0), score)

    max_imdb = float(df["imdbRating"].max() or 1)
    popularity = df.set_index("Title")["imdbRating"].fillna(0).astype(float).to_dict()
    popularity_max = max(popularity.values()) if popularity else 1.0

    candidates = set(semantic_scores) | set(cf_scores) | set(neural_scores) | set(rule_titles)
    relevance: Dict[str, float] = {}
    breakdowns: Dict[str, dict] = {}

    for title in candidates:
      if title not in df["Title"].values:
        continue

      rule_score = 1.0 if title in rule_titles else 0.0
      imdb = float(df.loc[df["Title"] == title, "imdbRating"].iloc[0] or 0)
      rating_score = imdb / max_imdb if max_imdb else 0
      pop_penalty = (popularity.get(title, 0) / popularity_max) if popularity_max else 0

      final_score = (
        weights.get("semantic", 0) * semantic_scores.get(title, 0)
        + weights.get("collaborative", 0) * cf_scores.get(title, 0)
        + weights.get("neural", 0) * neural_scores.get(title, 0)
        + weights.get("rule", 0) * rule_score
        + weights.get("rating", 0) * rating_score
        - weights.get("popularity_penalty", 0) * pop_penalty
      )

      relevance[title] = max(final_score, 0)
      breakdowns[title] = {
        "semantic": round(semantic_scores.get(title, 0), 4),
        "collaborative": round(cf_scores.get(title, 0), 4),
        "neural": round(neural_scores.get(title, 0), 4),
        "rule": round(rule_score, 4),
        "rating": round(rating_score, 4),
        "popularity_penalty": round(pop_penalty, 4),
      }

    vectors = {title: self.semantic.vector_for_title(title) for title in relevance}
    vectors = {k: v for k, v in vectors.items() if v is not None}
    ordered_titles = maximal_marginal_relevance(
      sorted(relevance, key=relevance.get, reverse=True),
      relevance,
      vectors,
      top_n=top_n,
    )

    engine_note = self.semantic.engine
    if self.ncf.available:
      engine_note += " + NeuMF"

    return [
      {
        "title": title,
        "score": round(relevance[title], 4),
        "breakdown": breakdowns[title],
        "explanation": f"Hybrid v3: {engine_note}, SVD-CF, neural CF, rules, MMR.",
      }
      for title in ordered_titles
    ]
