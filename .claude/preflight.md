# Project preflight

Read by `/auto-issues`. Project-specific checks and notes; the skill runs its generic checks first.

## Checks
1. `.env` has every key in `.env.example` (compare names only; never print values). `uv sync` succeeds.
2. App runs: `make run_server` and `make run_client` in the background; `curl -sf http://localhost:8080/health` and `http://localhost:8501` answer. Keep them running for check 3.
3. Browser: Claude in Chrome. Load its tools in one `ToolSearch`; `tabs_context_mcp` connects; a tab opens `http://localhost:8501` and `https://github.com` signed in (needed to upload screenshots). Then stop server and client (see Notes); stop them also if any check fails.

## Notes
- Run the app: start `make run_server` (API, port 8080) and `make run_client` (UI, `http://localhost:8501`) in the background. Stop both when done, on success or failure: stop the processes you started (keep their PIDs from the background start; `make run_server` runs `langchain app serve`, so `pkill -f uvicorn` does not match it), then confirm nothing listens on 8080 or 8501 (`lsof -ti tcp:8080 -ti tcp:8501 -sTCP:LISTEN` prints nothing).
- Browser for checks and screenshot upload: Claude in Chrome.
- `gh pr edit` fails on this repo (Projects-classic error): edit PR bodies and labels through `gh api`.
