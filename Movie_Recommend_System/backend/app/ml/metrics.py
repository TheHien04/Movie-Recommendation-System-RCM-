"""Ranking metrics used in modern recommender evaluation."""
import math
from typing import Iterable, Sequence


def precision_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int = 5) -> float:
  rec = list(recommended)[:k]
  rel = set(relevant)
  if not rec:
    return 0.0
  return len([item for item in rec if item in rel]) / len(rec)


def recall_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int = 5) -> float:
  rec = list(recommended)[:k]
  rel = set(relevant)
  if not rel:
    return 0.0
  return len([item for item in rec if item in rel]) / len(rel)


def dcg_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int = 5) -> float:
  rel = set(relevant)
  dcg = 0.0
  for idx, item in enumerate(list(recommended)[:k]):
    if item in rel:
      dcg += 1.0 / math.log2(idx + 2)
  return dcg


def ndcg_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int = 5) -> float:
  dcg = dcg_at_k(recommended, relevant, k)
  ideal_hits = min(len(set(relevant)), k)
  if ideal_hits == 0:
    return 0.0
  idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))
  return dcg / idcg if idcg else 0.0


def average_precision(recommended: Sequence[str], relevant: Iterable[str]) -> float:
  rel = set(relevant)
  if not rel:
    return 0.0
  hits = 0
  score = 0.0
  for idx, item in enumerate(recommended):
    if item in rel:
      hits += 1
      score += hits / (idx + 1)
  return score / len(rel)


def evaluate_ranking(recommended: Sequence[str], relevant: Sequence[str], k: int = 5) -> dict:
  return {
    f"precision@{k}": round(precision_at_k(recommended, relevant, k), 4),
    f"recall@{k}": round(recall_at_k(recommended, relevant, k), 4),
    f"ndcg@{k}": round(ndcg_at_k(recommended, relevant, k), 4),
    "map": round(average_precision(recommended, relevant), 4),
  }
