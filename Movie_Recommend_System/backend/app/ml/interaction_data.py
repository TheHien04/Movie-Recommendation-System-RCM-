"""Build implicit user–item interactions for neural collaborative filtering."""
from __future__ import annotations

import numpy as np

from app.data.movie_repository import get_dataframe


def build_implicit_interactions(min_rating: float = 6.5) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str], list[str]]:
  """
  Virtual users = genre taste personas + director personas.
  Positive label when a movie matches persona with sufficiently high IMDb score.
  """
  df = get_dataframe()
  titles = df["Title"].tolist()

  personas: list[tuple[str, str]] = []

  genres = set()
  for raw in df["Genre"].dropna():
    for g in str(raw).split(","):
      g = g.strip().lower()
      if g:
        genres.add(g)
  personas.extend([("genre", g) for g in sorted(genres)])

  directors = sorted({str(d).strip().lower() for d in df["Director"].dropna() if str(d).strip()})
  personas.extend([("director", d) for d in directors[:40]])

  user_ids: list[int] = []
  item_ids: list[int] = []
  labels: list[float] = []

  for user_idx, (ptype, key) in enumerate(personas):
    for _, row in df.iterrows():
      movie_idx = titles.index(row["Title"])
      rating = float(row.get("imdbRating") or 0)
      if rating <= 0:
        continue

      if ptype == "genre":
        match = key in str(row.get("Genre", "")).lower()
      else:
        match = key in str(row.get("Director", "")).lower()

      if not match:
        continue

      labels.append(1.0 if rating >= min_rating else 0.0)
      user_ids.append(user_idx)
      item_ids.append(movie_idx)

  for _, row in df.iterrows():
    rating = float(row.get("imdbRating") or 0)
    if rating < 8.0:
      continue
    movie_idx = titles.index(row["Title"])
    genre_key = str(row.get("Genre", "")).split(",")[0].strip().lower()
    persona_idx = next((i for i, (t, k) in enumerate(personas) if t == "genre" and k == genre_key), None)
    if persona_idx is not None:
      user_ids.append(persona_idx)
      item_ids.append(movie_idx)
      labels.append(1.0)

  user_keys = [f"{t}:{k}" for t, k in personas]
  return (
    np.array(user_ids, dtype=np.int64),
    np.array(item_ids, dtype=np.int64),
    np.array(labels, dtype=np.float32),
    user_keys,
    titles,
  )
