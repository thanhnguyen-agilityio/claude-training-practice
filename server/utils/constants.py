import os

from utils.utils import get_path

# Vector DB
VECTOR_STORE_PATH: str = os.getenv(
    "VECTOR_STORE_PATH", "db/embeddings/ivy_vector_store"
)
VECTOR_STORE_COLLECTION_NAME: str = os.getenv(
    "VECTOR_STORE_COLLECTION_NAME", "ivy_collections"
)

# LLM
# CHAT_MODEL = "gpt-4o-mini"
CHAT_MODEL = "ft:gpt-4o-mini-2024-07-18:personal::B16sK6xs"
CHAT_MODEL_GPT_4O_MINI = "gpt-4o-mini"
CHAT_MODEL_TEMPERATURE = 0.2
EMBEDDING_MODEL = "text-embedding-3-small"

# PROMPT
PROMPT_FILE = get_path(
    "agent_prompt_with_fine_tuning_model_v2.md", "agent/prompts"
)
USE_PROMPT_HUB = False
PROMPT_HUB_NAME = "ecommerce-agent-prompt"

# General
MAX_WORKERS: int = 5

# Base documents
BASE_DOCUMENTS_FOLDER: str = os.getenv("BASE_DOCUMENTS_FOLDER", "data/documents")

# Splitter
SPLITTER_TEXT_CHUNK_SIZE = int(os.getenv("SPLITTER_TEXT_CHUNK_SIZE", 500))
SPLITTER_TEXT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
SPLITTER_JSON_MAX_CHUNK_SIZE = int(os.getenv("SPLITTER_JSON_MAX_CHUNK_SIZE", 500))
RECENT_MESSAGE_LIMIT = int(os.getenv("RECENT_MESSAGE_LIMIT", 5))