from agent.graph import Assistant
from langchain_core.messages import AIMessage, HumanMessage


class FakeRunnable:
    def invoke(self, state):
        self.state = state
        return AIMessage("ok")


def test_assistant_input_includes_conversation_summary():
    runnable = FakeRunnable()
    state = {
        "messages": [HumanMessage("my name?")],
        "summary": "The user's name is Thanh.",
    }

    Assistant(runnable)(state, {})

    sent = " ".join(str(m.content) for m in runnable.state["messages"])
    assert "Thanh" in sent, "summary never reaches the model"


def test_summarize_only_new_older_messages(monkeypatch):
    from agent import graph

    seen = []

    class FakeLLM:
        def invoke(self, msgs):
            seen.append(msgs)
            return AIMessage("S2")

    monkeypatch.setattr(graph, "model_gpt_4o_mini", FakeLLM())
    monkeypatch.setattr(graph, "recent_window", lambda m, n: m[-1:])
    monkeypatch.setattr(graph, "trim_messages", lambda w, **kw: w)
    msgs = [HumanMessage(f"m{i}") for i in range(5)]
    state = {"messages": msgs, "summary": "S1", "summarized_count": 3}

    out = graph.summarize_conversation(state)

    sent = [m.content for m in seen[0]]
    assert "m0" not in sent and "m2" not in sent, "already-summarized messages re-sent"
    assert "m3" in sent and any("S1" in c for c in sent)
    assert out["summarized_count"] == 4 and out["summary"] == "S2"


def _summarize(monkeypatch, state):
    from agent import graph

    class FakeLLM:
        def invoke(self, msgs):
            return AIMessage("S2")

    monkeypatch.setattr(graph, "model_gpt_4o_mini", FakeLLM())
    monkeypatch.setattr(graph, "recent_window", lambda m, n: m[-1:])
    monkeypatch.setattr(graph, "trim_messages", lambda w, **kw: w)
    return graph.summarize_conversation(state)


def test_summarize_old_checkpoint_without_count(monkeypatch):
    msgs = [HumanMessage(f"m{i}") for i in range(5)]
    out = _summarize(monkeypatch, {"messages": msgs, "summary": "S1"})
    assert out["summarized_count"] == 4


def test_summarize_nothing_new_returns_only_window_start(monkeypatch):
    msgs = [HumanMessage(f"m{i}") for i in range(5)]
    out = _summarize(
        monkeypatch, {"messages": msgs, "summary": "S1", "summarized_count": 4}
    )
    assert out == {"window_start": 4}
