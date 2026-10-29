import asyncio
import json
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessageChunk
from routers import chat
from schema.schema import ChatRequest


def collect(chunks):
    graph = MagicMock()
    graph.stream.return_value = iter(chunks)
    graph.get_state.return_value.next = ()

    async def run():
        req = ChatRequest(message="hi", thread_id="t", user_id="u")
        return [json.loads(b) async for b in chat.stream_agent_response(req)]

    with patch.object(chat, "init_graph", return_value=graph):
        return asyncio.run(run())


def test_tool_call_emits_status_event():
    call = AIMessageChunk(
        content="",
        tool_call_chunks=[
            {"name": "lookup_documents", "args": "", "id": "1", "index": 0}
        ],
    )
    out = collect([(call, {"langgraph_node": "assistant"})])

    assert {"status": "Looking up our policies and support documents..."} in out


def test_plain_text_has_no_status():
    out = collect([(AIMessageChunk(content="hello"), {"langgraph_node": "assistant"})])

    assert out == ["hello"]
