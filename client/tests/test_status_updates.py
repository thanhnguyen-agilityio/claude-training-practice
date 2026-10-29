from pathlib import Path
from unittest.mock import patch

from services.chat_service import ChatService
from streamlit.testing.v1 import AppTest

AGENT_PAGE = str(Path(__file__).parents[1] / "pages" / "agent.py")


async def fake_stream(self, message):
    yield {"status": "Searching the product database..."}
    yield "Found it"


def run(stream):
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    with (
        patch.object(ChatService, "chat_history", return_value=[]),
        patch.object(ChatService, "chat_stream", stream),
    ):
        at.run()
        at.chat_input[0].set_value("compare").run()
    return at


def test_status_hidden_once_answer_streams():
    at = run(fake_stream)

    assert not at.exception
    assert at.chat_message[-1].markdown[0].value == "Found it"


def test_status_shown_while_waiting():
    # A stream that dies after the status leaves the status on screen (AppTest only sees the final state).
    async def status_then_fail(self, message):
        yield {"status": "Searching the product database..."}
        raise RuntimeError("boom")

    at = run(status_then_fail)

    assert any(c.value == "Searching the product database..." for c in at.caption)


def test_empty_chunk_keeps_status():
    # Tool-call chunks stream an empty string right after the status.
    async def status_empty_fail(self, message):
        yield {"status": "Searching the product database..."}
        yield ""
        raise RuntimeError("boom")

    at = run(status_empty_fail)

    assert any(c.value == "Searching the product database..." for c in at.caption)
