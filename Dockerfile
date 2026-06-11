FROM python:3.11-slim

WORKDIR /app
COPY requirements-prod.txt /tmp/requirements-prod.txt
RUN pip install --no-cache-dir -r /tmp/requirements-prod.txt

COPY Movie_Recommend_System /movie_system
WORKDIR /movie_system/backend
ENV PYTHONPATH=/movie_system/backend
ENV FLASK_ENV=production

# Artifacts are committed — skip heavy offline training in container build
RUN test -f artifacts/v1/manifest.json

EXPOSE 10000
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"10000\")}/api/health/live')"

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-10000} -w 1 --timeout 180 app:app"]
