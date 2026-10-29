import asyncio

import httpx
from services.chat_service import ChatService

EVENTS = [
    {"status": "Searching..."},
    "Hello",
    {"require_approval": False, "content": "x"},
]
LINES = [
    b'{"status": "Searching..."}\n',
    b'"Hello"\n',
    b'{"require_approval": false, "content": "x"}\n',
]


def stream(chunks):
    async def body():
        for c in chunks:
            yield c

    real = httpx.AsyncClient
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=body()))
    return lambda *a, **k: real(transport=transport)


def collect(chunks, monkeypatch):
    monkeypatch.setattr("services.chat_service.httpx.AsyncClient", stream(chunks))

    async def run():
        return [e async for e in ChatService().chat_stream("hi")]

    return asyncio.run(run())


def test_coalesced_events_in_one_chunk(monkeypatch):
    assert collect([b"".join(LINES)], monkeypatch) == EVENTS


def test_event_split_across_chunks(monkeypatch):
    whole = b"".join(LINES)
    chunks = [whole[:10], whole[10:40], whole[40:]]

    assert collect(chunks, monkeypatch) == EVENTS


def test_blank_and_malformed_lines_are_skipped_not_yielded(monkeypatch):
    chunks = [b'\n{"status": "a"}\nnot json\n\n"ok"\n']

    assert collect(chunks, monkeypatch) == [{"status": "a"}, "ok"]
