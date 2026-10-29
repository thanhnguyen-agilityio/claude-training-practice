import asyncio
import json
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessageChunk, ToolMessage
from routers import chat
from schema.schema import ChatRequest


def collect(chunks, raw=False):
    graph = MagicMock()
    graph.stream.return_value = iter(chunks)
    graph.get_state.return_value.next = ()

    async def run():
        req = ChatRequest(message="hi", thread_id="t", user_id="u")
        return [b async for b in chat.stream_agent_response(req)]

    with patch.object(chat, "init_graph", return_value=graph):
        out = asyncio.run(run())
    return out if raw else [json.loads(b) for b in out]


def call(name):
    return (
        AIMessageChunk(
            content="",
            tool_call_chunks=[{"name": name, "args": "", "id": "1", "index": 0}],
        ),
        {"langgraph_node": "assistant"},
    )


def result(name="lookup_documents"):
    msg = ToolMessage(content="docs", tool_call_id="1", name=name)
    return msg, {"langgraph_node": "safe_tools"}


def statuses(out):
    return [o for o in out if isinstance(o, dict)]


def test_tool_call_emits_status_event():
    out = collect([call("lookup_documents")])

    assert {"status": "Looking up our policies and support documents..."} in out


def test_tool_result_emits_done_status():
    out = collect([call("lookup_documents"), result()])

    assert out[-1] == {"status": chat.TOOL_DONE_STATUS}


def test_repeated_status_is_not_resent():
    out = collect([call("sql_db_list_tables"), call("sql_db_schema")])

    assert statuses(out) == [{"status": "Searching the product database..."}]


def test_ticket_status_does_not_claim_creation():
    out = collect([call("create_support_ticket")])

    assert {"status": "Preparing your support ticket..."} in out


def test_unknown_tool_has_no_status():
    assert not statuses(collect([call("save_memory")]))


def test_each_event_is_one_newline_terminated_line():
    text = (AIMessageChunk(content="a\nb"), {"langgraph_node": "assistant"})
    raw = collect([call("lookup_documents"), text], raw=True)

    assert all(b.endswith(b"\n") and b.count(b"\n") == 1 for b in raw)
    assert json.loads(raw[-1]) == "a\nb"

