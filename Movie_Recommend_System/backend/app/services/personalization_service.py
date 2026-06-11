"""Personalized recommendations from user events and watchlist."""
import json
from collections import Counter

from app.data.movie_repository import get_dataframe
from app.ml.hybrid import HybridRecommender
from app.models import UserEvent, WatchlistItem


def get_personalized_feed(user_id=None, limit: int = 8) -> list:
  df = get_dataframe()
  hybrid = HybridRecommender()

  if not user_id:
    top = df.nlargest(limit, "imdbRating")
    return [_row_to_card(row) for _, row in top.iterrows()]

  watch_titles = [w.movie_title for w in WatchlistItem.query.filter_by(user_id=user_id).all()]
  events = UserEvent.query.filter_by(user_id=user_id).order_by(UserEvent.created_at.desc()).limit(50).all()
  clicked = [e.movie_title for e in events if e.movie_title and e.event_type in ("click", "view", "save")]

  genre_counter: Counter = Counter()
  for title in watch_titles + clicked:
    row = df[df["Title"] == title]
    if row.empty:
      continue
    for g in str(row.iloc[0]["Genre"]).split(","):
      genre_counter[g.strip().lower()] += 1

  if not genre_counter:
    top = df.nlargest(limit, "imdbRating")
    return [_row_to_card(row) for _, row in top.iterrows()]

  top_genre = genre_counter.most_common(1)[0][0]
  query = f"best {top_genre} movies"
  ranked = hybrid.recommend(query, requirements={"genres": [top_genre]}, rule_titles=watch_titles[:5], top_n=limit)

  cards = []
  for item in ranked:
    row = df[df["Title"] == item["title"]]
    if row.empty:
      continue
    card = _row_to_card(row.iloc[0])
    card["personalized"] = True
    card["explanation"] = item.get("explanation", "Based on your watchlist and browsing history.")
    cards.append(card)
  return cards


def _row_to_card(row) -> dict:
  return {
    "title": row["Title"],
    "poster": row.get("Poster_Link"),
    "genre": row.get("Genre"),
    "imdb_rating": float(row.get("imdbRating") or 0),
    "description": row.get("Overview"),
    "year": row.get("Year"),
  }
