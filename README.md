# Service will not start

The deploy status helper from the Git labs now has a tiny companion service,
`status-page`, and it is unhealthy. The on-call teammate left you a folder with
the logs, the config, a runbook and a half-finished launch checklist, then went
home. Nothing here needs the real service to run: the evidence is all in files.

Your job: navigate the incident folder, pull the real errors out of the log with
pipes and `grep`, fix the script permissions, set the deployment environment
variable properly, and find and fix the port mismatch behind
`connection refused`.

About 15 minutes of your scheduled exercise block (an estimate); if you pass
20, pause and finish in self-study, using **Troubleshooting** if you are stuck.
Everything runs on your own computer, offline: no account, no network, no
container engine, no AI assistant.

This is a Linux lab. It runs on **macOS or Linux**. On Windows, open an
**Ubuntu (WSL) terminal** and run everything there: file permissions are a Linux
concept, and Windows file systems do not carry them.

## Open the project

This repository is the whole lab. Clone it, then open the cloned folder in VS Code or any
other editor or IDE (in VS Code: **File > Open Folder**). Nothing in this lab runs in a browser.

Run every command below in a terminal at the repository root, the folder that holds this
README: in VS Code use **Terminal > New Terminal**, which opens there; with any other editor,
open a terminal and `cd` into the clone. The steps call this folder the lab folder.

## What you edit

Setup (step 2) builds `starter/incident/`; the paths below are relative to it.
The checks read these files and their permission bits:

| You create or change | How | Why the incident needs it |
|---|---|---|
| `triage/launch-checklist.txt` | copy it out of the space-named `release notes` folder (step 3) | on-call must find the checklist in the triage folder |
| `triage/error-count.txt` and `triage/real-errors.txt` | build them from `app/logs/app.log` with `grep`, a pipe and `>` (step 4) | the handoff needs the real errors, not fifteen noisy lines |
| `bin/status.sh` | `chmod 750` only - the content stays as shipped (step 5) | on-call must run the status check directly |
| `env/deploy.env` | create from `env/deploy.env.example`, set `export DEPLOY_ENV=staging`, `chmod 600` (step 6) | the service must report the right deployment, privately |
| `triage/port-diagnosis.txt` | two lines naming the symptom and its cause (step 7) | the postmortem needs the diagnosis on record |
| `app/config/app.conf` | fix the `port=` line to the runbook's port (step 7) | the health check and the service must agree on one port |

Leave `tests/`, `fixtures/` and `expected/` as they are: the eight
checks pass only when the incident is really fixed.

One test command proves the lab, run from this lab folder (step 8):

```text
python -m unittest discover -s tests -v
```

Each failing check prints the next action to take.

## 1. Check your tools

Open a terminal at the repository root (the folder that holds this README).
Type each command and press Enter:

```text
bash --version
python --version
```

**Expect:** any bash version, and `Python 3.11` or newer.
If `python` is missing or old, try `python3 --version`; when that works, type
`alias python=python3` once for this terminal window.

## 2. Create the incident

From this lab folder, run:

```text
python tests/setup_lab.py
```

**Expect:** `Incident ready in starter/incident/.`

Setup creates the triage folder, the release manager's `release notes` folder,
and ships `bin/status.sh` without execute permission - that broken permission is
part of the incident. Running setup again resets the lab: your triage results
and `env/deploy.env` are removed and every shipped file is restored.

Move into the incident folder:

```text
cd starter/incident
```

## 3. Find your way around

```text
pwd
ls -a
ls app app/logs docs
cat docs/RUNBOOK.md
```

**Expect:** `pwd` ends in `starter/incident`; the listing shows `app`, `bin`,
`docs`, `env`, `release notes` and `triage`. Read the runbook: it tells you how
the service is supposed to look when healthy.

The release manager keeps the launch checklist in a folder whose name contains
a space. A bare `cd release notes` or `cp release notes/...` falls apart into
two words, so quote the path:

```text
ls "release notes"
cp "release notes/launch-checklist.txt" triage/
```

**Expect:** the copy succeeds; `ls triage` now shows `launch-checklist.txt`.
(Relative paths like `app/logs` start from where you stand; `~` is your home
folder and `..` is the parent - the checks only care that you end up in the
right place.)

## 4. Triage the log with pipes and grep

Look at the raw log first:

```text
cat app/logs/app.log
```

Fifteen lines, most of them noise. Narrow it down - a pipe (`|`) hands one
command's output to the next:

```text
grep ERROR app/logs/app.log
grep ERROR app/logs/app.log | wc -l
```

**Expect:** four ERROR lines, and `wc -l` counts them: `4`.
Record the count by redirecting the pipeline's output into a file:

```text
grep ERROR app/logs/app.log | wc -l > triage/error-count.txt
```

Two of those errors are just retry attempts. Keep the ERROR lines, then drop
the ones that mention retrying with `-v` (invert the match):

```text
grep ERROR app/logs/app.log | grep -v retrying > triage/real-errors.txt
cat triage/real-errors.txt
```

**Expect:** exactly two lines: the first `connection refused` failure and the
`UNHEALTHY` verdict. (`grep -i` would match any capitalisation; the log writes
ERROR in capitals, so plain `grep` is enough here.)

## 5. Fix the permissions

The runbook says the on-call person runs the script directly. Try it:

```text
./bin/status.sh
```

**Expect:** `permission denied`. Now look at why:

```text
ls -l bin/status.sh
```

**Expect:** `-rw-r--r--` - owner read-write, group read, others read, and **no
`x` anywhere**. Running a file directly needs execute permission. (Note that
`bash bin/status.sh` works even now: there the program being executed is
`bash`, which only *reads* the script.)

