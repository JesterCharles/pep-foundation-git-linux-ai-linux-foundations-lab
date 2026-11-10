"""Create (or reset) the incident in starter/incident/.

Run from the lab folder:  python tests/setup_lab.py
Re-running it is the reset path: it removes your triage work and deploy.env and
restores the shipped files and the shipped (broken) permissions.
"""

import sys

from lab_support import FIXTURES, INCIDENT, SPACED, TRIAGE, require_posix, reset_starter, write_fixture


def main():
    require_posix()
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 or newer is required. Check `python --version`.")

    if TRIAGE.exists() or (INCIDENT / "env" / "deploy.env").exists():
        print("WARNING: resetting the lab. Triage results and deploy.env are removed.")
    reset_starter()

    # The release manager's folder name contains a space on purpose.
    write_fixture(FIXTURES / "launch-checklist.txt", SPACED / "launch-checklist.txt")
    TRIAGE.mkdir(parents=True, exist_ok=True)

    print("Incident ready in starter/incident/.")
    print("Next: cd starter/incident, then read docs/RUNBOOK.md and run ls -a.")


if __name__ == "__main__":
    main()
