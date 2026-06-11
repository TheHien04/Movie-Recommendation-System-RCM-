# Contributing to Cinemate

## Development Setup
```bash
# Backend
cd Movie_Recommend_System/backend
python -m venv .venv && source .venv/bin/activate
pip install -r ../../requirements.txt
cp .env.example .env
python scripts/train_models.py
python app.py

# Frontend
cd Movie_Recommend_System/web
npm install
npm run dev
```

## Quality Gates
```bash
# Backend
cd Movie_Recommend_System/backend
ruff check app tests --config ../../pyproject.toml
pytest -q --cov=app --cov-fail-under=55

# Frontend
cd Movie_Recommend_System/web
npm run lint
npm run build
```

## Pull Request Checklist
- [ ] Tests pass locally and in CI
- [ ] ML artifacts retrained if `movie.csv` or ML code changed
- [ ] No secrets committed
- [ ] OpenAPI/docs updated if API surface changed
