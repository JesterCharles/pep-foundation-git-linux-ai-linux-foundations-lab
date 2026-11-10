"""Remove everything the lab created.

Run from the lab folder:  python tests/cleanup_lab.py
It removes triage/, the "release notes" folder, env/deploy.env and the Python
cache in tests/, then restores the shipped starter files and permissions.
It touches nothing outside this lab folder.
"""

from lab_support import reset_starter


def main():
    reset_starter()
    print("Lab cleaned: triage results, the release notes folder and deploy.env are removed.")
    print("The shipped starter files are restored. Run python tests/setup_lab.py to start again.")


if __name__ == "__main__":
    main()
