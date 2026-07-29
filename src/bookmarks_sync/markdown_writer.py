"""Write Chrome bookmarks as Markdown notes."""

from datetime import datetime
from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark
from bookmarks_sync.scraping.base import ScrapedContent


INVALID_WINDOWS_FILENAME_CHARS = '<>:"/\\|?*'
BOOKMARKS_FOLDER = "Bookmarks"
MAX_FILENAME_LENGTH = 100


def write_markdown_notes(
    bookmarks: list[Bookmark],
    obsidian_import_folder: Path,
) -> list[Path]:
    """Write bookmarks to Markdown files and return created paths."""
    obsidian_import_folder.mkdir(parents=True, exist_ok=True)

    created_paths: list[Path] = []
    for bookmark in bookmarks:
        created_paths.append(write_markdown_note(bookmark, obsidian_import_folder))

    return created_paths


def write_markdown_note(
    bookmark: Bookmark,
    output_dir: Path,
    content: ScrapedContent | None = None,
) -> Path:
    """Write one bookmark to a Markdown file and return the created path.

    When *content* is provided (scraped), the note is written directly into
    *output_dir* (typically ``01 Sources/<source_name>/``).

    When *content* is ``None`` (plain bookmark), the note is placed under
    ``<output_dir>/Bookmarks/<relative_folder>/``, preserving the Chrome
    folder hierarchy.
    """
    if content:
        note_folder = output_dir
    else:
        note_folder = output_dir / BOOKMARKS_FOLDER / bookmark.relative_folder

    note_folder.mkdir(parents=True, exist_ok=True)
    note_path = _available_note_path(note_folder, bookmark.title)

    # Ensure the immediate parent folder exists right before writing.
    # This prevents sporadic FileNotFoundError when nested folders are required.
    note_path.parent.mkdir(parents=True, exist_ok=True)
    md = _render_enriched(bookmark, content) if content else _render_markdown(bookmark)
    note_path.write_text(md, encoding="utf-8")

    return note_path


def _render_markdown(bookmark: Bookmark) -> str:
    """Render a bookmark as the required Markdown note structure."""
    created = datetime.now().replace(microsecond=0).isoformat()

    return (
        "---\n"
        "type: inbox\n"
        "source: chrome-bookmark\n"
        "processed: false\n"
        "\n"
        f"url: {bookmark.url}\n"
        "\n"
        f"created: {created}\n"
        "---\n"
        "\n"
        f"# {bookmark.title}\n"
        "\n"
        "## URL\n"
        "\n"
        f"{bookmark.url}\n"
        "\n"
        "## Notes\n"
        "\n"
    )


def _render_enriched(bookmark: Bookmark, content: ScrapedContent) -> str:
    """Render a bookmark with scraped Vedabase content."""
    created = datetime.now().replace(microsecond=0).isoformat()

    lines: list[str] = [
        "---",
        "type: inbox",
        "source: chrome-bookmark",
        f"source_type: {content.source_type}",
        "processed: false",
        "",
    ]
    if content.source_name:
        lines.append(f"source_name: {content.source_name}")
    if content.verse_ref:
        lines.append(f"verse: {content.verse_ref}")
    lines.extend([
        "",
        f"url: {bookmark.url}",
        "",
        f"created: {created}",
        "---",
        "",
        f"# {bookmark.title}",
        "",
    ])

    if content.devanagari:
        lines.extend(["## Devanagari", "", content.devanagari, ""])

    if content.verse_text:
        lines.extend(["## Verse", "", content.verse_text, ""])

    if content.synonyms:
        lines.extend(["## Synonyms", "", "| Sanskrit | Meaning |", "|---|---|"])
        for sk, en in content.synonyms:
            sk_escaped = sk.replace("|", "\\|")
            en_escaped = en.replace("|", "\\|")
            lines.append(f"| {sk_escaped} | {en_escaped} |")
        lines.append("")

    if content.translation:
        lines.extend(["## Translation", "", content.translation, ""])

    if content.purport:
        lines.extend(["## Purport", "", content.purport, ""])

    if content.body_text:
        excerpt = _excerpt_around_match(content.body_text, bookmark.title)
        lines.extend(["## Content", "", excerpt, ""])

    lines.extend([
        "## URL",
        "",
        bookmark.url,
        "",
        "## Notes",
        "",
    ])

    return "\n".join(lines)


def _available_note_path(folder: Path, title: str) -> Path:
    """Return a non-existing Markdown path for a bookmark title."""
    safe_name = _safe_filename(title)
    path = folder / f"{safe_name}.md"
    counter = 2

    while path.exists():
        path = folder / f"{safe_name} ({counter}).md"
        counter += 1

    return path


def _excerpt_around_match(text: str, query: str, context: int = 2) -> str:
    """Extract paragraphs around a matching query, or return full text if no match."""
    paragraphs = text.split("\n\n")
    query_lower = query.lower()
    query_words = [w for w in query_lower.split() if len(w) > 2]

    for i, para in enumerate(paragraphs):
        if query_lower in para.lower():
            start = max(0, i - context)
            end = min(len(paragraphs), i + context + 1)
            return "\n\n".join(paragraphs[start:end])

    for word in query_words:
        for i, para in enumerate(paragraphs):
            if word in para.lower():
                start = max(0, i - context)
                end = min(len(paragraphs), i + context + 1)
                return "\n\n".join(paragraphs[start:end])

    return text


def _safe_filename(filename: str) -> str:
    """Replace invalid Windows filename characters while preserving Unicode."""
    safe = "".join(
        "-" if char in INVALID_WINDOWS_FILENAME_CHARS or ord(char) < 32 else char
        for char in filename
    )
    safe = safe.strip().rstrip(".")
    safe = safe[:MAX_FILENAME_LENGTH]

    return safe or "Untitled"
