from app.security.password_policy import validate_password


def test_password_policy_accepts_strong_password():
  assert validate_password("Secret12") is None


def test_password_policy_rejects_short_password():
  assert validate_password("abc1") == "Password must be at least 8 characters"


def test_password_policy_rejects_no_letter():
  assert validate_password("12345678") == "Password must include at least one letter"


def test_password_policy_rejects_no_digit():
  assert validate_password("abcdefgh") == "Password must include at least one number"
