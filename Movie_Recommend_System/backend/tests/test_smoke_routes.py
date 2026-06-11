def test_ml_info_and_evaluate(client):
  info = client.get("/api/ml/info")
  assert info.status_code == 200
  payload = info.get_json()
  assert payload["pipeline"] == "Hybrid Recommender v3"
  assert "NeuMF" in " ".join(payload["components"])

  evaluate = client.get("/api/ml/evaluate")
  assert evaluate.status_code == 200
  eval_payload = evaluate.get_json()
  assert eval_payload["cases"] >= 8
  assert eval_payload["avg_ndcg"] >= 0.08


def test_genres_and_movie_detail(client):
  genres = client.get("/api/genres")
  assert genres.status_code == 200
  payload = genres.get_json()
  assert len(payload["genres"]) > 0

  title = payload["genres"][0]["movies"][0]["title"]
  detail = client.get(f"/movie/{title}")
  assert detail.status_code == 200


def test_feedback_and_events(client):
  feedback = client.post("/api/feedback", json={"movie_title": "Inception", "rating": 1, "query": "sci-fi"})
  assert feedback.status_code in (200, 201)

  event = client.post("/api/events", json={"event_type": "view", "movie_title": "Inception"})
  assert event.status_code in (200, 201)
