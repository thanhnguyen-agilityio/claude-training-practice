from pathlib import Path

import pytest
import requests
from services.chat_service import ChatService
from streamlit.testing.v1 import AppTest
from utils.apis import health_check
from utils.constants import ERROR_CONNECTION, ERROR_GENERIC, ERROR_REQUEST

AGENT_PAGE = str(Path(__file__).parents[1] / "pages" / "agent.py")
TECHNICAL = ("api", "server logs", "invoke", "response not success")


def fail_connect(*a, **k):
    raise requests.ConnectionError("boom")


class Resp500:
    status_code = 500


@pytest.mark.parametrize("method", ["get", "post"])
def test_connection_error_is_friendly(monkeypatch, method):
    monkeypatch.setattr(requests, method, fail_connect)
    s = ChatService()
    fn = s.chat_history if method == "get" else s.chat_invoke
    with pytest.raises(Exception) as e:
        fn() if method == "get" else fn("hi")
    assert str(e.value) == ERROR_CONNECTION


@pytest.mark.parametrize("method", ["get", "post"])
def test_bad_status_is_friendly(monkeypatch, method):
    monkeypatch.setattr(requests, method, lambda *a, **k: Resp500())
    s = ChatService()
    with pytest.raises(Exception) as e:
        s.chat_history() if method == "get" else s.approve_tool_call("1")
    assert str(e.value) == ERROR_REQUEST


def test_messages_have_no_technical_terms():
    for m in (ERROR_GENERIC, ERROR_CONNECTION, ERROR_REQUEST):
        assert not any(t in m.lower() for t in TECHNICAL)


def test_chat_stream_failure_shows_friendly_message(monkeypatch):
    def broken_stream(self, prompt):
        raise RuntimeError("All connection attempts failed")

    monkeypatch.setattr(ChatService, "chat_history", lambda self: [])
    monkeypatch.setattr(ChatService, "chat_stream", broken_stream)
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    at.run()
    at.chat_input[0].set_value("hello").run()

    assert [e.value for e in at.error] == [ERROR_GENERIC]


def test_health_check_failure_is_friendly(monkeypatch):
    errors = []
    monkeypatch.setattr(requests, "get", fail_connect)
    monkeypatch.setattr("streamlit.error", errors.append)
    monkeypatch.setattr("streamlit.stop", lambda: None)
    health_check()
    assert errors == [ERROR_CONNECTION]
