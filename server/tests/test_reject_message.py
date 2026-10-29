import asyncio

from langchain_core.messages import ToolMessage
from routers import chat
from schema.schema import ToolCallApprovalRequest


def test_reject_tells_model_action_was_not_performed(monkeypatch):
    sent = []

    class FakeGraph:
        def invoke(self, payload, config):
            sent.append(payload)

    monkeypatch.setattr(chat, "init_graph", lambda config: FakeGraph())
    request = ToolCallApprovalRequest(
        user_id="u1",
        thread_id="t1",
        tool_call_id="call_1",
        message="Rejected",
        user_input="The tool call is rejected.",
    )

    asyncio.run(chat.reject_action(request))

    (msg,) = sent[0]["messages"]
    assert isinstance(msg, ToolMessage)
    assert msg.tool_call_id == "call_1"
    assert "NOT performed" in msg.content
    assert "because the user chose not to" in msg.content
    assert "ask what they would like to do next" in msg.content
