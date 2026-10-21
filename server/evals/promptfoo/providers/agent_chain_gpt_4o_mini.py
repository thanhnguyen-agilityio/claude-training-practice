import json
import os
import sys
import uuid

from langchain.schema.runnable import RunnableLambda
from langchain_core.runnables import chain

# CONFIG PATH WHEN RUN SCRIPT (via Python runner in Promptfoo) TO ALLOW IMPORT MODULE FROM ROOT DIR
# ----------------------------------------------------------------
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if root_path not in sys.path:
    sys.path.append(root_path)

# ----------------------------------------------------------------
from agent import init_graph, input_format, output_format  # noqa: E402


@chain
def graph_chain(data: dict):
    """Set thread_id from client input for graph agent"""
    graph_agent = init_graph(model_name="gpt-4o-mini", temperature=0.2)
    return graph_agent.with_config(
        {"configurable": {"thread_id": data["thread_id"]}}
    ).invoke(data)


def call_api(query, options, context):
    main_chain = (
        RunnableLambda(input_format) | graph_chain | RunnableLambda(output_format)
    )
    response = main_chain.invoke(
        json.dumps(
            {"message": context["vars"]["query"], "thread_id": str(uuid.uuid4())}
        )
    )

    result = {
        "output": response,
    }

    return result
