# CONFIG
.PHONY: load_env
load_env:
	uv run --env-file .env python server/scripts/load_env.py

# APP
.PHONY: run_server
run_server:
	cd server && langchain app serve --port 8080 --app main:app

.PHONY: run_client
run_client:
	cd client && uv run streamlit run app.py

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
