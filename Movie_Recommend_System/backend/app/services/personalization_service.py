"""Personalized recommendations from user events, watchlist, and ratings."""
from app.data.movie_repository import get_dataframe
from app.ml.hybrid import HybridRecommender
from app.services.user_signals import get_user_signals


def get_personalized_feed(user_id=None, limit: int = 8) -> list:
  df = get_dataframe()
  hybrid = HybridRecommender()

  if not user_id:
    top = df.nlargest(limit, "imdbRating")
    return [_row_to_card(row) for _, row in top.iterrows()]

  signals = get_user_signals(user_id)
  genre_weights = signals["genre_weights"]

  if not genre_weights and not signals["seed_titles"]:
    top = df.nlargest(limit, "imdbRating")
    return [_row_to_card(row) for _, row in top.iterrows()]

  if genre_weights:
    top_genres = [g for g, _ in genre_weights.most_common(2)]
    query = f"best {' and '.join(top_genres)} movies"
    requirements = {"genres": top_genres}
  else:
    query = "movies similar to my favorites"
    requirements = {}

  ranked = hybrid.recommend(
    query,
    requirements=requirements,
    rule_titles=signals["seed_titles"][:8],
    avoid_titles=signals["avoid_titles"],
    top_n=limit + len(signals["avoid_titles"]),
  )

  cards = []
  avoid = set(signals["avoid_titles"])
  for item in ranked:
    title = item["title"]
    if title in avoid:
      continue
    row = df[df["Title"] == title]
    if row.empty:
      continue
    card = _row_to_card(row.iloc[0])
    card["personalized"] = True
    card["explanation"] = item.get("explanation", "Based on your ratings, watchlist, and browsing.")
    cards.append(card)
    if len(cards) >= limit:
      break

  if not cards:
    top = df.nlargest(limit, "imdbRating")
    return [_row_to_card(row) for _, row in top.iterrows()]

  return cards


def _row_to_card(row) -> dict:
  year = row.get("Year")
  return {
    "title": row["Title"],
    "poster": row.get("Poster_Link"),
    "genre": row.get("Genre"),
    "imdb_rating": float(row.get("imdbRating") or 0),
    "description": row.get("Overview"),
    "year": int(year) if year is not None and str(year) != "nan" else None,
  }
