from pathlib import Path
from unittest.mock import patch

from services.chat_service import ChatService
from streamlit.delta_generator import DeltaGenerator
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


def captions_shown(stream):
    shown = []
    real = DeltaGenerator.caption

    def spy(self, body, *a, **k):
        shown.append(body)
        return real(self, body, *a, **k)

    with patch.object(DeltaGenerator, "caption", spy):
        at = run(stream)
    return at, shown


def test_status_hidden_once_answer_streams():
    at, shown = captions_shown(fake_stream)

    assert not at.exception
    assert shown == ["Searching the product database..."]
    assert not at.caption
    assert at.chat_message[-1].markdown[0].value == "Found it"


def test_empty_chunk_keeps_status_and_error_clears_it():
    # Tool-call chunks stream an empty string right after the status.
    async def status_empty_fail(self, message):
        yield {"status": "Searching the product database..."}
        yield ""
        raise RuntimeError("boom")

    at, shown = captions_shown(status_empty_fail)

    assert shown == ["Searching the product database..."]
    assert not at.caption
    assert at.error
