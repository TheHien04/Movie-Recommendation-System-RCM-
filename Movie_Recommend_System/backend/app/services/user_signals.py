"""Aggregate per-user signals for personalization and hybrid ranking."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Set

from app.data.movie_repository import get_dataframe
from app.models import UserEvent, UserRating, WatchlistItem


def _add_genres(df, title: str, counter: Counter, weight: float) -> None:
  row = df[df["Title"] == title]
  if row.empty:
    return
  for g in str(row.iloc[0]["Genre"]).split(","):
    genre = g.strip().lower()
    if genre:
      counter[genre] += weight


def get_user_signals(user_id: Optional[int]) -> Dict:
  empty = {"seed_titles": [], "avoid_titles": [], "genre_weights": Counter()}
  if not user_id:
    return empty

  df = get_dataframe()
  genre_weights: Counter = Counter()
  seed_titles: List[str] = []
  avoid: Set[str] = set()

  for item in WatchlistItem.query.filter_by(user_id=user_id).all():
    seed_titles.append(item.movie_title)
    _add_genres(df, item.movie_title, genre_weights, 1.0)

  for rating in UserRating.query.filter_by(user_id=user_id).all():
    if rating.rating >= 4:
      seed_titles.append(rating.movie_title)
      _add_genres(df, rating.movie_title, genre_weights, rating.rating / 5.0)
    elif rating.rating <= 2:
      avoid.add(rating.movie_title)

  events = (
    UserEvent.query.filter_by(user_id=user_id)
    .order_by(UserEvent.created_at.desc())
    .limit(50)
    .all()
  )
  for event in events:
    if not event.movie_title or event.event_type not in ("click", "view", "save"):
      continue
    seed_titles.append(event.movie_title)
    _add_genres(df, event.movie_title, genre_weights, 0.5)

  return {
    "seed_titles": list(dict.fromkeys(seed_titles)),
    "avoid_titles": list(avoid),
    "genre_weights": genre_weights,
  }
