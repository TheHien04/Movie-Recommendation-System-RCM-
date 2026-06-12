"""Simple A/B assignment for recommendation variants."""
import hashlib

VARIANTS = {
  "A": "hybrid-v3",
  "B": "rag-v1",
}


def assign_variant(user_key: str) -> str:
  digest = hashlib.md5(user_key.encode()).hexdigest()
  return "A" if int(digest[0], 16) % 2 == 0 else "B"


def get_model_for_variant(variant: str) -> str:
  return VARIANTS.get(variant, VARIANTS["A"])
