import asyncio
import logging
import random

import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.messages import ChatMessage
from services.chat_service import ChatService
from utils.constants import (
    BOT_AVATAR,
    ERROR_GENERIC,
    QUICK_START,
    STOPPED_NOTE,
    WELCOME_MESSAGE,
)
from utils.utils import convert_chat_message, render_message


# Buttons only record the choice; the slow call runs in the page body so a spinner can show.
def handle_approve():
    st.session_state.pending_decision = "approve"


def handle_reject():
    st.session_state.pending_decision = "reject"


# Puts the Stop button over the chat input's send arrow; label kept for screen readers
STOP_BUTTON_CSS = """<style>
[data-testid="stChatInputSubmitButton"] { visibility: hidden; }
.st-key-stop_area { position: absolute; right: 0; bottom: 1rem; width: 40px; gap: 0; z-index: 1; }
.st-key-stop_area button {
    width: 40px; height: 40px; min-height: 0; padding: 0; border: none; background: transparent;
}
.st-key-stop_area [data-testid="stMarkdownContainer"] {
    position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0);
}
</style>"""


# Streamlit's fast rerun starts the next run at once, while the stopped run is
# still blocked on the stream, so take the partial reply it keeps in session state.
def handle_stop():
    st.session_state.stopped_reply = st.session_state.pop("partial_reply", "")


async def process_response(response):
    async for content in response:
        if isinstance(content, str):
            if content:
                status_placeholder.empty()
            response_holder[0] += content
            st.session_state.partial_reply = response_holder[0]
            message_placeholder.markdown(response_holder[0] + "▌")
            continue

        if "heartbeat" in content:
            # Any render lets Streamlit act on a Stop click while the server is busy.
            message_placeholder.markdown(response_holder[0] + "▌")
            continue

        if "status" in content:
            status_placeholder.caption(content["status"])
            continue

        if content["require_approval"]:
            message = content["message"]
            tool_call_data = content["tool_call_data"]
            st.session_state.tool_call_id = tool_call_data["id"]

            response_holder[0] += message
            message_placeholder.markdown(response_holder[0])

            # Create approve,reject button
            # Create columns for buttons
            col1, col2 = st.columns(2)
            with col1:
                st.button(
                    "Yes",
                    key="approve_button",
                    type="tertiary",
                    icon="✅",
                    use_container_width=True,
                    on_click=handle_approve,
                )
            with col2:
                st.button(
                    "No",
                    key="reject_button",
                    type="tertiary",
                    icon="❌",
                    use_container_width=True,
                    on_click=handle_reject,
                )

            return response_holder[0]
        else:
            response_holder[0] += content.get("content", "")
            message_placeholder.markdown(response_holder[0] + "▌")

    message_placeholder.markdown(response_holder[0])
    if response_holder[0]:
        history.add_message(ChatMessage(role="assistant", content=response_holder[0]))


# Initialize chat service
chat_service = ChatService(
    user_id=st.session_state.user_id,
    thread_id=st.session_state.thread_id,
)

# load history messages from Streamlit session state
history = StreamlitChatMessageHistory(
    key=f"user_{st.session_state.user_id}_chat_messages"
)

# Get chat history of thread_id
with st.spinner("Loading..."):
    try:
        messages = chat_service.chat_history()
        history_message_convert = []
        for message in messages:
            message_convert = convert_chat_message(message["type"], message["content"])
            if message_convert:
                history_message_convert.append(message_convert)

        history.messages = history_message_convert
    except Exception:
        logging.exception("Cannot load chat history")

# Welcome message is client-only (never in server history): pick once, always show at top
if "welcome_message" not in st.session_state:
    st.session_state.welcome_message = random.choice(WELCOME_MESSAGE)
render_message(ChatMessage(role="assistant", content=st.session_state.welcome_message))

# Show history messages to UI
for msg in history.messages:
    render_message(msg)

# A stopped reply shows until the server's saved copy (ends history with the assistant) loads
if "stopped_reply" in st.session_state:
    if history.messages and history.messages[-1].role == "user":
        reply = st.session_state.stopped_reply
        render_message(
            ChatMessage(
                role="assistant",
                content=f"{reply}\n\n{STOPPED_NOTE}" if reply else STOPPED_NOTE,
            )
        )
    else:
        del st.session_state["stopped_reply"]

typed = st.chat_input(placeholder="Give me categories list.")
clicked = st.session_state.pop("quick_start_prompt", None)

# Suggestions only on an empty conversation; a click sends the query
if not history.messages and not (typed or clicked):
    for category, examples in QUICK_START.items():
        st.caption(category)
        for example in examples:
            st.button(
                example,
                key=f"quick_start_{example}",
                on_click=st.session_state.__setitem__,
                args=("quick_start_prompt", example),
            )

# Send the clicked Yes/No to the server, then rerun so the history reload shows its reply
if decision := st.session_state.pop("pending_decision", None):
    call = getattr(chat_service, f"{decision}_tool_call")
    failed = False
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Working on it..."):
            try:
                call(st.session_state.tool_call_id)
            except Exception as e:
                st.error(e)
                failed = True
    if not failed:
        st.rerun()

# Handle user interaction
if prompt := typed or clicked:
    chat_message = ChatMessage(role="user", content=prompt)
    render_message(chat_message)
    history.add_message(chat_message)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        # Stop takes the send button's place in the chat input while the reply streams
        # ponytail: st._bottom is private (the chat input's container); recheck on upgrade
        stop_placeholder = st._bottom.empty()
        with stop_placeholder.container(key="stop_area"):
            st.markdown(STOP_BUTTON_CSS, unsafe_allow_html=True)
            st.button(
                "Stop response",
                key="stop_button",
                icon=":material/stop_circle:",
                on_click=handle_stop,
            )
        response_holder = [""]
        st.session_state.partial_reply = ""

        response = chat_service.chat_stream(prompt)
        # Own loop per reply: a stopped run may still be inside its loop when the next starts
        loop = asyncio.new_event_loop()
        with st.spinner("Thinking..."):
            try:
                loop.run_until_complete(process_response(response))
                st.session_state.pop("partial_reply", None)

                # If not have human approval, stream response is simple
                # st.write_stream(response)

                # With human approval, stream response need to handle manually

                # if response["require_approval"]:
                #     st.button('Approve', on_click=approve_action, args=[1])
                # else:
                #     st.write_stream(response)
            except Exception:
                st.session_state.pop("partial_reply", None)
                status_placeholder.empty()  # st.stop() below skips `finally` output
                logging.exception("Chat stream failed")
                st.error(ERROR_GENERIC)
                st.stop()
            finally:
                # Close the HTTP stream so the server sees the disconnect
                loop.run_until_complete(response.aclose())
                loop.close()
                status_placeholder.empty()
                stop_placeholder.empty()
