import sqlite3
import sys

from agent.graph import init_graph, route_after_sensitive_tools, ticket_rejected
from agent.tools import create_support_ticket
from agent.tools.create_support_ticket import TICKET_NOT_CREATED_PREFIX
from langchain_core.messages import AIMessage, ToolMessage

REJECTED = (
    f"{TICKET_NOT_CREATED_PREFIX} invalid phone '12ab'. "
    "A phone number must be 9 to 15 digits, optionally starting with +. "
    "Tell the user the reason and ask them for a valid phone number."
)


def test_routing_rejected_ticket_skips_the_model():
    rejected = {"messages": [ToolMessage(REJECTED, tool_call_id="c")]}
    ok = {
        "messages": [
            ToolMessage("Support ticket created successfully!", tool_call_id="c")
        ]
    }
    assert route_after_sensitive_tools(rejected) == "ticket_rejected"
    assert route_after_sensitive_tools(ok) == "assistant"


def test_rejected_node_replies_with_reason_only():
    state = {"messages": [ToolMessage(REJECTED, tool_call_id="c")]}
    msg = ticket_rejected(state)["messages"]
    assert isinstance(msg, AIMessage)
    assert "invalid phone '12ab'" in msg.content
    assert "9 to 15 digits" in msg.content
    assert "created successfully" not in msg.content
    assert "Tell the user" not in msg.content


def test_graph_wires_sensitive_tools_to_ticket_rejected_then_end():
    graph = init_graph(streaming=False, config={"configurable": {"user_id": "u"}})
    edges = {(e.source, e.target) for e in graph.get_graph().edges}
    assert ("sensitive_tools", "ticket_rejected") in edges
    assert ("ticket_rejected", "__end__") in edges


def test_rejection_found_among_all_tool_results_of_the_step():
    state = {
        "messages": [
            ToolMessage(REJECTED, tool_call_id="a"),
            ToolMessage("Some other tool result", tool_call_id="b"),
        ]
    }
    assert route_after_sensitive_tools(state) == "ticket_rejected"
    reply = ticket_rejected(state)["messages"]
    assert "invalid phone '12ab'" in reply.content


def test_real_tool_output_gives_exact_user_reply(tmp_path, monkeypatch):
    path = str(tmp_path / "ecommerce_store.db")
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE SupportTicket (id INTEGER PRIMARY KEY, name TEXT, email TEXT,"
            " subject TEXT, phone TEXT, description TEXT, resolved BOOLEAN)"
        )
    monkeypatch.setattr(
        sys.modules["agent.tools.create_support_ticket"], "get_path", lambda *_: path
    )
    output = create_support_ticket.invoke(
        {"email": "lan@gmail.com", "subject": "torn dress", "phone": "12ab"}
    )
    state = {"messages": [ToolMessage(output, tool_call_id="c")]}
    assert route_after_sensitive_tools(state) == "ticket_rejected"
    assert ticket_rejected(state)["messages"].content == (
        "Your support ticket was not created: invalid phone '12ab'. "
        "A phone number must be 9 to 15 digits, optionally starting with +. "
        "Please send the corrected details and I'll prepare the ticket again."
    )
