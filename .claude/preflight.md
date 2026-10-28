# Project preflight

Read by `/auto-issues`. Project-specific checks and notes; the skill runs its generic checks first.

## Checks
1. `.env` has every key in `.env.example` (compare names only; never print values). `uv sync` succeeds.
2. App runs: `make run_server` and `make run_client` in the background; `curl -sf http://localhost:8080/health` and `http://localhost:8501` answer. Keep them running for check 3.
3. Browser: Claude in Chrome. Load its tools in one `ToolSearch`; `tabs_context_mcp` connects; a tab opens `http://localhost:8501` and `https://github.com` signed in (needed to upload screenshots). Then stop server and client.

## Notes
- Run the app: `make run_server` (API, port 8080) and `make run_client` (UI, `http://localhost:8501`). Stop both when done.
- Browser for checks and screenshot upload: Claude in Chrome.
- `gh pr edit` fails on this repo (Projects-classic error): edit PR bodies and labels through `gh api`.
