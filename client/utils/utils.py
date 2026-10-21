from langchain_core.messages import ChatMessage
from streamlit import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from utils.constants import BOT_AVATAR, USER_AVATAR


def get_session_id():
    return get_script_run_ctx().session_id


def convert_chat_message(message_type, content):
    match message_type:
        case "human":
            return ChatMessage(role="user", content=content)
        case "ai":
            return ChatMessage(role="assistant", content=content)
        case _:
            return ChatMessage(role="unknown", content=content)


def get_chat_message_avatar(msg):
    if not msg:
        return "🤔"

    match msg.role:
        case "user":
            return "👤"
        case "assistant":
            return "🤖"
        case _:
            return "🤔"


def render_message(msg):
    if not msg or msg.role not in ["user", "assistant"] or not msg.content:
        return

    if msg.role == "user":
        avatar = USER_AVATAR
    else:
        avatar = BOT_AVATAR

    message = st.chat_message(msg.role, avatar=avatar)
    message.markdown(msg.content)
