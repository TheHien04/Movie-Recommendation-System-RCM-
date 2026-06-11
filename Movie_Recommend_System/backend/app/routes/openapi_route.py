from flask import Blueprint, jsonify

openapi_bp = Blueprint("openapi", __name__)

OPENAPI_SPEC = {
  "openapi": "3.0.3",
  "info": {
    "title": "Cinemate API",
    "version": "1.0.0",
    "description": "Hybrid ML movie recommendation platform with RAG chat and B2B endpoints.",
  },
  "servers": [{"url": "/"}],
  "paths": {
    "/api/health": {"get": {"summary": "Health check", "tags": ["ops"]}},
    "/api/health/ready": {"get": {"summary": "Readiness probe", "tags": ["ops"]}},
    "/api/health/live": {"get": {"summary": "Liveness probe", "tags": ["ops"]}},
    "/recommend": {
      "post": {
        "summary": "Hybrid or RAG recommendations",
        "tags": ["recommendations"],
        "requestBody": {
          "required": True,
          "content": {"application/json": {"schema": {"type": "object", "properties": {"query": {"type": "string"}}}}},
        },
      }
    },
    "/api/search": {"get": {"summary": "Semantic movie search", "tags": ["catalog"]}},
    "/api/movies/batch": {
      "post": {
        "summary": "Batch movie metadata",
        "tags": ["catalog"],
        "requestBody": {
          "content": {"application/json": {"schema": {"type": "object", "properties": {"titles": {"type": "array", "items": {"type": "string"}}}}}},
        },
      }
    },
    "/api/rag/chat": {"post": {"summary": "RAG conversational recommendations", "tags": ["recommendations"]}},
    "/api/v1/recommend": {
      "post": {
        "summary": "B2B recommendations",
        "tags": ["b2b"],
        "security": [{"ApiKeyAuth": []}],
      }
    },
    "/api/ml/info": {"get": {"summary": "ML pipeline metadata", "tags": ["ml"]}},
    "/api/ml/similar/{title}": {"get": {"summary": "Similar movies", "tags": ["ml"]}},
    "/api/auth/register": {"post": {"summary": "Register user", "tags": ["auth"]}},
    "/api/auth/login": {"post": {"summary": "Login", "tags": ["auth"]}},
  },
  "components": {
    "securitySchemes": {
      "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
      "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
    }
  },
}


@openapi_bp.route("/api/openapi.json", methods=["GET"])
def openapi_json():
  return jsonify(OPENAPI_SPEC)
