"""Maximal Marginal Relevance (MMR) for diverse recommendations."""
from typing import Dict, List

import numpy as np


def maximal_marginal_relevance(
  candidates: List[str],
  relevance: Dict[str, float],
  vectors: Dict[str, np.ndarray],
  top_n: int = 5,
  lambda_mult: float = 0.72,
) -> List[str]:
  if not candidates:
    return []

  selected: List[str] = []
  pool = [title for title in candidates if title in relevance]

  while pool and len(selected) < top_n:
    best_title = None
    best_score = -np.inf

    for title in pool:
      rel = relevance.get(title, 0.0)
      if not selected:
        mmr_score = rel
      else:
        sims = []
        vec = vectors.get(title)
        if vec is None:
          diversity_penalty = 0
        else:
          for chosen in selected:
            chosen_vec = vectors.get(chosen)
            if chosen_vec is None:
              continue
            denom = (np.linalg.norm(vec) * np.linalg.norm(chosen_vec)) or 1
            sims.append(float(np.dot(vec, chosen_vec) / denom))
          diversity_penalty = max(sims) if sims else 0
        mmr_score = lambda_mult * rel - (1 - lambda_mult) * diversity_penalty

      if mmr_score > best_score:
        best_score = mmr_score
        best_title = title

    if best_title is None:
      break
    selected.append(best_title)
    pool.remove(best_title)

  return selected
