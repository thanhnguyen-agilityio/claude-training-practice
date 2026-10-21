"""
Retriever provider for PromptFoo
Use it to test the retriever of the chatbot
"""

import os
import sys

# CONFIG PATH WHEN RUN SCRIPT (via Python runner in Promptfoo) TO ALLOW IMPORT MODULE FROM ROOT DIR
# ----------------------------------------------------------------
server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../."))
for path in [server_path]:
    if path not in sys.path:
        sys.path.append(path)

# ----------------------------------------------------------------
from rag.retriever import get_retriever  # noqa: E402


def call_api(query, options, context):
    context_vars = context["vars"]
    persist_directory = f"{server_path}/db/embeddings/ivy_vector_store"
    collection_name = "ivy_collections"

    query = context_vars["query"]
    docs = []
    doc_ids = set()
    service_categories = context_vars["service_categories"].split(",")

    for category in service_categories:
        retriever = get_retriever(
            collection_name=collection_name,
            persist_directory=persist_directory,
            service_category=category,
        )
        category_docs = retriever.invoke(query)

        if category_docs:
            for doc in category_docs:
                if doc.id not in doc_ids:
                    doc_ids.add(doc.id)
                    docs.append(doc)

    output = ""

    for doc in docs:
        if doc.metadata.get("source"):
            source = doc.metadata["source"]
        else:
            source = "Source Unknown"

        if doc.metadata.get("service_category"):
            service_category = doc.metadata["service_category"]
        else:
            service_category = "Service Category Unknown"

        output += (
            f"source:{source}-service_category:{service_category}: {doc.page_content}\n"
        )

    return {"output": output}
