# Cinemate Backend

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../../requirements.txt
cp .env.example .env
python app.py
```

## Tests

```bash
pytest -q
```

## ML modules

- `app/ml/content_based.py` — TF-IDF + cosine similarity
- `app/ml/collaborative.py` — item-item CF
- `app/ml/hybrid.py` — weighted hybrid scorer
