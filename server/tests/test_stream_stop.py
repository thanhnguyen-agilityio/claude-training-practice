import asyncio
import json
import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from routers import chat
from schema.schema import ChatRequest

TEXT = (AIMessageChunk(content="Part"), {"langgraph_node": "assistant"})


class SyncThread:
    """Runs the target on start so cleanup is deterministic."""

    def __init__(self, target, daemon=None):
        self.target = target

    def start(self):
        self.target()


def make_graph(events, next_=()):
    graph = MagicMock()
    graph.stream.return_value = events
    graph.get_state.return_value.next = next_
    return graph


def stream(graph):
    req = ChatRequest(message="hi", thread_id="t", user_id="u")
    return chat.stream_agent_response(req)


def test_heartbeat_sent_while_step_is_slow():
    def slow():
        time.sleep(0.1)
        yield TEXT

    async def run():
        return [json.loads(b) async for b in stream(None)]

    with (
        patch.object(chat, "init_graph", return_value=make_graph(slow())),
        patch.object(chat, "HEARTBEAT_SECONDS", 0.01),
    ):
        out = asyncio.run(run())

    assert {"heartbeat": True} in out
    assert out.index({"heartbeat": True}) < out.index("Part")


def test_stop_saves_partial_and_cancels_pending_tool_call():
    closed = []

    def events():
        try:
            yield TEXT
            yield TEXT
        finally:
            closed.append(True)

    graph = make_graph(events(), next_=("safe_tools",))
    call_msg = AIMessage(content="", tool_calls=[{"name": "x", "args": {}, "id": "1"}])
    graph.get_state.return_value.values = {"messages": [call_msg]}

    async def run():
        gen = stream(graph)
        await gen.__anext__()
        await gen.aclose()

    with (
        patch.object(chat, "init_graph", return_value=graph),
        patch.object(chat, "threading", SimpleNamespace(Thread=SyncThread)),
    ):
        asyncio.run(run())

    assert closed
    (config, update), kwargs = graph.update_state.call_args
    assert [type(m) for m in update["messages"]] == [ToolMessage, AIMessage]
    assert update["messages"][0].tool_call_id == "1"
    assert update["messages"][1].content == chat.stopped_text("Part")
    assert kwargs == {"as_node": "assistant"}


def test_finish_stopped_noop_when_run_already_finished():
    graph = make_graph(x for x in [])
    chat.finish_stopped(graph, {}, graph.stream.return_value, "x")

    graph.update_state.assert_not_called()


def test_full_stream_does_not_update_state():
    async def run():
        return [b async for b in stream(None)]

    graph = make_graph(iter([TEXT]))
    with patch.object(chat, "init_graph", return_value=graph):
        asyncio.run(run())

    graph.update_state.assert_not_called()
