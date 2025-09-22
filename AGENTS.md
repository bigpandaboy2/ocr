# Repository Guidelines

## Project Structure & Module Organization

- `main.py` boots the FastAPI gateway and wires document/user routers.
- `core/` centralizes configuration, async SQLAlchemy setup, and Redis/RQ helpers.
- `auth/`, `users/`, and `documents/` pair Pydantic schemas with services and routes; mirror that layout for new features.
- `services/` groups OCR pipeline packages (`ocr`, `preproc`, `quality`, `schema_ai`) consumed by worker tasks.
- `app_worker/` holds the RQ worker entry point, while `alembic/` stores migrations and `docs/` and `prompts/` provide reference material.

## Build, Test, and Development Commands

- `python -m venv .venv && source .venv/bin/activate` — create and activate the virtualenv.
- `pip install -r requirements.txt` — install runtime dependencies.
- `uvicorn main:app --reload` — run the API locally with hot reload.
- `python -m app_worker.main` — launch the Redis-backed worker.
- `docker-compose up --build` — bring up API, worker, Postgres, Redis, and MinIO for integration testing.
- `alembic upgrade head` — apply the latest database migrations.

## Coding Style & Naming Conventions

- Follow PEP 8 with four-space indentation and comprehensive type hints to keep FastAPI contracts explicit.
- Keep request/response models inside `schema.py` files and place business logic in `services.py` modules.
- Name async coroutines descriptively (`async def fetch_upload`) and run `black` before committing to maintain consistent formatting and sorted imports.

## Testing Guidelines

- Maintain a top-level `tests/` package that mirrors the module tree (`tests/users/test_routes.py`).
- Write `pytest` cases with explicit names and fixtures that mock Postgres, MinIO, and Redis interactions; target ≥80% coverage on touched code.
- Execute `pytest` for unit coverage and run the `docker-compose` stack for smoke checks before requesting review.

## Commit & Pull Request Guidelines

- Use imperative commit subjects scoped by module (`documents: enforce upload quotas`) and explain schema or migration updates in the body.
- Squash WIP commits so reviewers see cohesive changesets.
- PRs must include context, test evidence, environment variable changes, and screenshots or curl examples for API endpoints.

## Security & Configuration Tips

- Keep secrets in `.env`; never commit credentials or sample values.
- Rotate `MINIO_*`, `POSTGRES_*`, and `REDIS_URL` settings per environment and document defaults in `docs/`.
- Scrub customer data from logs and attachments before sharing with teammates or filing issues.

<!-- FAST-TOOLS PROMPT v1 | codex-mastery | watermark:do-not-alter -->

## CRITICAL: Use ripgrep, not grep

NEVER use grep for project-wide searches (slow, ignores .gitignore). ALWAYS use rg.

- `rg "pattern"` — search content
- `rg --files | rg "name"` — find files
- `rg -t python "def"` — language filters

## File finding

- Prefer `fd` (or `fdfind` on Debian/Ubuntu). Respects .gitignore.

## JSON

- Use `jq` for parsing and transformations.

## Install Guidance

- macOS: `brew install ripgrep fd jq`
- Debian/Ubuntu: `sudo apt update && sudo apt install -y ripgrep fd-find jq` (alias `fd=fdfind`)

## Agent Instructions

- Replace commands: grep→rg, find→rg --files/fd, ls -R→rg --files, cat|grep→rg pattern file
- Cap reads at 250 lines; prefer `rg -n -A 3 -B 3` for context
- Use `jq` for JSON instead of regex

<!-- END FAST-TOOLS PROMPT v1 | codex-mastery -->