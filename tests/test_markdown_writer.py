"""Tests for Markdown bookmark export."""

from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark
from bookmarks_sync.markdown_writer import write_markdown_notes


def test_write_markdown_notes_creates_expected_note(tmp_path: Path) -> None:
    """A bookmark is exported as the V1 inbox Markdown structure."""
    created_paths = write_markdown_notes(
        [Bookmark(title="BG 2.13 - Soul", url="https://example.com/bg-2-13")],
        tmp_path,
    )

    assert created_paths == [tmp_path / "BG 2.13 - Soul.md"]
    note = created_paths[0].read_text(encoding="utf-8")
    assert note.startswith(
        "---\n"
        "type: inbox\n"
        "source: chrome-bookmark\n"
        "processed: false\n"
        "\n"
        "url: https://example.com/bg-2-13\n"
        "\n"
        "created: "
    )
    assert note.endswith(
        "---\n"
        "\n"
        "# BG 2.13 - Soul\n"
        "\n"
        "## URL\n"
        "\n"
        "https://example.com/bg-2-13\n"
        "\n"
        "## Notes\n"
        "\n"
    )


def test_write_markdown_notes_sanitizes_invalid_windows_filename_chars(
    tmp_path: Path,
) -> None:
    """Invalid Windows filename characters are replaced before writing."""
    created_paths = write_markdown_notes(
        [Bookmark(title='A <bad> "name" / test?', url="https://example.com")],
        tmp_path,
    )

    assert created_paths == [tmp_path / "A -bad- -name- - test-.md"]
