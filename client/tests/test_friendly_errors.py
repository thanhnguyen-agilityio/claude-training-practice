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
    text = "internal boom detail"


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


def test_chat_stream_failure_shows_friendly_message(monkeypatch, caplog):
    async def broken_stream(self, prompt):
        raise RuntimeError("All connection attempts failed")
        yield  # makes this an async generator, like the real chat_stream

    monkeypatch.setattr(ChatService, "chat_history", lambda self: [])
    monkeypatch.setattr(ChatService, "chat_stream", broken_stream)
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    at.run()
    at.chat_input[0].set_value("hello").run()

    assert [e.value for e in at.error] == [ERROR_GENERIC]
    assert "All connection attempts failed" in caplog.text


def test_health_check_failure_is_friendly(monkeypatch):
    errors = []
    monkeypatch.setattr(requests, "get", fail_connect)
    monkeypatch.setattr("streamlit.error", errors.append)
    monkeypatch.setattr("streamlit.stop", lambda: None)
    health_check()
    assert errors == [ERROR_CONNECTION]


def test_invoke_and_reject_non_200_are_friendly_and_logged(monkeypatch, caplog):
    monkeypatch.setattr(requests, "post", lambda *a, **k: Resp500())
    s = ChatService()
    for fn in (lambda: s.chat_invoke("hi"), lambda: s.reject_tool_call("1")):
        with pytest.raises(Exception) as e:
            fn()
        assert str(e.value) == ERROR_REQUEST
    assert "HTTP 500 on /chat/invoke: internal boom detail" in caplog.text


def test_history_load_failure_is_logged_and_page_still_renders(monkeypatch, caplog):
    def boom(self):
        raise Exception("history down")

    monkeypatch.setattr(ChatService, "chat_history", boom)
    at = AppTest.from_file(AGENT_PAGE, default_timeout=30)
    at.session_state["user_id"] = "u1"
    at.session_state["thread_id"] = "t1"
    at.run()
    assert not at.exception and not at.error
    assert "history down" in caplog.text


def test_connection_cause_is_logged(monkeypatch, caplog):
    monkeypatch.setattr(requests, "post", fail_connect)
    with pytest.raises(Exception):
        ChatService().chat_invoke("hi")
    assert "boom" in caplog.text
