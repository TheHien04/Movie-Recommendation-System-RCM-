"""NLP intent extraction with OpenAI + English rule-based fallback."""
import difflib
import json
import os
import re
from functools import lru_cache

import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
_client = None

GENRE_KEYWORDS = {
  "action": ["action", "fight", "battle"],
  "comedy": ["comedy", "funny", "humor"],
  "drama": ["drama", "emotional"],
  "horror": ["horror", "scary", "frightening"],
  "thriller": ["thriller", "suspense"],
  "romance": ["romance", "romantic", "love"],
  "science fiction": ["sci-fi", "science fiction", "space", "future"],
  "adventure": ["adventure", "quest"],
  "animation": ["animation", "animated"],
  "crime": ["crime", "detective"],
  "fantasy": ["fantasy", "magic"],
}


def get_openai_client():
  global _client
  if _client is None:
    if not OPENAI_API_KEY:
      raise ValueError("OPENAI_API_KEY is not configured")
    _client = openai.OpenAI(api_key=OPENAI_API_KEY)
  return _client


def _rule_based_extract(user_input: str) -> dict:
  text = user_input.lower()
  genres = [genre for genre, keywords in GENRE_KEYWORDS.items() if any(k in text for k in keywords)]

  actors = []
  directors = []
  actor_match = re.search(
    r"(?:movies?\s+)?(?:with|starring|featuring)\s+([a-z][a-z\s\.]+?)(?:\s+movies?)?$",
    text,
  )
  if actor_match:
    actors.append(actor_match.group(1).strip())

  director_match = re.search(r"(?:directed by|from director|by)\s+([a-z\s\.]+)", text)
  if director_match:
    directors.append(director_match.group(1).strip())

  return {"actors": actors, "genres": genres, "directors": directors}


@lru_cache(maxsize=500)
def extract_requirements(user_input: str) -> dict:
  try:
    prompt = f"""
    Parse this movie request: "{user_input}"
    Return JSON with lowercase lists:
    - actors
    - genres
    - directors
    """
    response = get_openai_client().chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.2,
      response_format={"type": "json_object"},
    )
    parsed = json.loads(response.choices[0].message.content)
    parsed["genres"] = list({g.lower().strip() for g in parsed.get("genres", [])})
    return parsed
  except Exception:
    return _rule_based_extract(user_input)
