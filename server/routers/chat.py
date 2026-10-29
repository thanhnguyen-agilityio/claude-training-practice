import asyncio
import json
import threading
from typing import AsyncGenerator

from agent.graph import init_graph
from agent.tools import sensitive_tool_names
from fastapi import APIRouter
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import AIMessage, ToolMessage
from schema.schema import ChatRequest, ToolCallApprovalRequest
from utils.utils import build_require_approval_message

router = APIRouter(prefix="/chat", tags=[""])

# Progress text shown to the user while a tool runs
TOOL_STATUS = {
    "lookup_documents": "Looking up our policies and support documents...",
    "check_and_execute_query_tool": "Searching the product database...",
    "sql_db_list_tables": "Searching the product database...",
    "sql_db_schema": "Searching the product database...",
    "search_google_shopping": "Searching for similar items...",
    "create_support_ticket": "Preparing your support ticket...",
}
TOOL_DONE_STATUS = "✓ Got the results, preparing your answer..."
HEARTBEAT_SECONDS = 5
STOPPED_NOTE = "_(stopped)_"
# thread id -> (stop, done) events of the run streaming on it; removed when the run ends
_runs: dict[str, tuple[threading.Event, threading.Event]] = {}


def ndjson(obj) -> bytes:
    """One JSON value per line: the client splits the stream on newlines."""
    return (json.dumps(obj) + "\n").encode("utf-8")


def stopped_text(partial: str) -> str:
    return f"{partial}\n\n{STOPPED_NOTE}" if partial else STOPPED_NOTE


def finish_stopped(graph, config, events, partial):
    """Close a stopped run and save its state so the thread accepts the next message."""
    events.close()
    # Not snapshot.next: a closed stream leaves it empty even mid-run.
    messages = graph.get_state(config).values.get("messages", [])
    last = messages[-1] if messages else None
    if not last or (isinstance(last, AIMessage) and not last.tool_calls):
        return  # nothing saved yet, or the reply was already complete
    answered = {m.tool_call_id for m in messages if isinstance(m, ToolMessage)}
    cancelled = [
        ToolMessage(
            tool_call_id=call["id"],
            content="Cancelled: the user stopped the response.",
        )
        for call in getattr(last, "tool_calls", None) or []
        if call["id"] not in answered
    ]
    graph.update_state(
        config,
        {"messages": [*cancelled, AIMessage(content=stopped_text(partial))]},
        as_node="assistant",
    )


@router.post("/invoke")
async def chat_invoke(request: ChatRequest):
    """Invoke chat"""
    config = {
        "configurable": {
            "thread_id": request.thread_id,
            "user_id": request.user_id,
        }
    }
    messages = [("user", request.message)]
    graph = init_graph(config=config)
    response = graph.invoke({"messages": messages}, config)["messages"][-1].content
    return Response(
        response,
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


########## old code ##########
# add_routes(
#     app,
#     agent_chain,
#     path="/chat",
#     input_type=ChatRequest,
#     output_type="auto",
#     config_keys=("configurable",),
#     enabled_endpoints=("invoke"),
# )
########## old code ##########

# ---------------------- CHAT INVOKE ----------------------


# ---------------------- CHAT STREAMING ----------------------
async def stream_agent_response(request: ChatRequest) -> AsyncGenerator[bytes, None]:
    config = {
        "configurable": {
            "thread_id": request.thread_id,
            "user_id": request.user_id,
        }
    }
    messages = [("user", request.message)]
    graph = init_graph(config=config)

    # Stream messages of assistant node, plus progress status around tool calls
    last_status = None
    # graph.stream is sync: pull each item in a thread so the event loop can flush
    # events (e.g. status) to the client while a tool or the LLM is still running.
    events = graph.stream({"messages": messages}, config, stream_mode="messages")
    lock = threading.Lock()

    def step():
        # Locked so cleanup can't close the graph while a step is running.
        with lock:
            return next(events, None)

    # A new message stops the run still streaming on this thread (after Stop its client
    # may not have disconnected yet) and waits until that run's cleanup is saved.
    stop, done = threading.Event(), threading.Event()
    prior = _runs.get(request.thread_id)
    _runs[request.thread_id] = (stop, done)
    if prior:
        prior[0].set()
        await asyncio.to_thread(prior[1].wait)

    partial = ""
    finished = False
    try:
        while not stop.is_set():
            pending = asyncio.ensure_future(asyncio.to_thread(step))
            # Heartbeat keeps the client's read timeout alive and lets it act on Stop
            # while a step is slow.
            while (
                not stop.is_set()
                and not (await asyncio.wait({pending}, timeout=HEARTBEAT_SECONDS))[0]
            ):
                yield ndjson({"heartbeat": True})
            if stop.is_set():
                break
            event = pending.result()
            if event is None:
                finished = True
                break
            msg, metadata = event
            status = None
            if metadata["langgraph_node"] == "assistant":
                for chunk in getattr(msg, "tool_call_chunks", None) or []:
                    status = TOOL_STATUS.get(chunk.get("name")) or status
                if isinstance(msg.content, str):
                    partial += msg.content
            elif isinstance(msg, ToolMessage):
                status = TOOL_DONE_STATUS
                partial = ""
            if status and status != last_status:
                last_status = status
                yield ndjson({"status": status})
            if metadata["langgraph_node"] == "assistant":
                yield ndjson(msg.content)
    finally:
        # Only once cleanup is saved, so a newer message on this thread waits for it.
        def release():
            done.set()
            if _runs.get(request.thread_id) == (stop, done):
                del _runs[request.thread_id]

        if finished:
            release()
        else:
            # Stopped (client disconnected or a newer message): the in-flight step
            # finishes, then the graph closes and the partial answer is saved.
            # Off-thread so the event loop is free.
            def cleanup():
                try:
                    with lock:
                        finish_stopped(graph, config, events, partial)
                finally:
                    release()

            threading.Thread(target=cleanup, daemon=True).start()
    if not finished:
        return

    # interrupt
    snapshot = graph.get_state(config)
    if snapshot.next and snapshot.next[0] == "sensitive_tools":
        for tool_call in snapshot.values["messages"][-1].tool_calls:
            if tool_call["name"] in sensitive_tool_names:
                yield ndjson(
                    {
                        "require_approval": True,
                        "message": build_require_approval_message(tool_call),
                        "thread_id": request.thread_id,
                        "tool_call_data": tool_call,
                    }
                )
                return


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat messages"""
    return StreamingResponse(
        stream_agent_response(request),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# ---------------------- CHAT STREAMING ----------------------


# ---------------------- HUMAN IN THE LOOP ----------------------
@router.post("/approve")
async def approve_action(request: ToolCallApprovalRequest):
    """Approve tool call"""
    config = {
        "configurable": {
            "thread_id": request.thread_id,
            "user_id": request.user_id,
        }
    }
    graph = init_graph(config=config)

    # Continue the graph
    graph.invoke(None, config)


@router.post("/reject")
async def reject_action(request: ToolCallApprovalRequest):
    """Reject tool call"""
    config = {
        "configurable": {
            "thread_id": request.thread_id,
            "user_id": request.user_id,
        }
    }
    graph = init_graph(config=config)

    # Continue graph with reject tool message
    graph.invoke(
        {
            "messages": [
                ToolMessage(
                    tool_call_id=request.tool_call_id,
                    content=f"Tool call denied by user. Reasoning: '{request.user_input}'. The action was NOT performed (e.g. no support ticket was created) because the user chose not to. Tell the user plainly that, as they chose, it was not done (not because of an error or restriction), then ask what they would like to do next.",
                ),
            ]
        },
        config,
    )
