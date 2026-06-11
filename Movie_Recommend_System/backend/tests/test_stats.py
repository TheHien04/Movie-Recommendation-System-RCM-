def test_public_stats(client):
  res = client.get("/api/stats/public")
  assert res.status_code == 200
  data = res.get_json()
  assert data["movie_count"] > 0
  assert data["model"] == "hybrid-v3"


def test_leaderboard(client):
  res = client.get("/api/leaderboard?limit=5")
  assert res.status_code == 200
  movies = res.get_json()["movies"]
  assert len(movies) <= 5
  assert movies[0]["imdb_rating"] >= movies[-1]["imdb_rating"]


def test_admin_dashboard_requires_key(client):
  assert client.get("/api/admin/dashboard").status_code == 403


def test_admin_dashboard_with_key(client):
  res = client.get("/api/admin/dashboard", headers={"X-Admin-Key": "test-admin-key"})
  assert res.status_code == 200
  data = res.get_json()
  assert "users" in data
  assert data["model"] == "hybrid-v3"
