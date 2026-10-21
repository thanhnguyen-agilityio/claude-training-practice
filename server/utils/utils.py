import json
import os
import time

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode


def load_json(file_path: str):
    if not file_path or file_path.lower().endswith(".json") is False:
        print(f"Invalid file path: {file_path}")
        return

    with open(os.path.abspath(file_path), "rb") as file:
        try:
            return json.loads(file.read())
        except json.JSONDecodeError:
            print(f"Error decoding JSON file: {file_path}")
            return


def get_path(file_name: str, folder: str = "."):
    return os.path.abspath(f"{folder}/{file_name}")


def is_chroma_db_exist(persist_directory: str) -> bool:
    # Check if the directory exists
    if not os.path.exists(persist_directory):
        return False

    # Check for specific metadata files used by Chroma
    required_files = ["chroma.sqlite3"]
    for file in required_files:
        if not os.path.exists(os.path.join(persist_directory, file)):
            return False

    return True


def count_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time for {func.__name__}: {end_time - start_time} seconds")
        return result

    return wrapper

def build_require_approval_message(tool_call_data: dict) -> dict:
    tool_name = tool_call_data["name"]
    tool_action_msg = ""
    tool_call_data_str = ""

    if tool_name == "create_support_ticket":
        tool_action_msg = "We are about to create a support ticket on your behalf"
    if tool_name == "search_google_shopping":
        tool_action_msg = "We are about to expand search to Google Shopping"

    for arg_name, arg_value in tool_call_data["args"].items():
        tool_call_data_str += f"\n  - {arg_name.title()}: {arg_value}"

    return "**Action Required: Please Confirm**\n\n {action}. Please review the details below and confirm:\n\n {details}".format(
        action=tool_action_msg, details=tool_call_data_str
    )

# ----- LangGraph Utils - before use prebuilt create_react_agent -----
# from langchain_core.messages import ToolMessage
# from langchain_core.runnables import RunnableLambda
# from langgraph.prebuilt import ToolNode

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

# ----- LangGraph Utils - before use prebuilt create_react_agent -----


# Note: We disable parallel tool callings then don't need to process the malformed messages
# def handle_malformed_messages(state):
#     """
#     Handle malformed messages in the chat history.
#     There is a case when multiple tools cause the chat history to be invalid.
#     Ref: https://langchain-ai.github.io/langgraph/troubleshooting/errors/INVALID_CHAT_HISTORY/

#     Args:
#         state (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     messages = state["messages"]
#     clean_messages = []
#     last_ai_message_call_tools = None

#     for i, msg in enumerate(messages):
#         if isinstance(msg, AIMessage):
#             if msg.tool_calls:
#                 last_ai_message_call_tools = msg
#             else:
#                 clean_messages.append(msg)
#         elif isinstance(msg, ToolMessage):
#             before_message  = messages[i - 1] if i > 0 else None
#             if before_message:
#                 if isinstance(before_message, AIMessage):
#                     ai_message = before_message
#                 else:
#                     ai_message = last_ai_message_call_tools

#                 # Manual create AIMessage for ToolMessage
#                 tool_calls = []
#                 tool_calls_additional_kwargs = []

#                 # Find tool_calls data from last AI message
#                 if ai_message.tool_calls:
#                     for tool_call in ai_message.tool_calls:
#                         if tool_call["id"] == msg.tool_call_id:
#                             tool_calls.append(tool_call)

#                 if ai_message.additional_kwargs.get("tool_calls"):
#                     for tool_call_additional_kwargs in ai_message.additional_kwargs["tool_calls"]:
#                         if tool_call_additional_kwargs["id"] == msg.tool_call_id:
#                             tool_calls_additional_kwargs.append(tool_call_additional_kwargs)

#                 tool_ai_message = AIMessage(
#                     content="",
#                     tool_calls=tool_calls,
#                     additional_kwargs={"tool_calls": tool_calls_additional_kwargs}
#                 )

#             clean_messages.append(tool_ai_message)
#             clean_messages.append(msg)
#         else:
#             clean_messages.append(msg)

#     state["messages"] = clean_messages
#     return state


def handle_keep_recent_messages(
        messages: list[AnyMessage],
        recent_messages_number: int = 5
) -> list[AnyMessage]:
    """
    Util function to keep the recent messages and remove the old ones.
    """
    tool_call_ids = set()

    recent_messages = messages[-recent_messages_number:]
    remove_messages = messages[:-recent_messages_number]

    # Collect tool call IDs from the recent_messages
    for msg in recent_messages:
        if hasattr(msg, 'tool_calls'):
            tool_call_ids.update([tc["id"] for tc in msg.tool_calls])

    # Keeping necessary context for tool calling of the recent_messages
    for msg in remove_messages:
        # Keep messages that are responses to recent tool calls
        if isinstance(msg, ToolMessage) and msg.tool_call_id in tool_call_ids:
            recent_messages.append(msg)
        elif (
            isinstance(msg, AIMessage)
            and msg.tool_calls
            and any(tc["id"] in tool_call_ids for tc in msg.tool_calls)
        ):
            recent_messages.append(msg)

    return recent_messages