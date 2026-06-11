def test_batch_movies(client):
  res = client.post("/api/movies/batch", json={"titles": ["Inception", "Not A Real Movie"]})
  assert res.status_code == 200
  movies = res.get_json()["movies"]
  assert len(movies) == 2
  assert movies[0]["title"] == "Inception"
  assert movies[0].get("poster")
  assert movies[1]["title"] == "Not A Real Movie"
