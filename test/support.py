"""Shared helpers for the "Service will not start" tests.

Every check copies the incident from test/fixtures/incident into a fresh
temporary folder, runs your scripts from src/ there with bash, and then looks
at the result. Nothing ever runs inside this repository.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
INCIDENT_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "incident"

# Task number -> the script that holds that task's commands.
SCRIPTS = {
    1: "task1_checklist.sh",
    2: "task2_triage.sh",
    3: "task3_permissions.sh",
    4: "task4_environment.sh",
    5: "task5_port.sh",
}

HEALTHY_STATUS = "status-page (staging) expects http://localhost:8080/status"


def require_linux():
    """The lab checks Linux permissions and runs bash, so it needs a Linux shell."""
    if os.name != "posix":
        pytest.fail(
            "This lab runs on Linux: permission modes and bash scripts do not work on "
            "Windows file systems. Use the lab's Linux terminal (or WSL)."
        )
    if shutil.which("bash") is None:
        pytest.fail("bash was not found on PATH. The lab needs a bash shell.")


def _copy_text(source, target):
    """Copy a fixture with LF line endings, so counts are the same everywhere."""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes().replace(b"\r\n", b"\n"))


def make_incident(base, log_text=None):
    """Build a fresh copy of the incident under base and return its folder.

    The copy has the shipped (broken) permissions and an empty triage/ folder.
    log_text replaces app/logs/app.log, for checks that use different evidence.
    """
    require_linux()
    incident = Path(base) / "incident"
    for source in INCIDENT_FIXTURE.rglob("*"):
        if source.is_file():
            _copy_text(source, incident / source.relative_to(INCIDENT_FIXTURE))
    if log_text is not None:
        (incident / "app" / "logs" / "app.log").write_text(log_text, encoding="utf-8")
    (incident / "triage").mkdir(exist_ok=True)
    for path in incident.rglob("*"):
        os.chmod(path, 0o755 if path.is_dir() else 0o644)
    os.chmod(incident, 0o755)
    return incident


def clean_env():
    """The test's environment without DEPLOY_ENV, so your shell cannot leak into a check."""
    env = dict(os.environ)
    env.pop("DEPLOY_ENV", None)
    return env


def run_task(task, incident):
    """Run src/<task script> with bash, inside the incident folder."""
    name = SCRIPTS[task]
    script = SRC / name
    if not script.exists():
        pytest.fail(f"Task {task}: src/{name} is missing. Restore it from the starter and add your commands.")
    # Run an LF copy outside the incident folder, so Windows line endings in the
    # editor cannot break bash and the script never shows up in the incident.
    runnable = incident.parent / "scripts" / name
    _copy_text(script, runnable)
    result = subprocess.run(
        ["bash", str(runnable)],
        cwd=incident,
        env=clean_env(),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        pytest.fail(
            f"Task {task}: src/{name} stopped with exit code {result.returncode}. "
            f"bash said: {result.stderr.strip() or '(nothing)'}"
        )
    return result


def run_tasks(incident, *tasks):
    for task in tasks:
        run_task(task, incident)


def read(path):
    return Path(path).read_text(encoding="utf-8")


def lines_of(path):
    return [line.strip() for line in read(path).splitlines() if line.strip()]


def mode_of(path):
    """The permission bits of a path, as an octal string such as 750."""
    return oct(stat.S_IMODE(os.stat(path).st_mode))[2:]


def run_status(incident):
    """Run ./bin/status.sh directly, the way the on-call person does."""
    return subprocess.run(
        ["./bin/status.sh"],
        cwd=incident,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        timeout=30,
    )
