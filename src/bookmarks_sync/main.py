"""Command-line entry point for Milestone 2."""

from bookmarks_sync.chrome_reader import read_bookmarks
from bookmarks_sync.config import load_config


def main() -> None:
    """Load config, read Chrome bookmarks, and print the results."""
    config = load_config()
    bookmarks = read_bookmarks(config.bookmark_folder)

    print(f"Found {len(bookmarks)} bookmark(s)")

    for bookmark in bookmarks:
        print()
        print(f"Title: {bookmark.title}")
        print(f"URL: {bookmark.url}")


if __name__ == "__main__":
    main()
