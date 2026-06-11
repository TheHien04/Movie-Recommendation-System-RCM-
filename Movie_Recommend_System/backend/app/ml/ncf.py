"""Neural Collaborative Filtering (NeuMF-style) with PyTorch."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.data.movie_repository import get_dataframe
from app.ml import artifacts as artifact_store

_TORCH_AVAILABLE = None
_NCF_MODEL = None
_NCF_META: Optional[dict] = None


def _torch_available() -> bool:
  global _TORCH_AVAILABLE
  if _TORCH_AVAILABLE is None:
    try:
      import torch  # noqa: F401
      _TORCH_AVAILABLE = True
    except Exception:
      _TORCH_AVAILABLE = False
  return _TORCH_AVAILABLE


def _artifact_paths():
  d = artifact_store.get_artifact_dir()
  return d / "ncf_model.pt", d / "ncf_meta.json"


class NeuMFModule:
  """GMF + MLP fusion — He et al. NCF architecture (simplified)."""

  def __init__(self, n_users: int, n_items: int, embed_dim: int = 32, mlp_hidden: Tuple[int, ...] = (64, 32)):
    import torch.nn as nn

    class _NeuMF(nn.Module):
      def __init__(self):
        super().__init__()
        self.user_embed = nn.Embedding(n_users, embed_dim)
        self.item_embed = nn.Embedding(n_items, embed_dim)
        layers: list = []
        in_dim = embed_dim * 2
        for hidden in mlp_hidden:
          layers.extend([nn.Linear(in_dim, hidden), nn.ReLU(), nn.Dropout(0.1)])
          in_dim = hidden
        layers.append(nn.Linear(in_dim, 1))
        self.mlp = nn.Sequential(*layers)

      def forward(self, user_ids, item_ids):
        import torch

        u = self.user_embed(user_ids)
        i = self.item_embed(item_ids)
        gmf = u * i
        return self.mlp(torch.cat([gmf, u + i], dim=-1)).squeeze(-1)

    self._net = _NeuMF()

  def parameters(self):
    return self._net.parameters()

  def train(self, mode=True):
    self._net.train(mode)
    return self

  def eval(self):
    self._net.eval()
    return self

  def state_dict(self):
    return self._net.state_dict()

  def load_state_dict(self, state):
    self._net.load_state_dict(state)

  def __call__(self, user_ids, item_ids):
    return self._net(user_ids, item_ids)


def train_ncf(
  epochs: int = 12,
  batch_size: int = 256,
  lr: float = 1e-3,
  embed_dim: int = 32,
) -> dict:
  if not _torch_available():
    return {"trained": False, "reason": "PyTorch not installed"}

  import torch
  import torch.nn as nn
  from torch.utils.data import DataLoader, TensorDataset

  from app.ml.interaction_data import build_implicit_interactions

  user_ids, item_ids, labels, user_keys, titles = build_implicit_interactions()
  if len(labels) < 50:
    return {"trained": False, "reason": "insufficient interactions"}

  n_users = len(user_keys)
  n_items = len(titles)

  model = NeuMFModule(n_users, n_items, embed_dim=embed_dim)
  optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
  criterion = nn.BCEWithLogitsLoss()

  dataset = TensorDataset(
    torch.tensor(user_ids, dtype=torch.long),
    torch.tensor(item_ids, dtype=torch.long),
    torch.tensor(labels, dtype=torch.float32),
  )
  loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

  model.train()
  losses = []
  for _ in range(epochs):
    epoch_loss = 0.0
    for batch_u, batch_i, batch_y in loader:
      optimizer.zero_grad()
      logits = model(batch_u, batch_i)
      loss = criterion(logits, batch_y)
      loss.backward()
      optimizer.step()
      epoch_loss += float(loss.item())
    losses.append(round(epoch_loss / max(len(loader), 1), 4))

  artifact_store.get_artifact_dir().mkdir(parents=True, exist_ok=True)
  model_path, meta_path = _artifact_paths()
  torch.save(model.state_dict(), model_path)

  meta = {
    "n_users": n_users,
    "n_items": n_items,
    "embed_dim": embed_dim,
    "user_keys": user_keys,
    "titles": titles,
    "epochs": epochs,
    "final_loss": losses[-1] if losses else None,
    "loss_curve": losses,
    "interactions": int(len(labels)),
  }
  meta_path.write_text(json.dumps(meta), encoding="utf-8")
  return {"trained": True, **meta}


def _load_ncf():
  global _NCF_MODEL, _NCF_META
  if _NCF_MODEL is not None:
    return _NCF_MODEL, _NCF_META

  if not _torch_available() or not artifact_store.artifacts_available():
    return None, None

  model_path, meta_path = _artifact_paths()
  if not model_path.exists() or not meta_path.exists():
    return None, None

  import torch

  meta = json.loads(meta_path.read_text(encoding="utf-8"))
  model = NeuMFModule(meta["n_users"], meta["n_items"], embed_dim=meta["embed_dim"])
  state = torch.load(model_path, map_location="cpu")
  model.load_state_dict(state)
  model.eval()
  _NCF_MODEL = model
  _NCF_META = meta
  return model, meta


class NeuralCFRecommender:
  """Score movies via trained NeuMF for query-matched virtual taste personas."""

  def __init__(self):
    self._model = None
    self._meta = None

  def _ensure_loaded(self):
    if self._model is None:
      self._model, self._meta = _load_ncf()

  @property
  def available(self) -> bool:
    self._ensure_loaded()
    return self._model is not None

  def _persona_indices_for_query(self, query: str) -> List[int]:
    self._ensure_loaded()
    if not self._meta:
      return []
    q = query.lower()
    indices = []
    for idx, key in enumerate(self._meta["user_keys"]):
      _, persona = key.split(":", 1)
      if persona in q or any(tok in persona for tok in q.split() if len(tok) > 3):
        indices.append(idx)
    return indices[:8] or [0]

  def recommend_from_query(self, query: str, top_n: int = 30) -> Dict[str, float]:
    import torch

    self._ensure_loaded()
    if not self._model or not self._meta:
      return {}

    persona_ids = self._persona_indices_for_query(query)
    titles = self._meta["titles"]
    n_items = len(titles)
    item_tensor = torch.arange(n_items, dtype=torch.long)
    scores_acc = np.zeros(n_items, dtype=np.float64)

    with torch.no_grad():
      for uid in persona_ids:
        user_tensor = torch.full((n_items,), uid, dtype=torch.long)
        logits = self._model(user_tensor, item_tensor)
        probs = torch.sigmoid(logits).numpy()
        scores_acc += probs

    scores_acc /= max(len(persona_ids), 1)
    ranked = np.argsort(scores_acc)[::-1][:top_n]
    return {titles[i]: float(scores_acc[i]) for i in ranked if scores_acc[i] > 0}

  def recommend_from_seed_titles(self, seed_titles: Tuple[str, ...], top_n: int = 30) -> Dict[str, float]:
    if not seed_titles:
      return {}
    return self.recommend_from_query(" ".join(seed_titles), top_n=top_n)
