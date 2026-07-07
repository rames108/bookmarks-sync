"""State management for imported bookmarks."""

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from bookmarks_sync.chrome_reader import Bookmark


DEFAULT_STATE_PATH = Path("data") / "imported_bookmarks.json"


@dataclass(frozen=True)
class ImportedBookmark:
    """A bookmark that has already been imported."""

    url: str
    title: str
    filename: str
    imported_at: str


def ensure_state_file(state_path: Path = DEFAULT_STATE_PATH) -> None:
    """Create the imported bookmarks state file if it does not exist."""
    if state_path.exists():
        return

    state_path.parent.mkdir(parents=True, exist_ok=True)
    _safe_write_json(state_path, [])


def load_imported_bookmarks(
    state_path: Path = DEFAULT_STATE_PATH,
) -> list[ImportedBookmark]:
    """Load imported bookmark records from the state file."""
    ensure_state_file(state_path)

    with state_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        return []

    records: list[ImportedBookmark] = []
    for item in data:
        if not isinstance(item, dict):
            continue

        record = _record_from_json(item)
        if record is not None:
            records.append(record)

    return records


def has_imported_url(url: str, records: list[ImportedBookmark]) -> bool:
    """Return whether a URL is already present in the imported state."""
    return any(record.url == url for record in records)


def add_imported_bookmark(
    bookmark: Bookmark,
    filename: str,
    state_path: Path = DEFAULT_STATE_PATH,
) -> ImportedBookmark:
    """Append an imported bookmark record and safely persist the state file."""
    records = load_imported_bookmarks(state_path)
    record = ImportedBookmark(
        url=bookmark.url,
        title=bookmark.title,
        filename=filename,
        imported_at=datetime.now().replace(microsecond=0).isoformat(),
    )
    records.append(record)
    _safe_write_json(state_path, [asdict(item) for item in records])

    return record


def _record_from_json(item: dict[str, Any]) -> ImportedBookmark | None:
    """Convert a JSON object into an imported bookmark record."""
    url = item.get("url")
    title = item.get("title")
    filename = item.get("filename")
    imported_at = item.get("imported_at")

    if not all(isinstance(value, str) for value in (url, title, filename, imported_at)):
        return None

    return ImportedBookmark(
        url=url,
        title=title,
        filename=filename,
        imported_at=imported_at,
    )


def _safe_write_json(path: Path, data: list[dict[str, str]] | list[Any]) -> None:
    """Write JSON through a temporary file before replacing the state file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

    temp_path.replace(path)
