"""Tests for configuration loading."""

import json
from pathlib import Path

from bookmarks_sync.config import load_config, write_config


def test_load_config_uses_obsidian_import_folder_relative_to_vault(tmp_path: Path) -> None:
    """The Obsidian import folder is resolved below the configured vault."""
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "vault_path": str(tmp_path / "Vault"),
                "obsidian_import_folder": "00 Inbox",
                "bookmark_folder": "📥 Obsidian Inbox",
                "poll_interval_minutes": 60,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.vault_path == tmp_path / "Vault"
    assert config.obsidian_import_folder == tmp_path / "Vault" / "00 Inbox"
    assert config.bookmark_folder == "📥 Obsidian Inbox"
    assert config.poll_interval_minutes == 60


def test_write_config_preserves_unicode_as_utf8(tmp_path: Path) -> None:
    """Configuration JSON is written with readable Unicode characters."""
    config_path = tmp_path / "config.json"

    write_config(
        {
            "vault_path": "C:/Vault",
            "obsidian_import_folder": "00 Inbox",
            "bookmark_folder": "📥 Obsidian Inbox",
            "poll_interval_minutes": 60,
        },
        config_path,
    )

    text = config_path.read_text(encoding="utf-8")
    assert "📥 Obsidian Inbox" in text
    assert "\\ud83d" not in text
    assert "\\udce5" not in text