The runbook asks for mode `750`: owner `rwx` (7), group `r-x` (5), others
nothing (0):

```text
chmod 750 bin/status.sh
ls -l bin/status.sh
./bin/status.sh
```

**Expect:** `-rwxr-x---`, and the script now prints a status line:
`status-page (development) expects http://localhost:9091/status`.
Both parts of that line are still wrong; the next two steps fix them.

## 6. Set the deployment through the environment

The script reads the deployment name from the `DEPLOY_ENV` environment
variable. Watch what the environment actually does. First set a variable
**without** `export`, then run the script:

```text
DEPLOY_ENV=staging
./bin/status.sh
```

**Expect:** still `(development)`. The variable exists only in your shell; a
program you start is a new process and never sees unexported variables. Now:

```text
export DEPLOY_ENV=staging
./bin/status.sh
```

**Expect:** `(staging)`. Exported variables are copied to every program the
shell starts. Check it yourself with `echo $DEPLOY_ENV`.

Your exported variable disappears with this terminal, so the service loads its
settings from a file. Create it from the example and set staging there:

```text
cp env/deploy.env.example env/deploy.env
```

Open `env/deploy.env` in any editor and make its setting line exactly:

```text
export DEPLOY_ENV=staging
```

Deployment settings are nobody else's business - owner read-write only:

```text
chmod 600 env/deploy.env
ls -l env/deploy.env
```

**Expect:** `-rw-------`.

## 7. Find and fix the port mismatch

Read the evidence you collected:

```text
cat triage/real-errors.txt
grep port app/config/app.conf
```

**Expect:** the health check calls `http://localhost:8080/status` and is
refused, while the config says `port=9091`. In a URL like
`http://localhost:8080`, `localhost` is the host - this machine itself,
127.0.0.1 - and `8080` is the port. The service listens on 9091, the health
check knocks on 8080, and nobody is listening there: **connection refused**.
(The other classic port failure, `address already in use`, is the opposite:
something is already listening where a program wants to start.)

Record the diagnosis as two lines in `triage/port-diagnosis.txt`. The cause is
one of `nothing-listening`, `port-already-in-use` or `dns-failure` - pick the
one the evidence supports:

```text
symptom=connection-refused
cause=<your pick>
```

Then fix the config: open `app/config/app.conf` and change the `port=` line to
the runbook's port, keeping `host=localhost`. Run `./bin/status.sh` once more.

**Expect:** `status-page (staging) expects http://localhost:8080/status`.

## 8. Prove it

Return to the lab folder and run the checks:

```text
cd ../..
python -m unittest discover -s tests -v
```

**Expect:** all eight checks report `ok`, then `OK` (see **Expected output** below).

## How the checks work

The test command is `python -m unittest discover -s tests -v`, run from this
lab folder. It reads files and permission bits and runs `./bin/status.sh` once;
it never needs the network.

| Check | What it confirms |
|---|---|
| `test_checklist_copied_from_spaced_folder` | the checklist was copied out of the space-named folder, byte for byte |
| `test_error_count_via_pipe` | `triage/error-count.txt` holds the ERROR line count (4) |
| `test_real_errors_filtered` | `triage/real-errors.txt` holds exactly the two non-retry ERROR lines |
| `test_script_is_executable_750` | `bin/status.sh` has mode `750` |
| `test_env_file_exists_with_export_and_600` | `env/deploy.env` exports `DEPLOY_ENV=staging` and has mode `600` |
| `test_config_port_matches_runbook` | `app.conf` says `port=8080` with `host=localhost` |
| `test_port_diagnosis_recorded` | your diagnosis names the symptom and the right cause |
| `test_status_script_runs_directly_and_reports_staging` | `./bin/status.sh` runs directly and prints the healthy line |

## Expected output

Right after setup, all eight checks fail, each with a message naming the next
action. On completion the output matches `expected/on-completion.txt`; only the
run time differs.

## Offline note

Setup and checks use only the shell and the Python standard library. The
service never runs; its log and config are fixed files, so nothing listens on
any port during this lab.

## Cleanup

When you are finished, run this from the lab folder:

```text
python tests/cleanup_lab.py
```

It removes `triage/`, the `release notes` folder, `env/deploy.env` and the
Python cache in `tests/`, then restores the shipped files and the shipped
permissions. It touches nothing outside this lab folder.

## Troubleshooting

| Symptom | What to do |
|---|---|
| `python: command not found` | Use `python3`, or `alias python=python3` for this terminal window. |
| `The incident folder is missing` | Run `python tests/setup_lab.py` from the lab folder. |
| You are on Windows and permissions never change | Run the whole lab inside an Ubuntu (WSL) terminal; the Windows file system does not carry Linux permission bits. |
| `cp: release notes: No such file or directory` | The space split your path. Quote it: `cp "release notes/launch-checklist.txt" triage/`. |
| `error-count.txt` holds the wrong number | Rebuild it exactly: `grep ERROR app/logs/app.log \| wc -l > triage/error-count.txt`. |
| `./bin/status.sh: permission denied` after chmod | Check `ls -l bin/status.sh` shows `-rwxr-x---` (750), and that you ran chmod on `bin/status.sh`, not the example file. |
| The status line still says `development` | `env/deploy.env` must exist and contain exactly `export DEPLOY_ENV=staging`. |
| The status line still says `9091` | Edit `app/config/app.conf`: the `port=` line, nothing else. |
| You are lost or past 20 minutes | Pause the exercise block and continue in self-study. If your lab state is broken, rerun `python tests/setup_lab.py` (it resets everything) and repeat the steps in order. |
