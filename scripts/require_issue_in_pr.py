"""PreToolUse hook: block `gh pr create` when the PR does not link an issue.

Reads the hook JSON from stdin. Exit 2 (message on stderr) blocks the call;
exit 0 allows it. Stdlib only, never crashes: unexpected errors allow the call.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

ISSUE_RE = re.compile(
    r"\b(close[sd]?|fix(e[sd])?|resolve[sd]?|refs?|part of)\s+"
    r"(#\d+|https://github\.com/[^\s/]+/[^\s/]+/issues/\d+)",
    re.IGNORECASE,
)
BODY_FILE_RE = re.compile(
    r"(?:--body-file|-F)(?:=|\s+)(?P<q>[\"']?)(?P<path>[^\s\"']+)(?P=q)"
)
BODY_FLAGS = {"--body-file", "-F"}

MESSAGE = (
    "Blocked: no linked issue found in the PR. Create one with `gh issue create` "
    "first, then put `Closes #<n>` (or `Refs #<n>`) in the PR body."
)


def _body_file_paths(command: str) -> list[str]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return [m.group("path") for m in BODY_FILE_RE.finditer(command)]
    paths = []
    for i, tok in enumerate(tokens):
        if tok in BODY_FLAGS and i + 1 < len(tokens):
            paths.append(tokens[i + 1])
        elif tok.startswith("--body-file="):
            paths.append(tok.split("=", 1)[1])
    return paths


def check(command: str, cwd: str) -> str | None:
    """Return an error message if the PR links no issue, else None."""
    if "gh pr create" not in command:
        return None
    texts = [command]
    for p in _body_file_paths(command):
        path = Path(p).expanduser()
        if not path.is_absolute():
            path = Path(cwd or ".") / path
        try:
            texts.append(path.read_text(errors="replace"))
        except OSError:
            continue
    if any(ISSUE_RE.search(t) for t in texts):
        return None
    return MESSAGE


def main() -> int:
    try:
        data = json.load(sys.stdin)
        command = (data.get("tool_input") or {}).get("command") or ""
        message = check(command, data.get("cwd") or "")
    except Exception:
        return 0
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
