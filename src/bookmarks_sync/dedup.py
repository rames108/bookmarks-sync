"""Remove duplicate Markdown notes (same URL, same vault)."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

from bookmarks_sync.config import load_config

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _parse_frontmatter(path: Path) -> dict[str, str]:
    """Extract key: value pairs from a note's YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}

    result: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def dedup(vault_path: Path, dry_run: bool = False) -> list[Path]:
    """Remove duplicate notes (same URL) keeping only the newest.

    Scans ``00 Inbox`` and ``01 Sources`` recursively.

    Returns the list of removed paths.
    """
    folders = [vault_path / "00 Inbox", vault_path / "01 Sources"]
    url_map: dict[str, list[tuple[datetime, Path]]] = {}

    for folder in folders:
        if not folder.is_dir():
            continue
        for md in folder.rglob("*.md"):
            fm = _parse_frontmatter(md)
            url = fm.get("url")
            if not url:
                continue
            raw = fm.get("created", "")
            try:
                ts = datetime.fromisoformat(raw)
            except (ValueError, TypeError):
                ts = datetime.min
            url_map.setdefault(url, []).append((ts, md))

    removed: list[Path] = []
    for url, entries in url_map.items():
        if len(entries) <= 1:
            continue
        entries.sort(key=lambda x: x[0], reverse=True)
        for _, path in entries[1:]:
            removed.append(path)
            if dry_run:
                logger.info("Would remove %s (duplicate of %s)", path.name, entries[0][1].name)
            else:
                path.unlink()
                logger.info("Removed duplicate %s", path.name)

    return removed


def main() -> None:
    """CLI entry point: dedup notes in the configured vault."""
    import argparse

    parser = argparse.ArgumentParser(description="Remove duplicate bookmark notes")
    parser.add_argument("config", nargs="?", default="config.json", help="Path to config.json")
    parser.add_argument("--dry-run", action="store_true", help="Only list duplicates, don't delete")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show info logs")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    config = load_config(Path(args.config))
    removed = dedup(config.vault_path, dry_run=args.dry_run)

    if args.dry_run:
        print(f"Would remove {len(removed)} duplicate note(s).")
    else:
        print(f"Removed {len(removed)} duplicate note(s).")


if __name__ == "__main__":
    main()
