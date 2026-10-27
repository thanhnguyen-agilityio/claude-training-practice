from urllib.parse import quote

from streamlit.testing.v1 import AppTest


def app():
    import streamlit as st
    from utils.utils import get_session_id, get_thread_id, render_share_button

    st.write(get_thread_id())
    st.write(get_session_id())
    render_share_button()


def thread_and_session(at):
    return at.markdown[0].value, at.markdown[1].value


def test_new_visit_uses_session_thread():
    at = AppTest.from_function(app).run()

    thread, session = thread_and_session(at)
    assert thread == session


def test_shared_link_opens_its_thread():
    at = AppTest.from_function(app)
    at.query_params["thread"] = "abc"
    at.run()

    assert thread_and_session(at)[0] == "abc"


def test_thread_kept_when_param_dropped():
    # Page navigation drops query params; the shared thread must stay.
    at = AppTest.from_function(app)
    at.query_params["thread"] = "abc"
    at.run()
    del at.query_params["thread"]
    at.run()

    assert thread_and_session(at)[0] == "abc"


def test_share_sets_link_to_thread():
    at = AppTest.from_function(app).run()
    thread = thread_and_session(at)[0]

    at.button[0].click().run()

    assert at.query_params["thread"] == [thread]
    assert at.code[0].value.endswith(f"/?thread={quote(thread)}")


def test_share_link_encodes_thread():
    at = AppTest.from_function(app)
    at.query_params["thread"] = "a&b c"
    at.run()

    at.button[0].click().run()

    assert at.code[0].value.endswith("/?thread=a%26b%20c")
