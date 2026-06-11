import os
import sys

import pytest  # noqa: F401

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from app.ml.embeddings import SemanticRecommender
from app.ml.hybrid import HybridRecommender
from app.ml.metrics import ndcg_at_k, precision_at_k
from app.ml.svd_cf import SVDCollaborativeRecommender
from app.services.nlp_service import _rule_based_extract


def test_rule_based_genre_extraction():
  result = _rule_based_extract("recommend horror movies")
  assert "horror" in result["genres"]


def test_semantic_returns_results():
  semantic = SemanticRecommender()
  results = semantic.recommend_from_query("science fiction space adventure", top_n=5)
  assert len(results) > 0


def test_svd_collaborative_returns_results():
  cf = SVDCollaborativeRecommender()
  results = cf.recommend_from_genres(("drama",), top_n=5)
  assert len(results) > 0


def test_hybrid_ranking():
  hybrid = HybridRecommender()
  ranked = hybrid.recommend("horror movies", requirements={"genres": ["horror"]}, top_n=5)
  assert len(ranked) <= 5
  assert "title" in ranked[0]
  assert "score" in ranked[0]


def test_ranking_metrics():
  assert precision_at_k(["A", "B", "C"], ["A", "C"], k=3) == pytest.approx(2 / 3)
  assert ndcg_at_k(["A", "B", "C"], ["A", "C"], k=3) > 0
