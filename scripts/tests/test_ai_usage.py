import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_usage import load_usage, summarize  # noqa: E402

SID = "sess"


def line(mid, ts="2026-10-28T10:00:00.000Z", model="claude-opus-5-5", **usage):
    u = {"input_tokens": 0, "output_tokens": 0}
    u.update(usage)
    return json.dumps(
        {
            "type": "assistant",
            "timestamp": ts,
            "message": {"id": mid, "model": model, "usage": u},
        }
    )


def write(path: Path, *lines: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def test_dedupe_by_message_id(tmp_path):
    write(
        tmp_path / f"{SID}.jsonl", line("a", input_tokens=5), line("a", input_tokens=5)
    )
    recs = load_usage(tmp_path, SID)
    assert len(recs) == 1
    assert summarize(recs)["total"]["input"] == 5


def test_time_window(tmp_path):
    write(
        tmp_path / f"{SID}.jsonl",
        line("a", ts="2026-10-28T09:00:00Z"),
        line("b", ts="2026-10-28T10:00:00Z"),
        line("c", ts="2026-10-28T11:00:00Z"),
    )
    since = datetime(2026, 10, 28, 10, tzinfo=timezone.utc)
    until = datetime(2026, 10, 28, 11, tzinfo=timezone.utc)
    recs = load_usage(tmp_path, SID, since, until)
    assert [r["id"] for r in recs] == ["b"]


def test_subagents_included_meta_ignored(tmp_path):
    write(tmp_path / f"{SID}.jsonl", line("a", output_tokens=1))
    write(tmp_path / SID / "subagents" / "x.jsonl", line("b", output_tokens=2))
    (tmp_path / SID / "subagents" / "x.meta.json").write_text(
        line("c", output_tokens=100)
    )
    assert summarize(load_usage(tmp_path, SID))["total"]["output"] == 3


def test_cost_exact_opus(tmp_path):
    write(
        tmp_path / f"{SID}.jsonl",
        line(
            "a",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            cache_read_input_tokens=1_000_000,
            cache_creation_input_tokens=1_000_000,
            cache_creation={
                "ephemeral_5m_input_tokens": 500_000,
                "ephemeral_1h_input_tokens": 500_000,
            },
        ),
    )
    s = summarize(load_usage(tmp_path, SID))
    # 4 + 20 + 0.2 + 0.5M*5 (2.5) + 0.5M*8 (4) = 30.7
    assert s["total"]["cost_usd"] == 30.7
    assert s["models"]["claude-opus-5-5"]["total_tokens"] == 4_000_000


def test_unknown_model_counted_no_cost(tmp_path):
    write(tmp_path / f"{SID}.jsonl", line("a", model="claude-mystery", input_tokens=7))
    s = summarize(load_usage(tmp_path, SID))
    assert s["unknown_models"] == ["claude-mystery"]
    assert s["total"]["input"] == 7
    assert s["total"]["cost_usd"] == 0.0


def test_malformed_and_synthetic_skipped(tmp_path):
    write(
        tmp_path / f"{SID}.jsonl",
        "{not json",
        line("s", model="<synthetic>", input_tokens=9),
        line("a", input_tokens=1),
    )
    assert summarize(load_usage(tmp_path, SID))["total"]["requests"] == 1


def test_5m_fallback_without_cache_creation(tmp_path):
    write(tmp_path / f"{SID}.jsonl", line("a", cache_creation_input_tokens=42))
    t = summarize(load_usage(tmp_path, SID))["total"]
    assert t["cache_write_5m"] == 42
    assert t["cache_write_1h"] == 0
