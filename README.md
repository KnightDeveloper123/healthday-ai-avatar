# HealthDay AI

AI Health Day Voice Engagement & Personalized Poster Platform.
Scan → Talk → Learn → Personalize → Create → Share.

> Status: Phase 1 (project bootstrap). No AI features yet.

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

## Run

```powershell
python -m uvicorn app.main:app --reload
```

- Health: http://127.0.0.1:8000/api/v1/health
- API docs: http://127.0.0.1:8000/docs

## Test and lint

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
```
.

## API conventions

- All endpoints live under `/api/v1`.
- Every response has an `X-Request-ID` header. Clients may send their own `X-Request-ID`
  and `X-Session-ID` (8-64 chars: letters, digits, `.`, `_`, `-`).
- Errors always use this shape:

```json
{"error": {"code": "validation_error", "message": "...", "request_id": "...", "details": []}}
```

- `GET /api/v1/health` is liveness. `GET /api/v1/health/ready` is readiness (503 if a dependency fails).
- `CORS_ORIGINS` is a JSON list, e.g. `["http://localhost:3000"]`.