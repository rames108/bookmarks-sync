"""Configuration loading for Bookmarks Sync."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Config:
    """Application settings loaded from config.json."""

    vault_path: Path
    inbox_folder: str
    bookmark_folder: str
    poll_interval_minutes: int


def load_config(config_path: Path = Path("config.json")) -> Config:
    """Load application configuration from a JSON file."""
    data = _read_json(config_path)

    return Config(
        vault_path=Path(str(data["vault_path"])),
        inbox_folder=str(data["inbox_folder"]),
        bookmark_folder=str(data["bookmark_folder"]),
        poll_interval_minutes=int(data["poll_interval_minutes"]),
    )


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {path}")

    return data
