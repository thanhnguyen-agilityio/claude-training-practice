from pathlib import Path
from unittest.mock import patch

from services.chat_service import ChatService
from streamlit.runtime.scriptrunner_utils.exceptions import StopException
from streamlit.testing.v1 import AppTest

AGENT_PAGE = str(Path(__file__).parents[1] / "pages" / "agent.py")


def make_app(history, stream=None, state=None, prompt=None):
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    for key, value in (state or {}).items():
        at.session_state[key] = value
    with (
        patch.object(ChatService, "chat_history", return_value=history),
        patch.object(ChatService, "chat_stream", stream),
    ):
        at.run()
        if prompt:
            at.chat_input[0].set_value(prompt).run()
    return at


def texts(at):
    return [m.markdown[0].value for m in at.chat_message if m.markdown]


async def heartbeat_stream(self, message):
    yield {"heartbeat": True}
    yield "Hi"
    yield {"heartbeat": True}


async def interrupted_stream(self, message):
    yield "Part"
    raise StopException()


def test_heartbeat_adds_no_text():
    at = make_app([], heartbeat_stream, prompt="hello")

    assert not at.exception
    assert texts(at)[-1] == "Hi"


def test_stopped_reply_shown_when_server_copy_not_saved_yet():
    history = [{"type": "human", "content": "hello"}]
    at = make_app(history, state={"stopped_reply": "Part"})

    assert texts(at)[-1] == "Part\n\n_(stopped)_"


def test_stopped_reply_hidden_once_server_saved_it():
    history = [
        {"type": "human", "content": "hello"},
        {"type": "ai", "content": "Part\n\n_(stopped)_"},
    ]
    at = make_app(history, state={"stopped_reply": "Part"})

    assert texts(at).count("Part\n\n_(stopped)_") == 1


def test_interrupted_stream_keeps_partial_reply_for_stop():
    at = make_app([], interrupted_stream, prompt="hello")

    assert at.session_state["partial_reply"] == "Part"


def test_finished_stream_clears_partial_reply():
    at = make_app([], heartbeat_stream, prompt="hello")

    assert "partial_reply" not in at.session_state
