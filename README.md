# Spy Cat Agency (FastAPI + SQLite)

Small REST API to manage spy cats, their missions, and targets. Cat breeds are validated against TheCatAPI on creation.

Tech stack: FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite, HTTPX, Uvicorn.

## Quickstart

```bash
# 1) Create and activate a virtualenv
python -m venv venv
source venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the API
uvicorn app.main:app --reload
```

- Docs (Swagger): http://127.0.0.1:8000/docs
- Docs (ReDoc): http://127.0.0.1:8000/redoc

The SQLite database file `sca.db` is created automatically on first start (in the project root). Delete it to reset state.

## Project Layout

```
app/
  main.py          # FastAPI app + router wiring
  db.py            # SQLAlchemy engine/session setup (SQLite)
  models.py        # ORM models: Cat, Mission, Target
  schemas.py       # Pydantic v2 schemas / validation
  deps.py          # DB session dependency
  api/routes/
    cats.py        # CRUD for cats, TheCatAPI validation
    missions.py    # Missions CRUD, assign cat, update targets
```

## Business Rules & Validation

- Cat breed is validated against https://api.thecatapi.com/v1/breeds when creating a cat.
  - If TheCatAPI is unreachable → 503 Service Unavailable.
  - If breed is unknown per TheCatAPI → 422 Unprocessable Entity.
- A cat cannot be deleted if it has an active mission (assigned and not completed) → 409 Conflict.
- Create mission with 1–3 targets. Each target has `name`, `country`, optional `notes`.
- Assigning a cat to a mission:
  - Mission must not already have a cat.
  - Cat must exist and not have another active mission → 409 Conflict.
- Updating a target:
  - `notes` can be edited only if neither the target nor the mission is completed.
  - `completed` can only be set from false → true (cannot reopen) → 409 Conflict if attempted.
  - When all targets are completed, the mission is marked completed automatically.

## Postman Collection

Use the Postman collection to explore all endpoints and sample payloads:

"https://dansamedov-6140138.postman.co/workspace/Danylo-Samedov's-Workspace~268d5138-7cb3-48ca-8ab5-8f8a690fdd86/collection/48826425-45b41f99-d997-4b0a-a3d9-c6b239c03000?action=share&source=copy-link&creator=48826425"

Tips

- Set the base URL to `http://127.0.0.1:8000` (or your chosen port).
- If the collection uses an environment variable (e.g., `baseUrl`), create a Postman environment and assign it.

## Requirements

- Python 3.10+ recommended
