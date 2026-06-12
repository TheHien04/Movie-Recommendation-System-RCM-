"""Grid search hybrid fusion weights using offline NDCG@K."""
from __future__ import annotations

import json
from copy import deepcopy
from itertools import product
from pathlib import Path
from typing import Dict

import numpy as np

from app.ml.hybrid import DEFAULT_WEIGHTS, HybridRecommender, load_hybrid_weights, set_hybrid_weights
from app.ml.metrics import evaluate_ranking

TEST_CASES = Path(__file__).resolve().parents[2].parent / "data" / "test_cases.json"


def _avg_ndcg(cases: list, k: int = 5) -> float:
  hybrid = HybridRecommender()
  ndcgs = []
  for case in cases:
    ranked = hybrid.recommend(case["input"], top_n=k)
    titles = [r["title"] for r in ranked]
    ndcgs.append(evaluate_ranking(titles, case.get("expected_movies", []), k=k)[f"ndcg@{k}"])
  return float(np.mean(ndcgs)) if ndcgs else 0.0


def tune_hybrid_weights(k: int = 5, max_trials: int = 24) -> Dict[str, float]:
  if not TEST_CASES.exists():
    return load_hybrid_weights()

  cases = json.loads(TEST_CASES.read_text(encoding="utf-8"))

  set_hybrid_weights(dict(DEFAULT_WEIGHTS))
  default_ndcg = _avg_ndcg(cases, k)
  best_weights = dict(DEFAULT_WEIGHTS)
  best_ndcg = default_ndcg

  grid = {
    "semantic": [0.32, 0.35, 0.38],
    "collaborative": [0.18, 0.22, 0.25],
    "neural": [0.08, 0.10, 0.12],
    "rule": [0.15, 0.18, 0.20],
    "rating": [0.08, 0.10],
    "popularity_penalty": [0.03, 0.05],
  }

  keys = list(grid.keys())
  for values in list(product(*grid.values()))[:max_trials]:
    weights = dict(zip(keys, values))
    total = sum(weights.values())
    if total <= 0:
      continue
    normalized = {key: val / total for key, val in weights.items()}
    set_hybrid_weights(normalized)
    avg = _avg_ndcg(cases, k)
    if avg > best_ndcg:
      best_ndcg = avg
      best_weights = deepcopy(normalized)

  if best_ndcg < default_ndcg:
    set_hybrid_weights(dict(DEFAULT_WEIGHTS))
    best_weights = dict(DEFAULT_WEIGHTS)
    best_ndcg = default_ndcg

  set_hybrid_weights(best_weights)
  result = dict(best_weights)
  result["_tuned_ndcg"] = round(best_ndcg, 4)
  return result
