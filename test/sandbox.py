"""Make a practice copy of the incident, outside this repository.

Run from the project folder:  python -m test.sandbox

It prints the folder to cd into. Try your commands there, then put them in
your scripts in src/. Each run makes a brand-new copy, so a fresh start is one
command away. The tests never look at the practice copy.
"""

import tempfile
from pathlib import Path

from test.support import SRC, make_incident


def main():
    base = Path(tempfile.mkdtemp(prefix="incident-practice-"))
    incident = make_incident(base)
    print(f"Practice incident ready in {incident}")
    print(f"  cd {incident}")
    print("Try your commands there. To run one of your scripts on the copy:")
    print(f"  bash {SRC / 'task2_triage.sh'}")
    print("Run python -m test.sandbox again for a fresh copy.")


if __name__ == "__main__":
    main()
