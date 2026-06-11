#!/usr/bin/env python3
"""Offline ML training: TF-IDF/Transformers, SVD, Neural CF (PyTorch), hyperparameter tuning."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.data.movie_repository import DATA_PATH, get_dataframe  # noqa: E402
from app.data.validation import validate_movie_dataframe  # noqa: E402
from app.ml.hybrid import HybridRecommender, save_hybrid_weights  # noqa: E402
from app.ml.hyperopt import tune_hybrid_weights  # noqa: E402
from app.ml.metrics import evaluate_ranking  # noqa: E402
from app.ml.ncf import train_ncf  # noqa: E402

ARTIFACT_VERSION = os.getenv("ML_ARTIFACT_VERSION", "v1")
ARTIFACT_DIR = BACKEND / "artifacts" / ARTIFACT_VERSION
TEST_CASES = BACKEND.parent / "data" / "test_cases.json"


def _hash_file(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _build_svd_item_factors(df: pd.DataFrame, n_components: int = 48) -> np.ndarray:
  genre_users: dict[str, dict[int, float]] = {}
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

  n_comp = min(n_components, max(2, min(matrix.shape) - 1))
  svd = TruncatedSVD(n_components=n_comp, random_state=42)
  return normalize(svd.fit_transform(matrix.T))


def _offline_eval() -> dict:
  if not TEST_CASES.exists():
    return {}
  cases = json.loads(TEST_CASES.read_text(encoding="utf-8"))
  hybrid = HybridRecommender()
  k = 5
  metrics = []
  for case in cases:
    ranked = hybrid.recommend(case["input"], top_n=k)
    titles = [r["title"] for r in ranked]
    metrics.append(evaluate_ranking(titles, case.get("expected_movies", []), k=k))

  if not metrics:
    return {}
  return {
    f"avg_precision@{k}": round(float(np.mean([m[f"precision@{k}"] for m in metrics])), 4),
    f"avg_recall@{k}": round(float(np.mean([m[f"recall@{k}"] for m in metrics])), 4),
    f"avg_ndcg@{k}": round(float(np.mean([m[f"ndcg@{k}"] for m in metrics])), 4),
    "avg_map": round(float(np.mean([m["map"] for m in metrics])), 4),
    "eval_cases": len(metrics),
  }


def train() -> dict:
  data_path = Path(DATA_PATH)
  if not data_path.exists():
    raise FileNotFoundError(DATA_PATH)

  raw = pd.read_csv(
    DATA_PATH,
    dtype={"imdbRating": float, "rottenRating": float, "tmdbRating": float},
  )
  report = validate_movie_dataframe(raw)
  if not report.valid:
    raise ValueError(f"Data validation failed: {report.errors}")

  df = get_dataframe()
  titles = df["Title"].tolist()
  corpus = df["content_text"].tolist()

  ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

  vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
  tfidf_matrix = vectorizer.fit_transform(corpus)
  joblib.dump(vectorizer, ARTIFACT_DIR / "tfidf_vectorizer.joblib")
  sparse.save_npz(ARTIFACT_DIR / "tfidf_matrix.npz", tfidf_matrix)

  engine = "tfidf"
  try:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedding_matrix = model.encode(corpus, show_progress_bar=False, normalize_embeddings=True)
    np.save(ARTIFACT_DIR / "embedding_matrix.npy", embedding_matrix)
    engine = "sentence-transformers"
    print("Trained Transformer embeddings: all-MiniLM-L6-v2")
  except Exception as exc:
    print(f"Sentence-Transformers unavailable, TF-IDF fallback: {exc}")

  item_factors = _build_svd_item_factors(df)
  np.save(ARTIFACT_DIR / "svd_item_factors.npy", item_factors)
  (ARTIFACT_DIR / "titles.json").write_text(json.dumps(titles), encoding="utf-8")

  ncf_report = train_ncf(epochs=12)
  print(f"Neural CF: {ncf_report}")

  tuned_weights = tune_hybrid_weights()
  save_hybrid_weights({k: v for k, v in tuned_weights.items() if not k.startswith("_")})
  print(f"Tuned hybrid weights: {tuned_weights}")

  eval_metrics = _offline_eval()
  manifest = {
    "version": ARTIFACT_VERSION,
    "model_family": "hybrid-v3",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "data_hash": report.data_hash,
    "csv_hash": _hash_file(data_path),
    "row_count": report.row_count,
    "engine": engine,
    "embedding_model": "all-MiniLM-L6-v2" if engine == "sentence-transformers" else None,
    "svd_components": int(item_factors.shape[1]),
    "neural_cf": ncf_report,
    "hybrid_weights": {k: v for k, v in tuned_weights.items() if not k.startswith("_")},
    "tuned_ndcg": tuned_weights.get("_tuned_ndcg"),
    "validation_warnings": report.warnings,
    "offline_eval": eval_metrics,
    "ml_stack": [
      "Transformer semantic retrieval (Sentence-BERT)",
      "TruncatedSVD matrix factorization",
      "NeuMF neural collaborative filtering (PyTorch)",
      "Rule-based NLP constraints",
      "MMR diversification",
      "Grid-search hyperparameter tuning",
    ],
  }
  (ARTIFACT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
  print(json.dumps(manifest, indent=2))
  return manifest


if __name__ == "__main__":
  train()
