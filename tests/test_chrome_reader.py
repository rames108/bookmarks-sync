"""Tests for reading Chrome bookmark folder hierarchies."""

import json
from pathlib import Path

from bookmarks_sync.chrome_reader import Bookmark, read_bookmarks


def test_read_bookmarks_preserves_three_level_relative_folder_path(
    tmp_path: Path,
) -> None:
    """Nested folders below the configured Chrome folder are kept on bookmarks."""
    bookmarks_path = tmp_path / "Bookmarks"
    bookmark_folder = "\U0001f4e5 Obsidian Inbox"
    bookmarks_path.write_text(
        json.dumps(
            {
                "roots": {
                    "bookmark_bar": {
                        "type": "folder",
                        "name": "Bookmarks Bar",
                        "children": [
                            {
                                "type": "folder",
                                "name": bookmark_folder,
                                "children": [
                                    {
                                        "type": "folder",
                                        "name": "Vedabase",
                                        "children": [
                                            {
                                                "type": "folder",
                                                "name": "Bhagavad-gita",
                                                "children": [
                                                    {
                                                        "type": "folder",
                                                        "name": "Chapter 2",
                                                        "children": [
                                                            {
                                                                "type": "url",
                                                                "name": "BG 2.13 - Bhagavad-g\u012bt\u0101",
                                                                "url": "https://example.com/bg-2-13",
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                }
            },
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )

    assert read_bookmarks(bookmark_folder, bookmarks_path) == [
        Bookmark(
            title="BG 2.13 - Bhagavad-g\u012bt\u0101",
            url="https://example.com/bg-2-13",
            relative_folder=Path("Vedabase") / "Bhagavad-gita" / "Chapter 2",
        )
    ]
