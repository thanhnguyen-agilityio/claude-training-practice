from agent.graph import init_graph
from fastapi import APIRouter
from langchain_core.messages import AnyMessage

router = APIRouter(prefix="/history", tags=[""])


@router.get("/")
def history(thread_id: str) -> list[AnyMessage]:
    """Get chat history"""
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": None
        }
    }
    graph = init_graph(config=config)
    state_snapshot = graph.get_state(
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        }
    )
    return state_snapshot.values.get("messages", [])
