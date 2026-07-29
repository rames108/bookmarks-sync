"""Tests for Windows scheduled task installation helpers."""

from unittest.mock import patch

from bookmarks_sync.install import TASK_NAME, build_task_command, install_task


def test_build_task_command_runs_main_with_current_python() -> None:
    """The generated task command launches the package entry point with Python."""
    with patch("bookmarks_sync.install.sys.executable", "C:\\Project\\.venv\\Scripts\\python.exe"):
        command = build_task_command()

    assert command == '"C:\\Project\\.venv\\Scripts\\python.exe" -m bookmarks_sync.main'


def test_install_task_uses_schtasks_hourly_schedule() -> None:
    """Install creates an hourly scheduled task directly with schtasks arguments."""
    with patch("bookmarks_sync.install.subprocess.run") as run:
        with patch(
            "bookmarks_sync.install.sys.executable",
            "C:\\Project\\.venv\\Scripts\\python.exe",
        ):
            install_task()

    run.assert_called_once_with(
        [
            "schtasks.exe",
            "/Create",
            "/TN",
            "Bookmarks Sync",
            "/SC",
            "HOURLY",
            "/MO",
            "1",
            "/TR",
            '"C:\\Project\\.venv\\Scripts\\python.exe" -m bookmarks_sync.main',
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_task_name_matches_requirement() -> None:
    """The scheduled task name is stable."""
    assert TASK_NAME == "Bookmarks Sync"
