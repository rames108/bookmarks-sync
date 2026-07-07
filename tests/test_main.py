"""Tests for the Milestone 4 import flow."""

from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark
from bookmarks_sync.main import import_new_bookmarks
from bookmarks_sync.state import load_imported_bookmarks


def test_import_new_bookmarks_skips_duplicate_urls(tmp_path: Path) -> None:
    """Only bookmarks with URLs absent from state are written as notes."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    notes_path = tmp_path / "Vault" / "00 Inbox"
    bookmarks = [
        Bookmark(title="First", url="https://example.com"),
        Bookmark(title="Duplicate", url="https://example.com"),
        Bookmark(title="Second", url="https://example.com/second"),
    ]

    created_count, skipped_count = import_new_bookmarks(
        bookmarks,
        notes_path,
        state_path,
    )

    assert created_count == 2
    assert skipped_count == 1
    assert (notes_path / "First.md").exists()
    assert not (notes_path / "Duplicate.md").exists()
    assert (notes_path / "Second.md").exists()
    assert [record.url for record in load_imported_bookmarks(state_path)] == [
        "https://example.com",
        "https://example.com/second",
    ]
