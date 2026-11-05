import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from require_issue_in_pr import check  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "require_issue_in_pr.py"


def test_non_gh_command_passes():
    assert check("git status", "/tmp") is None


def test_no_issue_is_blocked():
    assert check('gh pr create --title "x" --body "y"', "/tmp")


def test_closes_in_body_passes():
    assert check('gh pr create --title x --body "Closes #77"', "/tmp") is None


def test_refs_in_body_file_passes(tmp_path):
    (tmp_path / "body.md").write_text("Refs #77\n")
    assert check("gh pr create --title x --body-file body.md", str(tmp_path)) is None
    assert check("gh pr create --title x -F body.md", str(tmp_path)) is None


def test_body_file_without_issue_is_blocked(tmp_path):
    (tmp_path / "body.md").write_text("just text\n")
    assert check("gh pr create --body-file=body.md", str(tmp_path))


def test_missing_body_file_is_blocked(tmp_path):
    assert check("gh pr create --body-file nope.md", str(tmp_path))


def test_heredoc_body_passes():
    cmd = (
        "gh pr create --title x --body \"$(cat <<'EOF'\nSummary\n\nFixes #12\nEOF\n)\""
    )
    assert check(cmd, "/tmp") is None


def test_bare_number_is_blocked():
    assert check('gh pr create --body "see #12"', "/tmp")


def test_issue_url_passes():
    cmd = 'gh pr create --body "Closes https://github.com/o/r/issues/5"'
    assert check(cmd, "/tmp") is None


def _run(command, cwd):
    payload = json.dumps({"tool_input": {"command": command}, "cwd": str(cwd)})
    return subprocess.run(
        [sys.executable, str(SCRIPT)], input=payload, capture_output=True, text=True
    )


def test_script_exit_codes(tmp_path):
    blocked = _run('gh pr create --body "nothing"', tmp_path)
    assert blocked.returncode == 2
    assert "gh issue create" in blocked.stderr
    assert _run('gh pr create --body "Closes #77"', tmp_path).returncode == 0
    bad = subprocess.run([sys.executable, str(SCRIPT)], input="not json", text=True)
    assert bad.returncode == 0
