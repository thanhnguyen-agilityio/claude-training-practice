# Ecommerce Customer Support Agent

LangGraph/LangServe customer-support agent (RAG + SQL + tools) with a Streamlit chat client.

## Commands
- Install: `uv sync` (copy `.env.example` to `.env` first)
- Run: `make run_server` (port 8080) and `make run_client`
- Test: `cd server && uv run --env-file ../.env --with pytest python -m pytest tests` / `cd client && uv run --env-file ../.env --with pytest python -m pytest tests` / `uv run --with pytest python -m pytest scripts/tests`
- E2E (UI): `make e2e` starts server + client, runs `e2e/`, stops both. First run: `cd e2e && npm ci && npx playwright install chromium`; needs Node >=22.22.3 or >=24.8 and ports 8080/8501 free.
- Lint/format: `uv run ruff check . && uv run ruff format .`
- Knowledge base: `make create_knowledge_base`
- Evals: `make langsmith_experiments`, `make promptfoo_eval_agent`

## Layout
- `server/agent` — LangGraph graph, LLMs, prompts, RAG, tools
- `server/routers` — FastAPI/LangServe routes (chat, history, health)
- `server/evals` — LangSmith and Promptfoo evaluations
- `server/data` — product data and support documents
- `client` — Streamlit app (`pages/`, `services/`, `utils/`)
- `in` — input resources for AI (specs, references, sample data)
- `out` — AI outputs (e.g. `out/run-reports/` from `/auto-issues`); not edited by hand

## Conventions
- Save cost. Opus advisor. Sonnet/Haiku code. Haiku mechanical tasks. Remember!
- One ticket per branch; small commits; PR always, never push to main.
- Every change ships with a test. Keep diffs minimal.
- PR body: run `/pr` first and use its output. Never open a PR with a one-line body.
- Python 3.11+, type hints, ruff style. Tests import relative to `server/` or `client/`, so run pytest from that dir.

## Never
- Commit or print secrets / `.env`.
- Merge or claim "done" without running tests.
- Add dependencies without asking.
