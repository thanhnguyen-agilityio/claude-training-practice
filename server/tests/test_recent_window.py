from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    trim_messages,
)

from utils.utils import prepend_summary, recent_window


def test_window_starts_on_human_message():
    msgs = [HumanMessage("my name is Thanh"), AIMessage("hi"), HumanMessage("categories"),
            AIMessage("list"), HumanMessage("my name?")]
    assert recent_window(msgs, 2) == msgs[2:]  # first turn left for the summary


def test_tool_loop_keeps_current_question():
    msgs = [HumanMessage("q"), AIMessage("", tool_calls=[{"id": "c", "name": "t", "args": {}}]),
            ToolMessage("r", tool_call_id="c")]
    assert recent_window(msgs, 1) == msgs


def test_summary_survives_assistant_pipeline():
    # Same steps as Assistant.__call__: trim first, summary after (trim drops system messages).
    msgs = [HumanMessage("my name is Thanh"), AIMessage("hi"), HumanMessage("my name?")]
    trimmed = trim_messages(recent_window(msgs, 1), max_tokens=1000, strategy="last",
                            start_on="human", token_counter=len, allow_partial=False)
    out = prepend_summary(trimmed, "user is Thanh")

    assert isinstance(out[0], SystemMessage) and "Thanh" in out[0].content
    assert out[1:] == msgs[2:]


def test_no_summary_adds_nothing():
    msgs = [HumanMessage("a"), AIMessage("b")]
    assert prepend_summary(msgs, "") == msgs
