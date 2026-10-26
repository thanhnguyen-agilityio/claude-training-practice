from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from utils.utils import handle_keep_recent_messages


def _call(*ids):
    return AIMessage("", tool_calls=[{"id": i, "name": "search", "args": {}} for i in ids])


def _assert_no_orphan(kept):
    ids = {tc["id"] for m in kept if isinstance(m, AIMessage) for tc in m.tool_calls}
    for m in kept:
        if isinstance(m, ToolMessage):
            assert m.tool_call_id in ids, "orphan ToolMessage: its AIMessage was cut"


def test_recent_window_never_starts_with_orphan_tool_message():
    # Cut lands between the AIMessage(tool_call) and its ToolMessage.
    messages = [
        HumanMessage("q1"),
        _call("c1"),
        ToolMessage("result", tool_call_id="c1"),
        AIMessage("answer"),
    ]
    kept = handle_keep_recent_messages(messages, recent_messages_number=2)

    _assert_no_orphan(kept)
    assert kept == messages[1:]  # AIMessage kept, order preserved


def test_several_tool_messages_in_a_row():
    messages = [
        HumanMessage("q1"),
        _call("c1", "c2", "c3"),
        ToolMessage("r1", tool_call_id="c1"),
        ToolMessage("r2", tool_call_id="c2"),
        ToolMessage("r3", tool_call_id="c3"),
        AIMessage("answer"),
    ]
    kept = handle_keep_recent_messages(messages, recent_messages_number=3)

    _assert_no_orphan(kept)
    assert kept == messages[1:]


def test_clean_cut_does_not_widen():
    messages = [HumanMessage("q1"), AIMessage("a1"), HumanMessage("q2"), AIMessage("a2")]
    assert handle_keep_recent_messages(messages, recent_messages_number=2) == messages[2:]


def test_n_bigger_than_list_keeps_all():
    messages = [HumanMessage("q1"), AIMessage("a1")]
    assert handle_keep_recent_messages(messages, recent_messages_number=10) == messages
