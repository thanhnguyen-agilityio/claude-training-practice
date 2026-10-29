from pathlib import Path
from unittest.mock import patch

from services.chat_service import ChatService
from streamlit.testing.v1 import AppTest
from utils.constants import QUICK_START

AGENT_PAGE = str(Path(__file__).parents[1] / "pages" / "agent.py")
FIRST = QUICK_START["💁‍♀️ Services"][0]


async def fake_stream(self, message):
    yield {"require_approval": False, "content": "reply"}


def run_agent(history):
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    with patch.object(ChatService, "chat_history", return_value=history):
        return at.run()


def test_quick_start_buttons_shown_on_new_conversation():
    at = run_agent([])

    assert [b.label for b in at.button] == [e for v in QUICK_START.values() for e in v]
    assert not at.expander


def test_quick_start_hidden_when_history_exists():
    at = run_agent([{"type": "human", "content": "hi"}])

    assert len(at.button) == 0


def test_click_sends_example_as_query():
    at = run_agent([])
    sent = []

    def stream(self, message):
        sent.append(message)
        return fake_stream(self, message)

    buttons = at.button
    with patch.object(ChatService, "chat_history", return_value=[]):
        with patch.object(ChatService, "chat_stream", stream):
            buttons[0].click().run()

    assert sent == [FIRST]
    assert [m.markdown[0].value for m in at.chat_message][-2:] == [FIRST, "reply"]
    assert len(at.button) == 0
