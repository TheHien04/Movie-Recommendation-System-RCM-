def test_search_endpoint(client):
  res = client.get("/api/search?q=horror")
  assert res.status_code == 200
  assert "results" in res.get_json()


def test_trending_endpoint(client):
  res = client.get("/api/trending")
  assert res.status_code == 200
  assert "trending" in res.get_json()


def test_api_docs(client):
  res = client.get("/api/docs")
  assert res.status_code == 200


def test_register_and_profile(client):
  import uuid
  email = f"user_{uuid.uuid4().hex[:8]}@cinemate.app"
  res = client.post("/api/auth/register", json={"email": email, "password": "secret12"})
  assert res.status_code == 201
  token = res.get_json()["token"]
  profile = client.get("/api/users/profile", headers={"Authorization": f"Bearer {token}"})
  assert profile.status_code == 200
