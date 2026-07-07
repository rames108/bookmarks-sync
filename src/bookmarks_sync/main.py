"""Command-line entry point for Milestone 4."""

from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark
from bookmarks_sync.chrome_reader import read_bookmarks
from bookmarks_sync.config import load_config
from bookmarks_sync.markdown_writer import write_markdown_note
from bookmarks_sync.state import (
    DEFAULT_STATE_PATH,
    add_imported_bookmark,
    has_imported_url,
    load_imported_bookmarks,
)


def import_new_bookmarks(
    bookmarks: list[Bookmark],
    obsidian_import_folder: Path,
    state_path: Path = DEFAULT_STATE_PATH,
) -> tuple[int, int]:
    """Import bookmarks that are not already present in state."""
    imported_bookmarks = load_imported_bookmarks(state_path)
    created_count = 0
    skipped_count = 0

    for bookmark in bookmarks:
        if has_imported_url(bookmark.url, imported_bookmarks):
            skipped_count += 1
            continue

        note_path = write_markdown_note(bookmark, obsidian_import_folder)
        record = add_imported_bookmark(bookmark, note_path.name, state_path)
        imported_bookmarks.append(record)
        created_count += 1

    return created_count, skipped_count


def main() -> None:
    """Load config, read Chrome bookmarks, and write new Markdown notes."""
    config = load_config()
    bookmarks = read_bookmarks(config.bookmark_folder)
    created_count, skipped_count = import_new_bookmarks(
        bookmarks,
        config.obsidian_import_folder,
    )

    print(f"Read {len(bookmarks)} bookmarks.")
    print(f"New: {created_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Created {created_count} Markdown notes.")


if __name__ == "__main__":
    main()
