import os
import sys
import uuid

from langgraph.types import Command

# CONFIG PATH WHEN RUN SCRIPT TO ALLOW IMPORT MODULE FROM PARENT DIR: server
# ----------------------------------------------------------------
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)
# ----------------------------------------------------------------
from agent.graph import init_graph  # noqa: E402
from utils.utils import count_time  # noqa: E402

graph = init_graph(streaming=False)


def stream_graph_updates(user_input: str, config):
    for event in graph.stream({"messages": [("user", user_input)]}, config):
        for value in event.values():
            if not value:
                print("value is empty: ", value)
                continue
            elif type(value) is tuple:
                print("value", value)
            elif type(value["messages"]) is list:
                print("value message is a list!---")
                for item in value["messages"]:
                    item.pretty_print()
                    print("--------------------------------------------")
            else:
                value["messages"].pretty_print()
                print("--------------------------------------------")


def check_graph_interruption(config):
    print("check interruption:")
    # Check interruption
    snapshot = graph.get_state(config)
    print("snapshot.next:", snapshot.next)
    print(snapshot.values["messages"][-1].tool_calls)


def continue_interruption(config):
    # Continue to use tool
    print("continue the interruption:")
    events = graph.stream(Command(resume={"action": "continue"}), config, stream_mode="values")
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()


@count_time
def invoke_graph(user_input: str, config):
    response = graph.invoke({"messages": [("user", user_input)]}, config)

    response["messages"][-1].pretty_print()
    # for message in response["messages"]:
    #     message.pretty_print()


def add_debug():
    from remote_pdb import RemotePdb

    RemotePdb("127.0.0.1", 4444).set_trace()


if __name__ == "__main__":
    # config = {"configurable": {"thread_id": "graph_local_1"}}
    config = {
        "configurable": {
            "thread_id": f"graph_local_{str(uuid.uuid4())}",
            "user_id": "user_1",
        }
    }

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input, config)

            check_graph_interruption(config)
    #         # continue_interruption(config)
        except Exception as e:
            # fallback if input() is not available
            print("Error:", e)
            user_input = "Hi there! My name is Will."
            print("User: " + user_input)
            stream_graph_updates(user_input, config)
            break

    # TEST INVOKE
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            invoke_graph(user_input, config)
        except Exception as e:
            raise e

# TESTING GRAPH AGENT-------------------------------------------------------
# THREAD 1:
# config = {"configurable": {"thread_id": "user_local_1"}}
# user_input = "Hi there! My name is Will."

# # The config is the **second positional argument** to stream() or invoke()!
# events = graph_agent.stream(
#     {"messages": [("user", user_input)]}, config, stream_mode="values"
# )
# for event in events:
#     event["messages"][-1].pretty_print()

# user_input = "Remember my name?"

# # The config is the **second positional argument** to stream() or invoke()!
# events = graph_agent.stream(
#     {"messages": [("user", user_input)]}, config, stream_mode="values"
# )
# for event in events:
#     event["messages"][-1].pretty_print()

# snapshot = graph_agent.get_state(config)
# print(snapshot)

# THREAD 2:
# config2 = {"configurable": {"thread_id": "2"}}
# events = graph_agent.stream(
#     {"messages": [("user", user_input)]},
#     config2,
#     stream_mode="values",
# )
# for event in events:
#     event["messages"][-1].pretty_print()

# snapshot = graph_agent.get_state(config2)
# print(snapshot)
# print(snapshot.next)
# def stream_graph_updates(user_input: str, config):
#     for event in graph_agent.stream(
#         {"messages": [("user", user_input)]},
#         config
#     ):
#         for value in event.values():
#             print("value:", value)
#             # print("Assistant:", value["messages"][-1].content)


# # TESTING GRAPH AGENT-------------------------------------------------------
