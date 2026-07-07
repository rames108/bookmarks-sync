"""Write Chrome bookmarks as Markdown notes."""

from datetime import datetime
from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark


INVALID_WINDOWS_FILENAME_CHARS = '<>:"/\\|?*'


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


def write_markdown_note(bookmark: Bookmark, obsidian_import_folder: Path) -> Path:
    """Write one bookmark to a Markdown file and return the created path."""
    obsidian_import_folder.mkdir(parents=True, exist_ok=True)
    note_path = _available_note_path(obsidian_import_folder, bookmark.title)
    note_path.write_text(_render_markdown(bookmark), encoding="utf-8")

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


def _available_note_path(folder: Path, title: str) -> Path:
    """Return a non-existing Markdown path for a bookmark title."""
    safe_name = _safe_filename(title)
    path = folder / f"{safe_name}.md"
    counter = 2

    while path.exists():
        path = folder / f"{safe_name} ({counter}).md"
        counter += 1

    return path


def _safe_filename(filename: str) -> str:
    """Replace invalid Windows filename characters while preserving Unicode."""
    safe = "".join(
        "-" if char in INVALID_WINDOWS_FILENAME_CHARS or ord(char) < 32 else char
        for char in filename
    )
    safe = safe.strip().rstrip(".")

    return safe or "Untitled"
