from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.tools import tool
from langgraph.types import interrupt
from utils.utils import get_path


@tool
def create_support_ticket(
    email: str,
    subject: str,
    name: str = "User",
    phone: str = "",
    description: str = ""
) -> str:
    """
    Use this tool to help use create a customer support ticket
    """
    db_path = get_path("ecommerce_store.db", "db")
    db = SQLDatabase.from_uri(
        f"sqlite:///{db_path}",
        # No sample to avoid issue on sample url image not correct
        sample_rows_in_table_info=0,
    )

    db.run(
        f"""
        INSERT INTO SupportTicket (name, email, subject, phone, description, resolved)
        VALUES ('{name}', '{email}', '{subject}', '{phone}', '{description}', false);
        """
    )
    return "Support ticket created successfully!"
