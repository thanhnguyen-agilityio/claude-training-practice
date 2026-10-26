from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from utils.utils import build_model_input


def test_summary_prepended_and_window_kept():
    msgs = [HumanMessage("my name is Thanh"), AIMessage("hi"), HumanMessage("categories"),
            AIMessage("list"), HumanMessage("my name?")]
    out = build_model_input(msgs, "user is Thanh", 2)

    assert isinstance(out[0], SystemMessage) and "Thanh" in out[0].content
    assert out[1:] == msgs[2:]  # window starts on a human message; first turn is in the summary


def test_no_summary_adds_nothing():
    msgs = [HumanMessage("a"), AIMessage("b")]
    assert build_model_input(msgs, "", 5) == msgs


def test_tool_loop_keeps_current_question():
    msgs = [HumanMessage("q"), AIMessage("", tool_calls=[{"id": "c", "name": "t", "args": {}}]),
            ToolMessage("r", tool_call_id="c")]
    assert build_model_input(msgs, "", 1) == msgs
