"""Read bookmarks from Google Chrome's Bookmarks JSON file."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Bookmark:
    """A single Chrome bookmark."""

    title: str
    url: str
    relative_folder: Path = Path()


def read_bookmarks(
    bookmark_folder: str,
    bookmarks_path: Path | None = None,
) -> list[Bookmark]:
    """Return bookmarks contained in the configured Chrome bookmark folder."""
    path = bookmarks_path or get_default_bookmarks_path()

    if not path.exists():
        return []

    data = _read_json(path)
    folder = _find_folder(data, bookmark_folder)
    if folder is None:
        return []

    return _collect_bookmarks(folder)


def get_default_bookmarks_path() -> Path:
    """Return the default Chrome Bookmarks path for the current Windows user."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return Path()

    return (
        Path(local_app_data)
        / "Google"
        / "Chrome"
        / "User Data"
        / "Default"
        / "Bookmarks"
    )


def _read_json(path: Path) -> dict[str, Any]:
    """Read Chrome's Bookmarks JSON object from disk."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {}

    return data


def _find_folder(node: Any, folder_name: str) -> dict[str, Any] | None:
    """Recursively find the first folder with an exact matching name."""
    if isinstance(node, dict):
        if node.get("type") == "folder" and node.get("name") == folder_name:
            return node

        for value in node.values():
            folder = _find_folder(value, folder_name)
            if folder is not None:
                return folder

    if isinstance(node, list):
        for item in node:
            folder = _find_folder(item, folder_name)
            if folder is not None:
                return folder

    return None


def _collect_bookmarks(
    folder: dict[str, Any],
    relative_folder: Path = Path(),
) -> list[Bookmark]:
    """Collect bookmarks from a matched folder and its child folders only."""
    bookmarks: list[Bookmark] = []

    for child in folder.get("children", []):
        if not isinstance(child, dict):
            continue

        if child.get("type") == "url":
            title = child.get("name")
            url = child.get("url")
            if isinstance(title, str) and isinstance(url, str):
                bookmarks.append(
                    Bookmark(
                        title=title,
                        url=url,
                        relative_folder=relative_folder,
                    )
                )

        if child.get("type") == "folder":
            folder_name = child.get("name")
            if isinstance(folder_name, str):
                bookmarks.extend(
                    _collect_bookmarks(child, relative_folder / folder_name)
                )

    return bookmarks
