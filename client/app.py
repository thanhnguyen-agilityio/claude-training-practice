import asyncio

import streamlit as st
from st_pages import add_page_title, get_nav_from_toml
from utils.apis import health_check
from utils.utils import get_thread_id, render_new_chat_button, render_share_button

# Initialize user_id and thread_id
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_1"

# Initialize event loop
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)


with st.sidebar:
    st.markdown(
        """
        Hi there! 👋

        I'm here to assist you with all your shopping needs on ecommerce platform!

        Contact us via:
        - 📧 hi@ecommerce.com
        - 📞 0905 89 86 83
        - 🕔 Monday to Saturday (8:00 AM to 5:30 PM)
        """
    )
    st.divider()

    get_thread_id()
    render_new_chat_button()
    render_share_button()

nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav)
add_page_title(pg)
pg.run()

# Check server healthy
health_check()
