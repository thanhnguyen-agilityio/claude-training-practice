from utils.utils import build_require_approval_message


def test_support_ticket_message_explains_why_and_both_outcomes():
    msg = build_require_approval_message(
        {"name": "create_support_ticket", "args": {"email": "a@b.com", "subject": "Late order"}}
    )
    assert "support team" in msg
    assert "**Yes**" in msg and "**No**" in msg
    assert "no ticket is created" in msg
    assert "Late order" in msg


def test_google_shopping_message_explains_why_cost_and_both_outcomes():
    msg = build_require_approval_message(
        {"name": "search_google_shopping", "args": {"query": "blue shirt"}}
    )
    assert "couldn't find this product in our store" in msg
    assert "costs you nothing" in msg
    assert "**Yes**" in msg and "**No**" in msg
    assert "blue shirt" in msg
