# auto-issues lessons

Read by every `/auto-issues` worker before it starts. Add a lesson only after a run report confirms it; one line each, as a rule.

- To test a chat history reload in the UI, navigate to another page and back; a browser reload starts a new thread.
- Streamlit button `on_click` callbacks run before the page body renders: anything they draw (a spinner) is never seen. Set a session_state flag in the callback and do the work in the page body.
- In Streamlit, `st.stop()` skips everything after it, including UI output in a `finally`; clear placeholders before calling it, or avoid it so the chat input still renders.
- `AppTest.from_file("app.py")` does not render `st.navigation` pages; test a page with `AppTest.from_file("pages/<page>.py")` and pass `run(timeout=20)`, since the 3s default flakes on a cold start.
- A sync LangGraph `graph.stream()` inside an async generator blocks the event loop, so events reach the client only at the end; pull items with `await asyncio.to_thread(next, events, None)`.
- In Claude in Chrome, open your own tab (others may be in use by another worker) and wait ~4–8s after navigating before typing, or the first message is lost.
