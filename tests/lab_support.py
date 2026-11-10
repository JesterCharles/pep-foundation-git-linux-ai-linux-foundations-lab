"""Shared paths and helpers for the "Service will not start" lab.

Standard library only.
"""

import os
import shutil
import stat
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = LAB_ROOT / "fixtures"
STARTER = LAB_ROOT / "starter"
INCIDENT = STARTER / "incident"
SPACED = INCIDENT / "release notes"
TRIAGE = INCIDENT / "triage"

# Shipped starter files and the fixture each one restores from.
SHIPPED = [
    ("app/logs/app.log", "incident/app.log"),
    ("app/config/app.conf", "incident/app.conf"),
    ("docs/RUNBOOK.md", "incident/RUNBOOK.md"),
    ("bin/status.sh", "incident/status.sh"),
    ("env/deploy.env.example", "incident/deploy.env.example"),
]

# Paths created by setup or by the learner; reset and cleanup remove them.
CREATED_PATHS = [
    SPACED,
    TRIAGE,
    INCIDENT / "env" / "deploy.env",
    LAB_ROOT / "tests" / "__pycache__",
]


def inside(path, parent):
    """True when path resolves to parent or somewhere below it."""
    resolved = Path(path).resolve()
    base = Path(parent).resolve()
    return resolved == base or base in resolved.parents


def remove(path):
    """Remove a lab-created path after confirming it is inside the starter or tests folder."""
    path = Path(path)
    if not (inside(path, STARTER) or inside(path, LAB_ROOT / "tests")):
        raise RuntimeError(f"refusing to remove {path}: outside the lab")
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def write_fixture(source, target):
    """Copy fixture text with LF line endings so grep counts are identical everywhere."""
    data = Path(source).read_bytes().replace(b"\r\n", b"\n")
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    Path(target).write_bytes(data)


def restore_starter_files():
    """Write the shipped starter bytes and the shipped (broken) permissions."""
    for local, fixture in SHIPPED:
        write_fixture(FIXTURES / fixture, INCIDENT / local)
    # The incident: the script is not executable, which is part of what the learner fixes.
    os.chmod(INCIDENT / "bin" / "status.sh", 0o644)
    os.chmod(INCIDENT / "env" / "deploy.env.example", 0o644)


def reset_starter():
    """Remove learner-created paths and restore the shipped files."""
    for path in CREATED_PATHS:
        remove(path)
    restore_starter_files()


def mode_of(path):
    """The permission bits of a path, as an octal string such as 750."""
    return oct(stat.S_IMODE(os.stat(path).st_mode))[2:]


def require_posix():
    if os.name != "posix":
        sys.exit(
            "This lab needs a Linux or macOS shell. On Windows, open an Ubuntu (WSL) "
            "terminal and run the lab from there."
        )
