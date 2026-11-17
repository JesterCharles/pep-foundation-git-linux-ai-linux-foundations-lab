# Linux Foundations lab: service will not start

A small service called `status-page` is unhealthy, and the on-call teammate left a
folder of evidence. You use the Linux shell to work the incident:
- copy a file out of a folder whose name contains a space;
- find the real errors in a log with pipes and `grep`;
- fix a file permission with `chmod`;
- set an environment variable with `export` and a settings file;
- fix the port mismatch behind `connection refused`.

The service never actually runs: all the evidence is in files, and 8 checks read
the files and permissions you leave behind.

The full learner instructions are in [`.evolv/instructions.md`](.evolv/instructions.md), which the lab platform shows as the lab's instructions.

## Layout

This repository follows the Exa coding-lab scaffold for Python.

| Path | What it is |
|---|---|
| `src/incident/` | The incident folder the learner works in |
| `test/test_incident.py` | Visible checks |
| `test/setup_lab.py` | Creates (or resets) the incident |
| `test/cleanup_lab.py` | Removes what setup and the learner created |
| `test/lab_support.py` | Paths and helpers the scripts and checks share |
| `test/conftest.py` | Counts a check that could not run (lab not set up) as a failure |
| `fixtures/` | The shipped files that setup restores |
| `.evolv/instructions.md` | Learner instructions |
| `.evolv/grade.yml` | Grading manifest, used by Run Tests and by the grader |
| `requirements.txt` | pytest, the only dependency |
| `Dockerfile` | Grader image with the dependencies baked in |
| `expected/on-completion.txt` | The result of a finished lab |

There are no held-out tests in this lab: every check is visible.

## Run the tests

The lab needs a Linux or macOS shell (on Windows, an Ubuntu WSL terminal) and
Python 3.11 or later. Set the lab up once, then run the checks:

```
python test/setup_lab.py
python -m pytest -q
```

On the platform, **Run Tests** runs the second command. All 8 checks fail until the
steps are done. That is expected. Grading never runs `test/setup_lab.py`.
