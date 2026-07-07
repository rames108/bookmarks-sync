"""Tests for imported bookmark state management."""

import json
from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark
from bookmarks_sync.state import (
    add_imported_bookmark,
    ensure_state_file,
    has_imported_url,
    load_imported_bookmarks,
)


def test_ensure_state_file_creates_empty_utf8_json_list(tmp_path: Path) -> None:
    """The state file is created as an empty JSON list."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"

    ensure_state_file(state_path)

    assert json.loads(state_path.read_text(encoding="utf-8")) == []


def test_add_imported_bookmark_preserves_existing_records(tmp_path: Path) -> None:
    """Adding a bookmark appends a state record without discarding old records."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    state_path.parent.mkdir()
    state_path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/old",
                    "title": "Old",
                    "filename": "Old.md",
                    "imported_at": "2026-07-06T12:30:00",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    add_imported_bookmark(
        Bookmark(title="📥 New", url="https://example.com/new"),
        "📥 New.md",
        state_path,
    )
    records = load_imported_bookmarks(state_path)

    assert [record.url for record in records] == [
        "https://example.com/old",
        "https://example.com/new",
    ]
    assert records[1].title == "📥 New"
    assert records[1].filename == "📥 New.md"


def test_has_imported_url_detects_existing_url(tmp_path: Path) -> None:
    """Duplicate checks are based on URL."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    add_imported_bookmark(
        Bookmark(title="Title", url="https://example.com"),
        "Title.md",
        state_path,
    )

    records = load_imported_bookmarks(state_path)

    assert has_imported_url("https://example.com", records)
    assert not has_imported_url("https://example.com/other", records)
