"""RAG: retrieve relevant movies then generate natural-language answer."""
import json
import os

from app.ml.embeddings import SemanticRecommender
from app.services.movie_service import get_movie_details
from app.services.nlp_service import get_openai_client

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def rag_recommend(user_input: str, top_n: int = 5) -> dict:
  semantic = SemanticRecommender()
  retrieved = semantic.recommend_from_query(user_input, top_n=12)
  titles = list(retrieved.keys())[:top_n]

  movie_cards = []
  context_lines = []
  for title in titles:
    details = get_movie_details(title)
    if not details:
      continue
    movie_cards.append({
      "title": details["title"],
      "poster": details.get("poster"),
      "total_rating": details.get("ratingIMDB"),
      "explanation": f"Semantic relevance {retrieved.get(title, 0):.3f}",
    })
    context_lines.append(
      f"- {details['title']} ({details.get('genre')}): {details.get('overview', '')[:200]}"
    )

  answer = _generate_answer(user_input, context_lines)
  return {
    "answer": answer,
    "recommended_movies": movie_cards,
    "model": "rag-v1",
    "retrieval_engine": semantic.engine,
    "sources": titles,
  }


def _generate_answer(user_input: str, context_lines: list) -> str:
  if not OPENAI_API_KEY or not context_lines:
    return (
      "Based on semantic search over our catalog, here are movies that best match your request. "
      "Add OPENAI_API_KEY for richer conversational answers."
    )
  try:
    client = get_openai_client()
    prompt = f"""You are Cinemate, a movie recommendation assistant.
User request: {user_input}

Retrieved movies:
{chr(10).join(context_lines)}

Write a concise, friendly 2-3 sentence answer explaining why these picks fit. English only."""
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.6,
    )
    return response.choices[0].message.content.strip()
  except Exception:
    return "Here are the most semantically relevant movies from our catalog for your request."
