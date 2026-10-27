import requests
from services.chat_service import ChatService


def test_history_encodes_thread_id(monkeypatch):
    # thread_id now comes from the page URL, so it must not inject query params.
    sent = {}

    def fake_get(url, **kwargs):
        sent["url"] = requests.Request("GET", url, **kwargs).prepare().url

        class Resp:
            status_code = 200

            def json(self):
                return []

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    ChatService(thread_id="a&user_id=x").chat_history()

    assert sent["url"].endswith("/history?thread_id=a%26user_id%3Dx")
