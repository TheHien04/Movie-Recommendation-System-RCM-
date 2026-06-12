import uuid

from app.models import UserRating, WatchlistItem
from app.services.personalization_service import get_personalized_feed
from app.services.user_signals import get_user_signals


def test_user_signals_empty_for_guest():
  signals = get_user_signals(None)
  assert signals["seed_titles"] == []
  assert signals["avoid_titles"] == []


def test_personalization_uses_ratings_and_watchlist(client):
  email = f"pers_{uuid.uuid4().hex[:8]}@cinemate.app"
  reg = client.post("/api/auth/register", json={"email": email, "password": "Secret12"})
  token = reg.get_json()["token"]
  headers = {"Authorization": f"Bearer {token}"}

  with client.application.app_context():
    from app.auth_utils import decode_token
    from app.database import db

    user_id = int(decode_token(token)["sub"])
    db.session.add(WatchlistItem(user_id=user_id, movie_title="Inception"))
    db.session.add(UserRating(user_id=user_id, movie_title="Inception", rating=5))
    db.session.add(UserRating(user_id=user_id, movie_title="Titanic", rating=1))
    db.session.commit()

    signals = get_user_signals(user_id)
    assert "Inception" in signals["seed_titles"]
    assert "Titanic" in signals["avoid_titles"]
    assert signals["genre_weights"]

    feed = get_personalized_feed(user_id, limit=5)
    assert feed
    assert all(m.get("personalized") for m in feed)
    assert all(m["title"] != "Titanic" for m in feed)

  api_feed = client.get("/api/personalized", headers=headers)
  assert api_feed.status_code == 200
  movies = api_feed.get_json()["movies"]
  assert movies
  assert movies[0].get("personalized")
