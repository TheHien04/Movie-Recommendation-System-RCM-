FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash cinemate
WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY Movie_Recommend_System /movie_system
WORKDIR /movie_system/backend
ENV PYTHONPATH=/movie_system/backend
ENV PORT=5001
ENV FLASK_ENV=production

RUN python scripts/train_models.py

RUN chown -R cinemate:cinemate /movie_system
USER cinemate

EXPOSE 5001
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5001/api/health/live')"

CMD ["gunicorn", "-b", "0.0.0.0:5001", "-w", "2", "--timeout", "120", "app:app"]
