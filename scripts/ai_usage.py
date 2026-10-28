"""Sum Claude Code token usage and estimated cost for one session / time window."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

# USD per 1M tokens. Cache write 5m = 1.25x input, 1h = 2x input.
PRICES: dict[str, dict[str, float]] = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.20},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
    "claude-fable-5-1": {"input": 10.00, "output": 50.00, "cache_read": 0.25},
}
FIELDS = ("input", "cache_write_5m", "cache_write_1h", "cache_read", "output")


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def cost_for(model: str, tokens: dict[str, int]) -> float | None:
    p = PRICES.get(model)
    if p is None:
        return None
    total = (
        tokens["input"] * p["input"]
        + tokens["cache_write_5m"] * p["input"] * 1.25
        + tokens["cache_write_1h"] * p["input"] * 2.0
        + tokens["cache_read"] * p["cache_read"]
        + tokens["output"] * p["output"]
    )
    return total / 1_000_000


def _record(line: dict) -> dict | None:
    if line.get("type") != "assistant":
        return None
    msg = line.get("message")
    if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
        return None
    model = msg.get("model")
    if not model or model == "<synthetic>" or not line.get("timestamp"):
        return None
    u = msg["usage"]
    cc = u.get("cache_creation")
    if isinstance(cc, dict):
        w5, w1 = (
            cc.get("ephemeral_5m_input_tokens", 0),
            cc.get("ephemeral_1h_input_tokens", 0),
        )
    else:
        w5, w1 = u.get("cache_creation_input_tokens", 0), 0
    return {
        "id": msg.get("id"),
        "model": model,
        "timestamp": line["timestamp"],
        "input": u.get("input_tokens", 0) or 0,
        "cache_write_5m": w5 or 0,
        "cache_write_1h": w1 or 0,
        "cache_read": u.get("cache_read_input_tokens", 0) or 0,
        "output": u.get("output_tokens", 0) or 0,
    }


def load_usage(
    project_dir: Path,
    session_id: str,
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[dict]:
    files = [project_dir / f"{session_id}.jsonl"]
    files += sorted((project_dir / session_id / "subagents").glob("*.jsonl"))
    seen: set[str] = set()
    records: list[dict] = []
    for f in files:
        if not f.is_file():
            continue
        for raw in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                line = json.loads(raw)
            except json.JSONDecodeError:
                continue
            rec = _record(line) if isinstance(line, dict) else None
            if rec is None:
                continue
            try:
                ts = parse_ts(rec["timestamp"])
            except ValueError:
                continue
            if (since and ts < since) or (until and ts >= until):
                continue
            if rec["id"]:
                if rec["id"] in seen:
                    continue
                seen.add(rec["id"])
            records.append(rec)
    return records


def summarize(records: list[dict]) -> dict:
    models: dict[str, dict] = {}
    unknown: list[str] = []
    for r in records:
        m = models.setdefault(r["model"], {"requests": 0, **dict.fromkeys(FIELDS, 0)})
        m["requests"] += 1
        for k in FIELDS:
            m[k] += r[k]
    total = {"requests": 0, **dict.fromkeys(FIELDS, 0)}
    total_cost = 0.0
    for name, m in models.items():
        m["total_tokens"] = sum(m[k] for k in FIELDS)
        cost = cost_for(name, m)
        if cost is None:
            unknown.append(name)
        else:
            total_cost += cost
        m["cost_usd"] = None if cost is None else round(cost, 4)
        for k in ("requests", *FIELDS):
            total[k] += m[k]
    total["total_tokens"] = sum(total[k] for k in FIELDS)
    total["cost_usd"] = round(total_cost, 4)
    stamps = sorted((parse_ts(r["timestamp"]), r["timestamp"]) for r in records)
    first, last = (stamps[0], stamps[-1]) if stamps else (None, None)
    minutes = round((last[0] - first[0]).total_seconds() / 60, 1) if first else 0.0
    return {
        "models": models,
        "total": total,
        "unknown_models": sorted(unknown),
        "first_timestamp": first[1] if first else None,
        "last_timestamp": last[1] if last else None,
        "active_minutes": minutes,
    }


def to_markdown(s: dict) -> str:
    cols = ["requests", *FIELDS, "total_tokens", "cost_usd"]
    lines = ["| model | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    rows = [*s["models"].items(), ("TOTAL", s["total"])]
    for name, m in rows:
        cells = ["n/a" if m[c] is None else str(m[c]) for c in cols]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(
        f"First: {s['first_timestamp']}  Last: {s['last_timestamp']}  Active minutes: {s['active_minutes']}"
    )
    if s["unknown_models"]:
        lines.append(
            f"Unknown models (cost excluded): {', '.join(s['unknown_models'])}"
        )
    return "\n".join(lines)


def default_project_dir() -> Path:
    slug = str(Path.cwd().resolve()).replace("/", "-").replace(".", "-")
    return Path.home() / ".claude" / "projects" / slug


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--session", required=True)
    ap.add_argument("--project-dir", type=Path, default=None)
    ap.add_argument("--since", type=parse_ts)
    ap.add_argument("--until", type=parse_ts)
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()
    records = load_usage(
        a.project_dir or default_project_dir(), a.session, a.since, a.until
    )
    s = summarize(records)
    print(json.dumps(s, indent=2) if a.format == "json" else to_markdown(s))


if __name__ == "__main__":
    main()
