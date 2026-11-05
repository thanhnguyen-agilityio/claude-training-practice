import re
import sqlite3
from contextlib import closing

from langchain_core.tools import tool
from utils.utils import get_path

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?\d{9,15}$")
PHONE_SEPARATORS = re.compile(r"[\s\-.()]")


@tool
def create_support_ticket(
    email: str, subject: str, name: str = "User", phone: str = "", description: str = ""
) -> str:
    """
    Use this tool to help use create a customer support ticket.
    The email is validated. The phone is optional; if given it must be 9 to 15
    digits with an optional leading +. If the result says the ticket was not
    created, tell the user the reason and ask for the corrected value.
    """
    if not EMAIL_RE.match(email.strip()):
        return (
            f"Support ticket NOT created: invalid email '{email}'. "
            "Tell the user the reason and ask them for a valid email address."
        )
    if phone.strip() and not PHONE_RE.match(PHONE_SEPARATORS.sub("", phone)):
        return (
            f"Support ticket NOT created: invalid phone '{phone}'. "
            "A phone number must be 9 to 15 digits, optionally starting with +. "
            "Tell the user the reason and ask them for a valid phone number."
        )
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
