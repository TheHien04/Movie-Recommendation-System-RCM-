"""Lazy hybrid recommender — avoids loading torch/transformers at gunicorn boot on Render free tier."""
from __future__ import annotations

from typing import Optional

from app.ml.hybrid import HybridRecommender

_instance: Optional[HybridRecommender] = None


class _LazyHybrid:
  def __getattr__(self, name: str):
    global _instance
    if _instance is None:
      _instance = HybridRecommender()
    return getattr(_instance, name)


hybrid_recommender = _LazyHybrid()
