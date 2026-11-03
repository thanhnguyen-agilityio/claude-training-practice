# Ecommerce Customer Support Agent

LangGraph agent (RAG + SQL + tools) served by FastAPI/LangServe, with a Streamlit chat client.

## Commands
- Install: `cp .env.example .env` (fill in keys), then `uv sync`
- Run: `make run_server` (8080), `make run_client` (8501)
- Test (single test: `tests/test_x.py::test_name`):
  - `cd server && uv run --env-file ../.env --with pytest python -m pytest tests`
  - `cd client && uv run --env-file ../.env --with pytest python -m pytest tests`
  - `uv run --with pytest python -m pytest scripts/tests`
- Lint/format: `uv run ruff check . && uv run ruff format .`
- E2E (calls OpenAI): `make e2e`; first run `cd e2e && npm ci && npx playwright install chromium`

## Conventions
- Imports are relative to `server/` or `client/` (`from utils.utils import ...`): run pytest and apps from that dir
- Config and env defaults live in `server/utils/constants.py`
- Tests never call OpenAI: mock with `monkeypatch`/`unittest.mock`; Streamlit UI via `AppTest`
- Every change ships with a test; one ticket per branch
- Push to both remotes: `git push origin <branch> && git push gitlab <branch>`

## Never
- Commit or print secrets / `.env`; don't run `make load_env` (prints `OPENAI_API_KEY`)
- Add dependencies without asking
- Claim done without running all three test suites and ruff
- Change `STOPPED_NOTE` on one side only (`server/routers/chat.py` ↔ `client/utils/constants.py`)
- Run `make clean_knowledge_base` or evals without asking (wipes `server/db` / costs money)
