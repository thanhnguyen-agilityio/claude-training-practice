import sqlite3
from contextlib import closing

from langchain_core.tools import tool
from utils.utils import get_path


@tool
def create_support_ticket(
    email: str, subject: str, name: str = "User", phone: str = "", description: str = ""
) -> str:
    """
    Use this tool to help use create a customer support ticket
    """
    db_path = get_path("ecommerce_store.db", "db")

    with closing(sqlite3.connect(db_path)) as conn, conn:  # conn: commit on exit
        conn.execute(
            """
            INSERT INTO SupportTicket (name, email, subject, phone, description, resolved)
            VALUES (?, ?, ?, ?, ?, false)
            """,
            (name, email, subject, phone, description),
        )
    return "Support ticket created successfully!"
