from pathlib import Path
from unittest.mock import patch

from services.chat_service import ChatService
from streamlit.testing.v1 import AppTest
from utils.constants import WELCOME_MESSAGE

AGENT_PAGE = str(Path(__file__).parents[1] / "pages" / "agent.py")
HISTORY = [
    {"type": "human", "content": "Give me categories"},
    {"type": "ai", "content": "Here are the categories"},
]


def run_agent(history):
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    with patch.object(ChatService, "chat_history", return_value=history):
        return at.run()


def chat_texts(at):
    return [m.markdown[0].value for m in at.chat_message]


def test_welcome_shown_for_new_conversation():
    at = run_agent([])

    assert chat_texts(at)[0] in WELCOME_MESSAGE


def test_welcome_stays_at_top_when_history_exists():
    at = run_agent(HISTORY)

    texts = chat_texts(at)
    assert texts[0] in WELCOME_MESSAGE
    assert texts[1:] == [m["content"] for m in HISTORY]


def test_welcome_unchanged_across_reruns():
    at = run_agent([])
    first = chat_texts(at)[0]
    with patch.object(ChatService, "chat_history", return_value=HISTORY):
        at.run()

    assert chat_texts(at)[0] == first
