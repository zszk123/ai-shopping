# AI Shopping Compare Backend

FastAPI backend for product recognition, similarity search, price comparison and crawl management.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

## Database migration

Development can auto-create tables on startup. Production must use Alembic:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

## Checks

```bash
ruff check app tests
pytest
```

## API contract

Export the OpenAPI contract used by frontend/backend integration:

```bash
python scripts/export_openapi.py
```

## Health endpoints

- `GET /healthz`: process is alive.
- `GET /readyz`: database and Redis are reachable.

## Internal APIs

Internal spider and vector endpoints require the `X-Internal-Token` header when `INTERNAL_API_TOKEN` is configured.
