import asyncio
import random

import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.messages import ChatMessage
from services.chat_service import ChatService
from utils.constants import BOT_AVATAR, QUICK_START, WELCOME_MESSAGE
from utils.utils import convert_chat_message, render_message

# Initialize event loop - use to stream response customize with human approval
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)


def handle_approve():
    chat_service.approve_tool_call(st.session_state.tool_call_id)


def handle_reject():
    chat_service.reject_tool_call(st.session_state.tool_call_id)


async def process_response(response):
    async for content in response:
        if isinstance(content, str):
            response_holder[0] += content
            message_placeholder.markdown(response_holder[0] + "▌")
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
        pass

# Welcome message is client-only (never in server history): pick once, always show at top
if "welcome_message" not in st.session_state:
    st.session_state.welcome_message = random.choice(WELCOME_MESSAGE)
render_message(ChatMessage(role="assistant", content=st.session_state.welcome_message))

# Show history messages to UI
for msg in history.messages:
    render_message(msg)

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

# Handle user interaction
if prompt := typed or clicked:
    chat_message = ChatMessage(role="user", content=prompt)
    render_message(chat_message)
    history.add_message(chat_message)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        response_holder = [""]

        with st.spinner("Thinking..."):
            try:
                response = chat_service.chat_stream(prompt)

                st.session_state.loop.run_until_complete(process_response(response))

                # If not have human approval, stream response is simple
                # st.write_stream(response)

                # With human approval, stream response need to handle manually

                # if response["require_approval"]:
                #     st.button('Approve', on_click=approve_action, args=[1])
                # else:
                #     st.write_stream(response)
            except Exception as e:
                st.error(e)
                st.stop()
