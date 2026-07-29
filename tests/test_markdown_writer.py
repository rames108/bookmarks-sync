"""Tests for Markdown bookmark export."""

from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark
from bookmarks_sync.markdown_writer import write_markdown_notes, write_markdown_note
from bookmarks_sync.scraping.base import ScrapedContent


def test_write_markdown_notes_creates_expected_note(tmp_path: Path) -> None:
    """A bookmark is exported as the V1 inbox Markdown structure."""
    created_paths = write_markdown_notes(
        [Bookmark(title="BG 2.13 - Soul", url="https://example.com/bg-2-13")],
        tmp_path,
    )

    assert created_paths == [tmp_path / "Bookmarks" / "BG 2.13 - Soul.md"]
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

    assert created_paths == [tmp_path / "Bookmarks" / "A -bad- -name- - test-.md"]


def test_write_markdown_notes_preserves_nested_bookmark_folders(
    tmp_path: Path,
) -> None:
    """Chrome folder nesting is mirrored below the Bookmarks import folder."""
    created_paths = write_markdown_notes(
        [
            Bookmark(
                title="BG 2.13",
                url="https://example.com/bg-2-13",
                relative_folder=Path("Vedabase") / "Bhagavad-gita" / "Chapter 2",
            )
        ],
        tmp_path,
    )

    assert created_paths == [
        tmp_path
        / "Bookmarks"
        / "Vedabase"
        / "Bhagavad-gita"
        / "Chapter 2"
        / "BG 2.13.md"
    ]


def test_write_markdown_note_with_enriched_content(tmp_path: Path) -> None:
    """Scraped Vedabase content is rendered into the note body."""
    bookmark = Bookmark(title="Bg 2.13", url="https://vedabase.io/en/library/bg/2/13/")
    content = ScrapedContent(
        source_type="vedabase",
        source_name="Bhagavad-gītā As It Is",
        verse_ref="Bg 2.13",
        devanagari="देहिनोऽस्मिन् यथा देहे",
        verse_text="dehino 'smin yathā dehe",
        synonyms=[("dehinaḥ", "of the embodied"), ("asmin", "in this")],
        translation="As the embodied soul continuously passes...",
        purport="Since every living entity is an individual soul...",
    )

    path = write_markdown_note(bookmark, tmp_path, content)

    note = path.read_text(encoding="utf-8")
    assert "source_type: vedabase" in note
    assert "source_name: Bhagavad-gītā As It Is" in note
    assert "verse: Bg 2.13" in note
    assert "## Devanagari" in note
    assert "देहिनोऽस्मिन् यथा देहे" in note
    assert "## Verse" in note
    assert "dehino 'smin yathā dehe" in note
    assert "## Synonyms" in note
    assert "| dehinaḥ | of the embodied |" in note
    assert "| asmin | in this |" in note
    assert "## Translation" in note
    assert "As the embodied soul continuously passes..." in note
    assert "## Purport" in note
    assert "Since every living entity is an individual soul..." in note
