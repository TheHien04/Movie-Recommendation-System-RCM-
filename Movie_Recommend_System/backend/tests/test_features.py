def test_moods_list(client):
  res = client.get("/api/moods")
  assert res.status_code == 200
  data = res.get_json()
  assert len(data["moods"]) >= 6


def test_compare_movies(client):
  res = client.post("/api/compare", json={"titles": ["Inception", "Interstellar"]})
  assert res.status_code == 200
  data = res.get_json()
  assert len(data["movies"]) == 2
  assert len(data["similarity_matrix"]) == 2


def test_advanced_search(client):
  res = client.get("/api/search/advanced?q=horror&min_rating=6&limit=5")
  assert res.status_code == 200
  data = res.get_json()
  assert "results" in data
