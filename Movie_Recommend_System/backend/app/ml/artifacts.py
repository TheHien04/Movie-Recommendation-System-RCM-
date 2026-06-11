"""ML artifact loading — offline-trained models served at inference time."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, List, Optional, Tuple

import joblib
import numpy as np
from scipy import sparse

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_ROOT = _BACKEND_ROOT / "artifacts"


def get_artifact_dir(version: Optional[str] = None) -> Path:
  ver = version or os.getenv("ML_ARTIFACT_VERSION", "v1")
  return _ARTIFACT_ROOT / ver


def artifacts_available(version: Optional[str] = None) -> bool:
  d = get_artifact_dir(version)
  return (d / "manifest.json").exists() and (d / "titles.json").exists()


def load_manifest(version: Optional[str] = None) -> dict:
  path = get_artifact_dir(version) / "manifest.json"
  with open(path, encoding="utf-8") as f:
    return json.load(f)


def load_titles(version: Optional[str] = None) -> List[str]:
  path = get_artifact_dir(version) / "titles.json"
  with open(path, encoding="utf-8") as f:
    return json.load(f)


def load_tfidf_artifacts(version: Optional[str] = None):
  d = get_artifact_dir(version)
  vectorizer = joblib.load(d / "tfidf_vectorizer.joblib")
  matrix = sparse.load_npz(d / "tfidf_matrix.npz")
  return vectorizer, matrix


def load_embedding_matrix(version: Optional[str] = None) -> Optional[np.ndarray]:
  path = get_artifact_dir(version) / "embedding_matrix.npy"
  if not path.exists():
    return None
  return np.load(path)


def load_svd_artifacts(version: Optional[str] = None):
  d = get_artifact_dir(version)
  item_factors = np.load(d / "svd_item_factors.npy")
  with open(d / "titles.json", encoding="utf-8") as f:
    titles = json.load(f)
  title_to_idx = {t: i for i, t in enumerate(titles)}
  return item_factors, titles, title_to_idx
