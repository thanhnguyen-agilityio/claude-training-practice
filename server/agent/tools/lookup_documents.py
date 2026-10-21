from agent.rag.retriever import get_retriever
from langchain_core.documents import Document
from langchain_core.tools import tool
from pydantic import BaseModel, Field, ValidationError, field_validator


class DocumentRequest(BaseModel):
    query: str

    service_categories: list[str] = Field(
        max_length=2,
        min_length=1,
    )

    @field_validator('service_categories')
    @classmethod
    def validate_service_categories(cls, value):
        if not value:
            raise ValidationError('service_categories cannot be empty')

        if set(value) - {"faqs", "policies"}:
            raise ValidationError('service_categories must be either "faqs" or "policies"')

        return value


@tool
def lookup_documents(document_request: DocumentRequest) -> list[Document]:
    """
    Retrieve shop documents for queries about store services like policies, FAQs, or categories. Use for intent `service`.

    Categories:
    - faqs: General queries like "How to cancel an order."
    - policies: Detailed policy inquiries like "What is your refund policy?"

    Example:
    - Query: "What are your policies?" → Category: [policies]

    Use only when `intent = service`.
    """
    query = document_request.query
    service_categories = document_request.service_categories
    docs = []
    doc_ids = set()

    for category in service_categories:
        retriever = get_retriever(service_category=category)
        category_docs = retriever.invoke(query)

        if category_docs:
            for doc in category_docs:
                if doc.id not in doc_ids:
                    doc_ids.add(doc.id)
                    docs.append(doc)

    return docs
