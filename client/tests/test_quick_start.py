from pathlib import Path
from unittest.mock import patch

from services.chat_service import ChatService
from streamlit.testing.v1 import AppTest

AGENT_PAGE = str(Path(__file__).parents[1] / "pages" / "agent.py")
SHIPPING = "Do you offer free shipping?"
HISTORY = [{"type": "human", "content": "hi"}]


async def fake_stream(self, message):
    yield {"require_approval": False, "content": "reply"}


def run_agent(history):
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    with patch.object(ChatService, "chat_history", return_value=history):
        return at.run()


def labels(at):
    return [b.label for b in at.button]


def test_quick_start_buttons_shown_on_new_conversation():
    at = run_agent([])

    assert SHIPPING in labels(at), "no quick-start button"
    assert len(at.button) == 6
    assert len(at.expander) == 0


def test_quick_start_hidden_once_history_exists():
    at = run_agent([])
    assert SHIPPING in labels(at), "no quick-start button on empty history"

    at = run_agent(HISTORY)

    assert SHIPPING not in labels(at)


def test_click_sends_example_as_query():
    at = run_agent([])
    btn = [b for b in at.button if b.label == SHIPPING]
    assert btn, "no quick-start button"
    sent = []

    def stream(self, message):
        sent.append(message)
        return fake_stream(self, message)

    with patch.object(ChatService, "chat_history", return_value=[]):
        with patch.object(ChatService, "chat_stream", stream):
            btn[0].click().run()

    assert sent == [SHIPPING]
    assert [m.markdown[0].value for m in at.chat_message][-2:] == [SHIPPING, "reply"]
    assert SHIPPING not in labels(at)
