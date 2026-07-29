"""Install Bookmarks Sync as a Windows scheduled task."""

from __future__ import annotations

import subprocess
import sys


TASK_NAME = "Bookmarks Sync"


def main() -> None:
    """Create the Bookmarks Sync scheduled task if it is not installed."""
    if task_exists():
        print(f'Scheduled task "{TASK_NAME}" already exists. No changes made.')
        return

    result = install_task()
    if result.returncode == 0:
        print(f'Scheduled task "{TASK_NAME}" installed successfully.')
        print("It will run every 1 hour.")
        return

    print(f'Failed to install scheduled task "{TASK_NAME}".')
    if result.stderr:
        print(result.stderr.strip())
    elif result.stdout:
        print(result.stdout.strip())


def task_exists() -> bool:
    """Return whether the scheduled task already exists."""
    result = subprocess.run(
        ["schtasks.exe", "/Query", "/TN", TASK_NAME],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def install_task() -> subprocess.CompletedProcess[str]:
    """Install the scheduled task using schtasks.exe."""
    return subprocess.run(
        [
            "schtasks.exe",
            "/Create",
            "/TN",
            TASK_NAME,
            "/SC",
            "HOURLY",
            "/MO",
            "1",
            "/TR",
            build_task_command(),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def build_task_command() -> str:
    """Build the command executed by the scheduled task."""
    return f'"{sys.executable}" -m bookmarks_sync.main'


if __name__ == "__main__":
    main()
