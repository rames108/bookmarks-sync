"""Tests for the duplicate-removal module."""

from pathlib import Path

from bookmarks_sync.dedup import dedup, _parse_frontmatter


def test_parse_frontmatter_extracts_url(tmp_path: Path) -> None:
    md = tmp_path / "note.md"
    md.write_text(
        "---\n"
        "type: inbox\n"
        "url: https://example.com\n"
        "created: 2026-07-28T12:00:00\n"
        "---\n"
        "\n"
        "# Title\n"
    )
    fm = _parse_frontmatter(md)
    assert fm["url"] == "https://example.com"
    assert fm["created"] == "2026-07-28T12:00:00"


def test_parse_frontmatter_returns_empty_for_no_frontmatter(tmp_path: Path) -> None:
    md = tmp_path / "note.md"
    md.write_text("# Just a heading\n\nNo frontmatter here.")
    assert _parse_frontmatter(md) == {}


def test_dedup_keeps_newest(tmp_path: Path) -> None:
    folder = tmp_path / "00 Inbox"
    folder.mkdir(parents=True)
    old = folder / "old.md"
    old.write_text(
        "---\n"
        "url: https://example.com/a\n"
        "created: 2026-07-01T12:00:00\n"
        "---\n"
    )
    new = folder / "new.md"
    new.write_text(
        "---\n"
        "url: https://example.com/a\n"
        "created: 2026-07-28T12:00:00\n"
        "---\n"
    )

    removed = dedup(tmp_path)
    assert len(removed) == 1
    assert old.exists() is False
    assert new.exists() is True


def test_dedup_does_not_touch_singletons(tmp_path: Path) -> None:
    folder = tmp_path / "01 Sources" / "Bhagavad-gita"
    folder.mkdir(parents=True)
    note = folder / "verse.md"
    note.write_text(
        "---\n"
        "url: https://example.com/unique\n"
        "created: 2026-07-28T12:00:00\n"
        "---\n"
    )

    removed = dedup(tmp_path)
    assert removed == []
    assert note.exists()


def test_dedup_respects_dry_run(tmp_path: Path) -> None:
    folder = tmp_path / "00 Inbox"
    folder.mkdir(parents=True)
    old = folder / "old.md"
    old.write_text(
        "---\n"
        "url: https://example.com/a\n"
        "created: 2026-07-01T12:00:00\n"
        "---\n"
    )
    new = folder / "new.md"
    new.write_text(
        "---\n"
        "url: https://example.com/a\n"
        "created: 2026-07-28T12:00:00\n"
        "---\n"
    )

    removed = dedup(tmp_path, dry_run=True)
    assert len(removed) == 1
    assert old.exists()
    assert new.exists()
