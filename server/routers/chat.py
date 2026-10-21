import asyncio
import json
from typing import AsyncGenerator

from agent.graph import init_graph
from agent.tools import sensitive_tool_names
from fastapi import APIRouter
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import ToolMessage
from schema.schema import ChatRequest, ToolCallApprovalRequest
from utils.utils import build_require_approval_message

router = APIRouter(prefix="/chat", tags=[""])


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
    response = graph.invoke({"messages": messages}, config)["messages"][0].content
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

    # Stream messages of assistant node
    for msg, metadata in graph.stream(
        {"messages": messages},
        config,
        stream_mode="messages"
    ):
        if metadata["langgraph_node"] == "assistant":
            yield json.dumps(msg.content).encode("utf-8")
            await asyncio.sleep(0.05)

    # interrupt
    snapshot = graph.get_state(config)
    if snapshot.next and snapshot.next[0] == "sensitive_tools":
        for tool_call in snapshot.values["messages"][-1].tool_calls:
            if tool_call["name"] in sensitive_tool_names:
                yield json.dumps({
                    "require_approval": True,
                    "message": build_require_approval_message(tool_call),
                    "thread_id": request.thread_id,
                    "tool_call_data": tool_call,
                }).encode("utf-8")
                return

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat messages"""
    return StreamingResponse(
        stream_agent_response(request),
        media_type="application/json",
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
                    content=f"Tool call denied by user. Reasoning: '{request.user_input}'. Continue assisting, accounting for the user's input.",

                ),
            ]
        },
        config
    )
