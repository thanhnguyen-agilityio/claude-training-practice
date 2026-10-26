from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from utils.utils import handle_keep_recent_messages


def test_recent_window_never_starts_with_orphan_tool_message():
    # Cut lands between the AIMessage(tool_call) and its ToolMessage.
    messages = [
        HumanMessage("q1"),
        AIMessage("", tool_calls=[{"id": "c1", "name": "search", "args": {}}]),
        ToolMessage("result", tool_call_id="c1"),
        AIMessage("answer"),
    ]
    kept = handle_keep_recent_messages(messages, recent_messages_number=2)

    ids = {tc["id"] for m in kept if isinstance(m, AIMessage) for tc in m.tool_calls}
    for m in kept:
        if isinstance(m, ToolMessage):
            assert m.tool_call_id in ids, "orphan ToolMessage: its AIMessage was cut"
