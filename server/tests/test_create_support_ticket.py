import sqlite3
import sys

import pytest

from agent.tools import create_support_ticket


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = str(tmp_path / "ecommerce_store.db")
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE SupportTicket (id INTEGER PRIMARY KEY, name TEXT, email TEXT,"
            " subject TEXT, phone TEXT, description TEXT, resolved BOOLEAN)"
        )
    # `agent.tools.create_support_ticket` is the tool, so patch the module via sys.modules
    monkeypatch.setattr(
        sys.modules["agent.tools.create_support_ticket"], "get_path", lambda *_: path
    )
    return path


def _rows(path):
    with sqlite3.connect(path) as conn:
        return conn.execute(
            "SELECT name, email, subject, phone, description FROM SupportTicket"
        ).fetchall()


def test_apostrophes_stored_verbatim(db_path):
    args = {
        "name": "O'Brien",
        "email": "o'brien@x.com",
        "subject": "can't login",
        "phone": "'555'",
        "description": "it's 'broken'",
    }
    create_support_ticket.invoke(args)

    assert _rows(db_path) == [
        tuple(args[k] for k in ("name", "email", "subject", "phone", "description"))
    ]


def test_injection_payload_does_not_alter_tables(db_path):
    payload = "x'); DROP TABLE SupportTicket;--"
    create_support_ticket.invoke({"email": "a@b.com", "subject": payload})

    assert _rows(db_path) == [("User", "a@b.com", payload, "", "")]
