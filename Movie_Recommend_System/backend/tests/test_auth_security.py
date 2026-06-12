import uuid


def test_register_rejects_weak_password(client):
  email = f"weak_{uuid.uuid4().hex[:8]}@cinemate.app"
  res = client.post("/api/auth/register", json={"email": email, "password": "short"})
  assert res.status_code == 400
  assert "8 characters" in res.get_json()["error"]


def test_login_failure_returns_generic_error(client):
  res = client.post(
    "/api/auth/login",
    json={"email": "nobody@cinemate.app", "password": "WrongPass1"},
  )
  assert res.status_code == 401
  assert res.get_json()["error"] == "Invalid credentials"
