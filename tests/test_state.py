"""Tests for imported bookmark state management."""

import json
from os import PathLike
from pathlib import Path
from typing import Any

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
                    "relative_folder": "Vedabase",
                    "imported_at": "2026-07-06T12:30:00",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    add_imported_bookmark(
        Bookmark(
            title="\U0001f4e5 New",
            url="https://example.com/new",
            relative_folder=Path("Vedabase") / "Bhagavad-gītā",
        ),
        state_path,
    )
    records = load_imported_bookmarks(state_path)

    assert [record.url for record in records] == [
        "https://example.com/old",
        "https://example.com/new",
    ]
    assert records[1].relative_folder == "Vedabase/Bhagavad-gītā"
    assert json.loads(state_path.read_text(encoding="utf-8"))[1].keys() == {
        "url",
        "relative_folder",
        "imported_at",
    }


def test_has_imported_url_detects_existing_url(tmp_path: Path) -> None:
    """Duplicate checks are based on URL."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    add_imported_bookmark(
        Bookmark(title="Title", url="https://example.com"),
        state_path,
    )

    records = load_imported_bookmarks(state_path)

    assert has_imported_url("https://example.com", records)
    assert not has_imported_url("https://example.com/other", records)


def test_load_imported_bookmarks_recovers_invalid_json(
    tmp_path: Path,
    capsys: Any,
) -> None:
    """Invalid state JSON is reset to an empty list with a warning."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    state_path.parent.mkdir()
    state_path.write_text("{not-json", encoding="utf-8")

    assert load_imported_bookmarks(state_path) == []

    assert "Warning: resetting invalid state file" in capsys.readouterr().err
    assert json.loads(state_path.read_text(encoding="utf-8")) == []


def test_load_imported_bookmarks_recovers_empty_state_file(
    tmp_path: Path,
    capsys: Any,
) -> None:
    """An empty state file is reset to an empty JSON list with a warning."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    state_path.parent.mkdir()
    state_path.write_text("", encoding="utf-8")

    assert load_imported_bookmarks(state_path) == []

    assert "Warning: resetting invalid state file" in capsys.readouterr().err
    assert json.loads(state_path.read_text(encoding="utf-8")) == []


def test_interrupted_state_write_leaves_original_json_valid(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """A failed temp-file replace does not corrupt the existing state file."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    state_path.parent.mkdir()
    state_path.write_text(
        json.dumps(
            [
                {
                    "url": "https://example.com/old",
                    "relative_folder": "",
                    "imported_at": "2026-07-06T12:30:00",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    original_json = state_path.read_text(encoding="utf-8")
    original_replace = Path.replace

    def fail_temp_replace(path: Path, target: str | PathLike[str]) -> Path:
        if path.name.startswith("."):
            raise OSError("simulated interrupted write")
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_temp_replace)

    try:
        add_imported_bookmark(
            Bookmark(title="New", url="https://example.com/new"),
            state_path,
        )
    except OSError:
        pass

    assert state_path.read_text(encoding="utf-8") == original_json
    assert [record.url for record in load_imported_bookmarks(state_path)] == [
        "https://example.com/old"
    ]


def test_state_preserves_utf8_relative_folder(tmp_path: Path) -> None:
    """UTF-8 folder names are written and read without mojibake."""
    state_path = tmp_path / "data" / "imported_bookmarks.json"
    relative_folder = Path("Vedabase") / "Bhagavad-gītā"

    add_imported_bookmark(
        Bookmark(
            title="BG 2.13 - Bhagavad-gītā",
            url="https://example.com/bg-2-13",
            relative_folder=relative_folder,
        ),
        state_path,
    )

    raw_state = state_path.read_text(encoding="utf-8")
    records = load_imported_bookmarks(state_path)

    assert "Bhagavad-gītā" in raw_state
    assert "Bhagavad-g\\u012bt\\u0101" not in raw_state
    assert records[0].relative_folder == "Vedabase/Bhagavad-gītā"
