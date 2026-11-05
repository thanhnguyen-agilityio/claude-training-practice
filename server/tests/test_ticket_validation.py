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
    monkeypatch.setattr(
        sys.modules["agent.tools.create_support_ticket"], "get_path", lambda *_: path
    )
    return path


def _rows(path):
    with sqlite3.connect(path) as conn:
        return conn.execute("SELECT email, phone FROM SupportTicket").fetchall()


@pytest.mark.xfail(strict=True, reason="issue #55: no contact validation")
def test_invalid_email_rejected_no_row(db_path):
    for email in ["lan@@gmail", "lan@gmail", "lan gmail.com", "@gmail.com"]:
        result = create_support_ticket.invoke({"email": email, "subject": "torn dress"})
        assert "not created" in result.lower(), email
        assert "email" in result.lower(), email
    assert _rows(db_path) == []


@pytest.mark.xfail(strict=True, reason="issue #55: no contact validation")
def test_invalid_phone_rejected_no_row(db_path):
    for phone in ["12ab", "12345678", "1234567890123456", "++84912345678"]:
        result = create_support_ticket.invoke(
            {"email": "lan@gmail.com", "subject": "torn dress", "phone": phone}
        )
        assert "not created" in result.lower(), phone
        assert "phone" in result.lower(), phone
    assert _rows(db_path) == []


def test_valid_contact_saved_unchanged(db_path):
    cases = [
        ("lan@gmail.com", "+84912345678"),
        ("lan.nguyen@shop.co.vn", "0912 345 678"),
        ("lan@gmail.com", "0912-345-678"),
        ("lan@gmail.com", ""),
    ]
    for email, phone in cases:
        result = create_support_ticket.invoke(
            {"email": email, "subject": "torn dress", "phone": phone}
        )
        assert result == "Support ticket created successfully!"
    assert _rows(db_path) == cases
