import asyncio

from langchain_core.messages import AIMessage

from routers import chat
from schema.schema import ToolCallApprovalRequest


class FakeGraph:
    def invoke(self, *_):
        return {"messages": [AIMessage(content="Ticket created!")]}


def _call(fn, monkeypatch):
    monkeypatch.setattr(chat, "init_graph", lambda config: FakeGraph())
    req = ToolCallApprovalRequest(
        user_id="u", thread_id="t", tool_call_id="c", user_input="x"
    )
    return asyncio.run(fn(req))


def test_approve_returns_assistant_reply(monkeypatch):
    assert _call(chat.approve_action, monkeypatch) == "Ticket created!"


def test_reject_returns_assistant_reply(monkeypatch):
    assert _call(chat.reject_action, monkeypatch) == "Ticket created!"
