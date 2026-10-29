# Project preflight

Read by `/auto-issues`. Project-specific checks and notes; the skill runs its generic checks first.

## Checks
Each check has a tag. `always` checks run in preflight. `server`, `client` and `browser` checks run the first time an issue needs that verification level, once per run.
1. `always` — `.env` has every key in `.env.example` (compare names only; never print values). `uv sync` succeeds.
2. `server` — start the server (Notes); `curl -sf http://localhost:8080/health` returns 200.
3. `client` — needs `server`. Start the client (Notes); `curl -sf http://localhost:8501` answers.
4. `browser` — needs `client`. Claude in Chrome: load its tools in one `ToolSearch`; `tabs_context_mcp` connects; a tab opens `http://localhost:8501`. Record separately whether `https://github.com` is signed in: only screenshot upload needs it (otherwise screenshot paths go in a PR comment).

## Verification levels
Pick the highest level the diff needs:
- **tests** — tests, CI, refactor, code style, docs: tests and lint only; start nothing.
- **curl** — `server/routers` or API behavior: tests, then `curl` against the server; evidence is the command, HTTP status, and trimmed response body.
- **browser** — `client/` or anything a user sees in the UI: tests, then the scenario in the browser with screenshots.
- `server/agent` logic (prompts, tools, graph): prefer tests. Curl a chat route only when the issue's Expected section describes an API response, and check status and shape, not exact LLM wording (each call costs money and varies).

## Notes
- Run the app: start `make run_server` (API, `http://localhost:8080`) and, for the browser level, `make run_client` (UI, `http://localhost:8501`) in the background. Stop both when done, on success or failure: stop the processes you started (keep their PIDs from the background start; `make run_server` runs `langchain app serve`, so `pkill -f uvicorn` does not match it), then confirm nothing listens on 8080 or 8501 (`lsof -ti tcp:8080 -ti tcp:8501 -sTCP:LISTEN` prints nothing).
- API routes: `GET /health`; `GET /history/?thread_id=<id>`; `POST /chat/invoke` and `POST /chat/stream` with `{"message": "...", "thread_id": "<id>", "user_id": "<id>"}`; `POST /chat/approve` and `POST /chat/reject` with `{"thread_id": "<id>", "user_id": "<id>"}`. Chat and approve/reject call the LLM; health and history do not.
- Read an issue with `gh issue view <n> --json title,body,author,labels,comments` (`--comments` fails with the Projects-classic error).
- New worktree setup: copy `server/db/` (gitignored: SQLite store and embeddings) from the main checkout, and run tests with `--env-file <main checkout>/.env`; without them server tests fail to collect (`sqlite3.OperationalError`).
- Lint: `uv run ruff check .` and `uv run ruff format --check .` (CI runs both). `main` is fully formatted, and the `.claude/settings.json` hook formats each `.py` file Claude edits, so never hand-format.
- Commit with `PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit ...`: a pre-commit hook is installed but the repo has no `.pre-commit-config.yaml`, so a plain commit fails. Check `git log` afterwards; in a `;` chain a failed commit is easy to miss.
- Browser for checks and screenshot upload: Claude in Chrome.
- `gh pr edit` fails on this repo (Projects-classic error): edit PR bodies and labels through `gh api`.
