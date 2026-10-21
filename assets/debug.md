# 🔍 Debug

- Check api docs `http://127.0.0.1:8080/docs`
- PlayGround: `http://localhost:8080/chat/playground/`
    - Test: `{"message": "hello", "thread_id": "3b4de725-586a-4e48-b824-41bdc3c18cf5"}`
- Run local graph: `uv run scripts/graph_local.py`
- Debug with tracer
  This debugger is used to debug python code run in promptfoo for example
  - Add trace in code:
    ```bash
    from remote_pdb import RemotePdb
    RemotePdb('127.0.0.1', 4444).set_trace()
    ```
  - Access the debugger:
    ```bash
    telnet 127.0.0.1 4444
    ```
  - Check port on use: `lsof -t -i:4444`
  - Kill process on port: `kill lsof -t -i:4444`

- Debug database: call db in `sql_tools.py`
```bash
print(db.run("SELECT * FROM Product LIMIT 2;"))
```