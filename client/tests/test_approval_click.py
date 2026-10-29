from streamlit.testing.v1 import AppTest


class FakeService:
    """Server stand-in: the reply only appears in history after approve/reject ran."""

    calls = []
    replied = False
    fail = False

    def __init__(self, **_):
        pass

    def chat_history(self):
        if FakeService.replied:
            return [{"type": "ai", "content": "Ticket created!"}]
        return []

    def approve_tool_call(self, tool_call_id):
        if FakeService.fail:
            raise Exception("server down")
        FakeService.calls.append(("approve", tool_call_id))
        FakeService.replied = True

    def reject_tool_call(self, tool_call_id):
        FakeService.calls.append(("reject", tool_call_id))
        FakeService.replied = True


def run_after_click(monkeypatch, decision, fail=False):
    from services import chat_service

    FakeService.calls, FakeService.replied, FakeService.fail = [], False, fail
    monkeypatch.setattr(chat_service, "ChatService", FakeService)
    at = AppTest.from_file("pages/agent.py")
    at.session_state["user_id"] = "u"
    at.session_state["thread_id"] = "t"
    at.session_state["tool_call_id"] = "call_1"
    at.session_state["pending_decision"] = decision
    return at.run(timeout=20)


def reply_count(at):
    return sum("Ticket created!" in m.value for m in at.markdown)


def test_approve_click_calls_server_and_shows_reply_once(monkeypatch):
    at = run_after_click(monkeypatch, "approve")

    assert not at.exception
    assert FakeService.calls == [("approve", "call_1")]
    assert reply_count(at) == 1


def test_reject_click_calls_server_and_shows_reply_once(monkeypatch):
    at = run_after_click(monkeypatch, "reject")

    assert not at.exception
    assert FakeService.calls == [("reject", "call_1")]
    assert reply_count(at) == 1


def test_server_error_is_shown_and_chat_input_stays(monkeypatch):
    at = run_after_click(monkeypatch, "approve", fail=True)

    assert not at.exception
    assert [e.value for e in at.error] == ["server down"]
    assert len(at.chat_input) == 1
