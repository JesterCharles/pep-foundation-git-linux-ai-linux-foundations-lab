"""Remove everything the lab created.

Run from the lab folder:  python test/cleanup_lab.py
It removes triage/, the "release notes" folder, env/deploy.env and the Python
cache in test/, then restores the shipped starter files and permissions.
It touches nothing outside this lab folder.
"""

import sys
from pathlib import Path

# Run as a script (python test/cleanup_lab.py): put the project folder on the import
# path so the shared helpers load as test.lab_support, the name pytest uses.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test.lab_support import reset_starter


def main():
    reset_starter()
    print("Lab cleaned: triage results, the release notes folder and deploy.env are removed.")
    print("The shipped starter files are restored. Run python test/setup_lab.py to start again.")


if __name__ == "__main__":
    main()
