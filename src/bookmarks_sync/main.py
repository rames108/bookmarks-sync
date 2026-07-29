"""Command-line entry point for Milestone 4."""

import logging
from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark
from bookmarks_sync.chrome_reader import read_bookmarks
from bookmarks_sync.config import load_config
from bookmarks_sync.markdown_writer import write_markdown_note
from bookmarks_sync.scraping import scrape as try_scrape
from bookmarks_sync.state import (
    DEFAULT_STATE_PATH,
    add_imported_bookmark,
    has_imported_url,
    load_imported_bookmarks,
)

logger = logging.getLogger(__name__)

SOURCES_FOLDER = "01 Sources"
INVALID_FOLDER_CHARS = '<>:"/\\|?*'


def _safe_folder(name: str) -> str:
    """Sanitize a folder name for Windows."""
    safe = "".join(
        "-" if char in INVALID_FOLDER_CHARS or ord(char) < 32 else char
        for char in name
    )
    safe = safe.strip().rstrip(".")
    return safe or "Untitled Source"


def import_new_bookmarks(
    bookmarks: list[Bookmark],
    obsidian_import_folder: Path,
    vault_path: Path,
    state_path: Path = DEFAULT_STATE_PATH,
) -> tuple[int, int]:
    """Import bookmarks that are not already present in state.

    Scraped bookmarks go to ``<vault_path>/01 Sources/<source_name>/``.

    Plain bookmarks go to ``<obsidian_import_folder>/Bookmarks/…``.
    """
    imported_bookmarks = load_imported_bookmarks(state_path)
    created_count = 0
    skipped_count = 0

    for bookmark in bookmarks:
        if has_imported_url(bookmark.url, imported_bookmarks):
            skipped_count += 1
            continue

        content = try_scrape(bookmark.url)
        if content:
            logger.info("Scraped content for %s (%s)", bookmark.url, content.source_type)

        if content and content.source_name:
            output_dir = vault_path / SOURCES_FOLDER / _safe_folder(content.source_name)
        else:
            output_dir = obsidian_import_folder

        write_markdown_note(bookmark, output_dir, content)
        record = add_imported_bookmark(bookmark, state_path)
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
        config.vault_path,
    )

    print(f"Read {len(bookmarks)} bookmarks.")
    print(f"New: {created_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Created {created_count} Markdown notes.")


if __name__ == "__main__":
    main()
