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
