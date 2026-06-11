def test_health_endpoint(client):
  response = client.get("/api/health")
  assert response.status_code == 200
  payload = response.get_json()
  assert payload["status"] in ("ok", "degraded")
  assert "checks" in payload


def test_random_movies(client):
  response = client.get("/random_movies")
  assert response.status_code == 200
  payload = response.get_json()
  assert "movies" in payload
  assert len(payload["movies"]) <= 3


def test_recommend_endpoint(client):
  response = client.post("/recommend", json={"query": "phim kinh dị"})
  assert response.status_code == 200
  payload = response.get_json()
  assert "recommended_movies" in payload
  assert payload["model"] in ("hybrid-v2", "hybrid-v3", "rag-v1")
