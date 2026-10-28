import os

# Importing agent.llms builds a ChatOpenAI client, which needs a key at import time.
# Tests never call the API, so a placeholder lets them run without a real secret (e.g. in CI).
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")
