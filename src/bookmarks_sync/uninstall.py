"""Remove the Bookmarks Sync Windows scheduled task."""

from __future__ import annotations

import subprocess

from bookmarks_sync.install import TASK_NAME, task_exists


def main() -> None:
    """Delete the Bookmarks Sync scheduled task if it is installed."""
    if not task_exists():
        print(f'Scheduled task "{TASK_NAME}" is not installed. No changes made.')
        return

    result = uninstall_task()
    if result.returncode == 0:
        print(f'Scheduled task "{TASK_NAME}" removed successfully.')
        return

    print(f'Failed to remove scheduled task "{TASK_NAME}".')
    if result.stderr:
        print(result.stderr.strip())
    elif result.stdout:
        print(result.stdout.strip())


def uninstall_task() -> subprocess.CompletedProcess[str]:
    """Remove the scheduled task using schtasks.exe."""
    return subprocess.run(
        ["schtasks.exe", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True,
        text=True,
        check=False,
    )


if __name__ == "__main__":
    main()
