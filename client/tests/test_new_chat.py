from pathlib import Path
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest

CLIENT = Path(__file__).parents[1]
MESSAGES_KEY = "user_user_1_chat_messages"


def test_new_chat_button_starts_fresh_conversation(monkeypatch):
    monkeypatch.chdir(CLIENT)  # app.py reads .streamlit/pages.toml relatively
    at = AppTest.from_file(str(CLIENT / "app.py"), default_timeout=30)
    at.query_params["thread"] = "old"
    at.session_state[MESSAGES_KEY] = ["old message"]
    with patch("utils.apis.requests.get", return_value=MagicMock(status_code=200)):
        at.run()
        assert at.session_state["thread_id"] == "old"

        buttons = [b for b in at.sidebar.button if b.label == "➕ New chat"]
        assert buttons, "no New chat button in the sidebar"
        buttons[0].click().run()

    assert at.session_state["thread_id"] not in ("old", None)
    assert "thread" not in at.query_params
    assert MESSAGES_KEY not in at.session_state
