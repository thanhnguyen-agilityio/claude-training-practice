# CONFIG
.PHONY: load_env
load_env:
	uv run --env-file .env python server/scripts/load_env.py

# APP
.PHONY: run_server
run_server:
	cd server && uv run --env-file ../.env langchain app serve --port 8080 --app main:app

.PHONY: run_client
run_client:
	cd client && uv run --env-file ../.env streamlit run app.py

# E2E: start server and client, run e2e/ against them, stop both even on failure.
# First run: cd e2e && npm ci && npx playwright install chromium
.PHONY: e2e
e2e:
	@if lsof -ti tcp:8080 -ti tcp:8501 -sTCP:LISTEN >/dev/null; then echo "Port 8080 or 8501 in use: stop the app first"; exit 1; fi; \
	$(MAKE) run_server > /tmp/e2e-server.log 2>&1 & \
	$(MAKE) run_client > /tmp/e2e-client.log 2>&1 & \
	trap 'lsof -ti tcp:8080 -ti tcp:8501 -sTCP:LISTEN | xargs kill 2>/dev/null' EXIT; \
	for i in $$(seq 90); do curl -sf http://localhost:8080/health >/dev/null && curl -sf http://localhost:8501 >/dev/null && up=1 && break; sleep 2; done; \
	[ -n "$$up" ] || { echo "App did not start: see /tmp/e2e-server.log, /tmp/e2e-client.log"; exit 1; }; \
	cd e2e && E2E_TELEMETRY_DISABLED=1 uv run --env-file ../.env npx e2e run

# KNOWLEDGE BASE
.PHONY: create_knowledge_base
create_knowledge_base:
	uv run python server/scripts/create_database.py && uv run server/agent/rag/ingest.py --force true

.PHONY: clean_knowledge_base
clean_knowledge_base:
	uv run rm -rf server/db && uv run mkdir server/db

.PHONY: create_database
create_database:
	uv run python server/scripts/create_database.py

.PHONY: ingest_documents
ingest_documents:
	uv run server/agent/rag/ingest.py --force true

# EVALUATION
# - LangSmith
.PHONY: langsmith_experiments
langsmith_experiments:
	cd server && uv run evals/langsmith/experiment.py && cd ..

# - PromptFoo
.PHONY: promptfoo_eval_retriever
promptfoo_eval_retriever:
	cd server/evals/promptfoo && npx promptfoo@latest eval  -c ./promptfooconfigs/retriever_promptfooconfig.yaml --no-cache && cd ../..

.PHONY: promptfoo_eval_agent
promptfoo_eval_agent:
	cd server/evals/promptfoo && npx promptfoo@latest eval  -c ./promptfooconfigs/agent_promptfooconfig.yaml --no-cache && cd ../..

.PHONY: promptfoo_view
promptfoo_view:
	npx promptfoo@latest view

.PHONY: promptfoo_eval_debug
promptfoo_eval_debug:
	cd server/evals/promptfoo && LOG_LEVEL=debug npx promptfoo@latest eval  -c ./promptfooconfigs/agent_promptfooconfig.yaml --no-cache
