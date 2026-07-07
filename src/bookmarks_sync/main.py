"""Command-line entry point for Milestone 3."""

from bookmarks_sync.chrome_reader import read_bookmarks
from bookmarks_sync.config import load_config
from bookmarks_sync.markdown_writer import write_markdown_notes


def main() -> None:
    """Load config, read Chrome bookmarks, and write Markdown notes."""
    config = load_config()
    bookmarks = read_bookmarks(config.bookmark_folder)
    created_paths = write_markdown_notes(bookmarks, config.obsidian_import_folder)

    for path in created_paths:
        print("Created:")
        print(path.name)
        print()

    print(f"Created {len(created_paths)} Markdown notes.")


if __name__ == "__main__":
    main()
