import re
from pathlib import Path

from streamlit.testing.v1 import AppTest
from utils import apis
from utils.constants import ERROR_REQUEST

CLIENT = Path(__file__).parents[1]
# Split literals so the issue's `grep -r ... client` does not match this file.
STALE = re.compile(
    "|".join(
        ["hi@" + r"ecommerce\.com", "0905 89 " + "86 83", "Monday to " + "Saturday"]
    )
)
SKIP_DIRS = {"tests", ".venv", "__pycache__", ".pytest_cache", ".streamlit-cache"}


def client_files():
    for p in CLIENT.rglob("*"):
        if p.is_file() and not SKIP_DIRS & set(p.relative_to(CLIENT).parts):
            yield p


def test_no_stale_contacts_in_client():
    hits = []
    for p in client_files():
        try:
            text = p.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        if STALE.search(text):
            hits.append(str(p.relative_to(CLIENT)))
    assert hits == []


def test_sidebar_shows_ivy_moda_contacts(monkeypatch):
    monkeypatch.chdir(CLIENT)
    monkeypatch.setattr(apis, "health_check", lambda: None)
    at = AppTest.from_file(str(CLIENT / "app.py"), default_timeout=30)
    at.run()
    sidebar = "\n".join(m.value for m in at.sidebar.markdown)
    for expected in (
        "CSKH@ivy.com.vn",
        "0246 662 3434",
        "Monday to Friday",
        "IVY moda",
    ):
        assert expected in sidebar


def test_request_error_has_ivy_contacts():
    assert "CSKH@ivy.com.vn" in ERROR_REQUEST
    assert "0246 662 3434" in ERROR_REQUEST


def test_about_us_is_ivy_moda_apparel_only():
    text = (CLIENT / "assets" / "docs" / "about.md").read_text()
    assert "IVY moda" in text
    low = text.lower()
    for banned in ("accessor", "lingerie", "ecommerce platform"):
        assert banned not in low
