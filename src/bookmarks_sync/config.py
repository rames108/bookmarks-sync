"""Configuration loading for Bookmarks Sync."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Config:
    """Application settings loaded from config.json."""

    vault_path: Path
    obsidian_import_folder: Path
    bookmark_folder: str
    poll_interval_minutes: int


def load_config(config_path: Path = Path("config.json")) -> Config:
    """Load application configuration from a JSON file."""
    data = _read_json(config_path)
    vault_path = Path(str(data["vault_path"]))
    obsidian_import_folder = Path(str(data["obsidian_import_folder"]))
    if not obsidian_import_folder.is_absolute():
        obsidian_import_folder = vault_path / obsidian_import_folder

    return Config(
        vault_path=vault_path,
        obsidian_import_folder=obsidian_import_folder,
        bookmark_folder=str(data["bookmark_folder"]),
        poll_interval_minutes=int(data["poll_interval_minutes"]),
    )


def write_config(data: dict[str, Any], config_path: Path = Path("config.json")) -> None:
    """Write configuration data to disk as UTF-8 JSON."""
    with config_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {path}")

    return data
