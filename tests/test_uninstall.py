"""Tests for Windows scheduled task uninstall helpers."""

from unittest.mock import patch

from bookmarks_sync.uninstall import uninstall_task


def test_uninstall_task_uses_schtasks_delete() -> None:
    """Uninstall removes the scheduled task by name."""
    with patch("bookmarks_sync.uninstall.subprocess.run") as run:
        uninstall_task()

    run.assert_called_once_with(
        ["schtasks.exe", "/Delete", "/TN", "Bookmarks Sync", "/F"],
        capture_output=True,
        text=True,
        check=False,
    )
