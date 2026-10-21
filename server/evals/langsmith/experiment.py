import os
import sys
import uuid

from langsmith import Client, evaluate

# CONFIG PATH WHEN RUN SCRIPT (via Python runner in Promptfoo) TO ALLOW IMPORT MODULE FROM ROOT DIR
# ----------------------------------------------------------------
server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
for path in [server_path]:
    if path not in sys.path:
        sys.path.append(path)
# ----------------------------------------------------------------


from agent.graph import init_graph  # noqa: E402
from evaluators import compare_semantic_similarity  # noqa: E402; is_concise_enough,


def target_function(inputs: dict):
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "user_eval_1",
        }
    }
    messages = [("user", inputs["user_query"])]
    graph = init_graph(config=config)
    response = graph.invoke({"messages": messages}, config)
    return response["messages"][-1].content


client = Client()
dataset_name = "Ecommerce Agent Dataset With Fine Tuned Model"
evaluate(
    target_function,
    data=dataset_name,
    evaluators=[compare_semantic_similarity],
    experiment_prefix="Ecommerce Agent Data Set Fine Tuning Experiment",
    num_repetitions=1,
)


# # TASK: Run 1 example with ID
# # "Ecommerce Golden Data Set"
# dataset_id = "05306da6-f37c-4765-9d28-928ca47a49b5"
# # Give me list of policies
# example_id = "40176d4a-7f5e-4be4-bea4-089547b1bf9c"
# examples = client.list_examples(dataset_id=dataset_id)
# for example in examples:
#     if str(example.id) == example_id:
#         example_to_run = example
#         break

# evaluate(
#     target_function,
#     data=[example_to_run],
#     evaluators=[
#         compare_semantic_similarity,
#         # is_concise_enough,
#         latency_evaluator
#     ],
#     experiment_prefix=f"Eval example {example_id}",
# )

# Need recheck: all product query is not correct
# Give me price of "Iphone 15"
# Compare "Viviane Pleated Fitted Dress" and "Pauline Neckline Fitted Dress".
# How much is the product "French Style Vest (with Croptop)"?
# Give me product "Lucille Silk Collared Shirt"
# Is "Sleeves Style Shirt" in stock?
