"""State management for imported bookmarks."""

from dataclasses import asdict, dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from typing import Any

from bookmarks_sync.chrome_reader import Bookmark


DEFAULT_STATE_PATH = Path("data") / "imported_bookmarks.json"


@dataclass(frozen=True)
class ImportedBookmark:
    """A bookmark that has already been imported."""

    url: str
    relative_folder: str
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

    data = _read_state_json(state_path)

    if not isinstance(data, list):
        _warn_and_reset_state(state_path)
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
    state_path: Path = DEFAULT_STATE_PATH,
) -> ImportedBookmark:
    """Append an imported bookmark record and safely persist the state file."""
    records = load_imported_bookmarks(state_path)
    record = ImportedBookmark(
        url=bookmark.url,
        relative_folder=bookmark.relative_folder.as_posix(),
        imported_at=datetime.now().replace(microsecond=0).isoformat(),
    )
    records.append(record)
    _safe_write_json(state_path, [asdict(item) for item in records])

    return record


def _record_from_json(item: dict[str, Any]) -> ImportedBookmark | None:
    """Convert a JSON object into an imported bookmark record."""
    url = item.get("url")
    relative_folder = item.get("relative_folder", "")
    imported_at = item.get("imported_at")

    if not all(isinstance(value, str) for value in (url, relative_folder, imported_at)):
        return None

    return ImportedBookmark(
        url=url,
        relative_folder=relative_folder,
        imported_at=imported_at,
    )


def _read_state_json(path: Path) -> Any:
    """Read state JSON, recovering from empty or invalid files."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError):
        _warn_and_reset_state(path)
        return []


def _warn_and_reset_state(path: Path) -> None:
    """Reset a corrupt state file to an empty JSON list."""
    print(f"Warning: resetting invalid state file: {path}", file=sys.stderr)
    _safe_write_json(path, [])


def _safe_write_json(path: Path, data: list[dict[str, str]] | list[Any]) -> None:
    """Write JSON through a flushed temporary file before replacing state.

    Atomicity requirements:
    - write -> flush -> fsync -> replace

    Windows note:
    - the target file may be briefly locked by another process.
    - keep atomic replace behavior, but add a short retry loop around replace.
    """

    import time

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())

    # Ensure the temp file handle is fully closed before attempting replace().
    retries = 5
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            temp_path.replace(path)
            return
        except PermissionError as exc:
            last_exc = exc
            if attempt >= retries:
                break
            time.sleep(0.05)
        except OSError as exc:
            # WinError 5: Access is denied.
            winerror = getattr(exc, "winerror", None)
            if winerror != 5:
                raise
            last_exc = exc
            if attempt >= retries:
                break
            time.sleep(0.05)

    if last_exc is not None:
        raise last_exc

