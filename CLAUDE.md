# Ecommerce Customer Support Agent

LangGraph agent (RAG + SQL + tools) served by FastAPI/LangServe, with a Streamlit chat client.

## Commands
- Install: `cp .env.example .env` (fill in keys), then `uv sync`
- Run server (port 8080): `make run_server`
- Run client (port 8501): `make run_client`
- Test server: `cd server && uv run --env-file ../.env --with pytest python -m pytest tests`
- Test client: `cd client && uv run --env-file ../.env --with pytest python -m pytest tests`
- Test scripts: `uv run --with pytest python -m pytest scripts/tests`
- Single test: `cd server && uv run --env-file ../.env --with pytest python -m pytest tests/test_recent_window.py::test_window_starts_on_human_message`
- E2E (UI, calls OpenAI): `make e2e`; first run `cd e2e && npm ci && npx playwright install chromium`; ports 8080/8501 must be free
- Lint/format: `uv run ruff check .` and `uv run ruff format .` (CI uses `ruff format --check .`)
- Knowledge base (Chroma + SQLite in `server/db`): `make create_knowledge_base`

## Layout
- `server/agent` — LangGraph graph, LLMs, prompts (`.md` files), RAG, tools
- `server/routers` — FastAPI routes: chat (streaming, stop, approval), history, health
- `server/utils` — shared helpers; `constants.py` holds config and env defaults
- `client` — Streamlit app: `app.py`, `pages/`, `services/`, `utils/`
- `server/evals` — LangSmith and Promptfoo evaluations
- `server/tests`, `client/tests`, `scripts/tests` — pytest; `e2e/` — UI tests

## Conventions
- Python 3.11+; ruff with default rules (no ruff config); isort profile black
- Imports are relative to `server/` or `client/` (`from utils.utils import ...`), so run pytest and apps from that dir
- Config: `os.getenv(NAME, default)` in `server/utils/constants.py`; `.env` is passed with `uv run --env-file`
- Module-level constants are UPPER_SNAKE; private module state starts with `_`
- Add type hints to new code (existing code is only partly typed)
- Tests: plain pytest functions `test_<behavior>`, with `monkeypatch`/`unittest.mock`; Streamlit UI tests use `streamlit.testing.v1.AppTest`
- Tests never call OpenAI (`server/tests/conftest.py` sets a placeholder key)
- Every change ships with a test; one ticket per branch; PR into `main`
- Always push to both remotes together: `git push origin <branch> && git push gitlab <branch>`

## Never
- Commit or print secrets / `.env`; don't run `make load_env` (it prints `OPENAI_API_KEY`)
- Add dependencies without asking (root `pyproject.toml` + `uv.lock`)
- Claim done without running the server, client and scripts tests plus ruff (what CI runs)
- Push to `main`
- Change `STOPPED_NOTE` on only one side (`server/routers/chat.py` and `client/utils/constants.py`)
- Run `make clean_knowledge_base` or evals without asking: they wipe `server/db` or spend OpenAI credits
