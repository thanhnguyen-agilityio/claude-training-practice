import os
import sys

import utils.constants as constants
from agent.llms import embeddings_model
from chromadb.errors import InvalidCollectionException
from langchain_chroma import Chroma

# Make sure server/ in the path
server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if server_path not in sys.path:
    sys.path.append(server_path)


def get_retriever(
    collection_name: str = constants.VECTOR_STORE_COLLECTION_NAME,
    persist_directory: str = constants.VECTOR_STORE_PATH,
    service_category: str = "faqs",
):
    # Access vector database from CHROME_PATH
    try:
        db: Chroma = Chroma(
            collection_name=collection_name,
            persist_directory=f"{server_path}/{persist_directory}",
            embedding_function=embeddings_model,
            create_collection_if_not_exists=False,
        )
    except InvalidCollectionException:
        raise ValueError(
            f"No documents found in the collection of vector database located at {persist_directory}."
        )

    return db.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,
            "filter": {"service_category": {"$eq": service_category}},
        },
    )
