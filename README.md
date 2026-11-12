# Service will not start

A small service called `status-page` is unhealthy. The on-call teammate left you a
folder of evidence: logs, a config file, a runbook and a launch checklist. You use
the Linux shell to find the real errors, fix a file permission, set an environment
variable and fix the port mismatch behind `connection refused`. The service never
actually runs: all the evidence is in files.

- **Time:** about 15 minutes. If you pass 20, pause and finish in self-study.
- **You need:** a bash terminal and Python 3.11 or newer. Linux permissions are part
  of the lab, so use macOS or Linux (on Windows, see **Troubleshooting**).
- **Offline:** no account, network, container or AI assistant.

## Your path

```text
Open project -> Set up -> Tests: 8 fail -> Steps 3-7 -> Tests: 8 ok -> Stop
```

In words: open the project, set it up and see all 8 checks fail, work through
steps 3 to 7, then run the checks again and stop when all 8 pass.

## Quick start

1. **Open the project.** Open this lab's folder in VS Code. It is already on your
   machine, so you do not need to clone anything. Open a terminal with
   **Terminal > New Terminal**; it starts in the project folder, the one that holds
   this README.
2. **Set up, then run the starter tests:**

   ```text
   python tests/setup_lab.py
   python -m unittest discover -s tests -v
   ```

   **Expect:** `Incident ready in starter/incident/.`, then all 8 checks `FAIL`.
   That is normal before you start: each failure message names what is missing.
   Now move into the incident folder, where steps 3 to 7 happen:
   `cd starter/incident`
3. **Look around** and copy the launch checklist out of the `release notes` folder
   into `triage/`. Check name: `checklist`.
4. **Triage the log:** save the ERROR line count in `triage/error-count.txt` and only
   the real errors in `triage/real-errors.txt`. Check names: `error_count`,
   `real_errors`.
5. **Fix the permissions:** make `bin/status.sh` runnable with mode `750`. Do not
   change its content. Check name: `executable`.
6. **Set the deployment:** create `env/deploy.env` with mode `600`. Check name:
   `env_file`.
7. **Find and fix the port mismatch:** write `triage/port-diagnosis.txt`, then fix
   the port in `app/config/app.conf`. Check names: `diagnosis`, `config_port`.
8. **Prove it:** go back to the project folder and run every check:

   ```text
   cd ../..
   python -m unittest discover -s tests -v
   ```

   **Expect:** all 8 checks report `ok`, then `OK`. You are done: stop here.

**Check one step at a time.** From `starter/incident`, put the step's check name
after `-k`:

```text
python -m unittest discover -s ../../tests -v -k error_count
```

**Expect:** that check reports `ok`. If it says `FAIL`, read the message under it.

## Step-by-step guide

Steps 3 to 7 run in the incident folder, `starter/incident`.

### Step 3: Find your way around

```text
pwd
ls -a
cat docs/RUNBOOK.md
```

**Expect:** `pwd` ends in `starter/incident`. The list shows `app`, `bin`, `docs`,
`env`, `release notes` and `triage`. The runbook describes how the healthy service
should look.

<details>
<summary>Hint</summary>

Relative paths such as `app/logs` start from where you are; `..` is the parent
folder (so `cd ../..` goes up two levels) and `~` is your home folder.

</details>

A path with a space falls apart into two words unless you quote it:

```text
ls "release notes"
cp "release notes/launch-checklist.txt" triage/
```

**Expect:** `ls triage` now shows `launch-checklist.txt`.

### Step 4: Triage the log with pipes and grep

Read the log with `cat app/logs/app.log`: fifteen lines, mostly noise. A pipe (`|`)
hands one command's output to the next, and `>` saves output to a file:

```text
grep ERROR app/logs/app.log
grep ERROR app/logs/app.log | wc -l > triage/error-count.txt
```

**Expect:** four ERROR lines, so the file holds `4`.

Two of those errors are only retry attempts. `grep -v` keeps the lines that do
**not** match:

```text
grep ERROR app/logs/app.log | grep -v retrying > triage/real-errors.txt
cat triage/real-errors.txt
```

**Expect:** exactly two lines: the first `connection refused` failure and the
`UNHEALTHY` verdict.

### Step 5: Fix the permissions

```text
./bin/status.sh
ls -l bin/status.sh
```

**Expect:** `permission denied`, and `-rw-r--r--` with no `x`: running a file
directly needs execute permission. The runbook asks for mode `750`: owner `rwx` (7),
group `r-x` (5), others nothing (0):

```text
chmod 750 bin/status.sh
./bin/status.sh
```

**Expect:** the script prints
`status-page (development) expects http://localhost:9091/status`.
Both `development` and `9091` are still wrong; steps 6 and 7 fix them.

### Step 6: Set the deployment through the environment

The script reads the deployment name from the `DEPLOY_ENV` environment variable.
Try it without and then with `export`:

```text
DEPLOY_ENV=staging
./bin/status.sh
export DEPLOY_ENV=staging
./bin/status.sh
```

**Expect:** first `(development)`, then `(staging)`. A program you start only sees
exported variables.

An exported variable disappears when the terminal closes, so the service reads its
settings from a file. Create it from the example:

```text
cp env/deploy.env.example env/deploy.env
```

Open `env/deploy.env` in the editor and make its setting line exactly
`export DEPLOY_ENV=staging`. Deployment settings are private, so make the file
owner read-write only:

```text
chmod 600 env/deploy.env
ls -l env/deploy.env
```

**Expect:** `-rw-------`.

### Step 7: Find and fix the port mismatch

```text
cat triage/real-errors.txt
grep port app/config/app.conf
```

**Expect:** the health check calls `http://localhost:8080/status` and is refused,
while the config says `port=9091`. In `http://localhost:8080`, `localhost` is this
machine and `8080` is the port.

<details>
<summary>Hint</summary>

`address already in use` is a different port problem: something already listens
where a program wants to start.

</details>

Create `triage/port-diagnosis.txt` with two lines. For the cause, pick the one the
evidence supports: `nothing-listening`, `port-already-in-use` or `dns-failure`.

```text
symptom=connection-refused
cause=<your pick>
```

Then open `app/config/app.conf`, change only the `port=` line to the runbook's port
(keep `host=localhost`), and run `./bin/status.sh` again.

**Expect:** `status-page (staging) expects http://localhost:8080/status`.
Now do step 8.

## Reference

- **What the 8 checks look at:** the copied checklist, the error count, the filtered
  errors, the script's permission, the settings file and its permission, the config
  port, your diagnosis, and whether `./bin/status.sh` runs directly and prints the
  healthy line. They read files and permissions only; nothing uses the network.
- **Expected output:** when everything passes, the output matches
  `expected/on-completion.txt`; only the run time differs.
- **Start again:** from the project folder, `python tests/setup_lab.py` resets the
  lab. It removes your triage files and `env/deploy.env` and restores every shipped
  file.
- **Clean up when finished:** from the project folder, `python tests/cleanup_lab.py`
  removes everything setup created and restores the shipped files and permissions.
- **Leave these as they are:** `tests/`, `fixtures/` and `expected/`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python: command not found`, or a version older than 3.11 | Run `python3 --version`. If that shows 3.11 or newer, type `alias python=python3` once in this terminal. |
| `The incident folder is missing` | From the project folder, run `python tests/setup_lab.py`. |
| A test command fails with `No such file or directory` | Check where you are with `pwd`. Use `-s tests` in the project folder and `-s ../../tests` in `starter/incident`. |
| `cp: release notes: No such file or directory` | Put quotes around the path that contains the space. |
| `./bin/status.sh: permission denied` after `chmod` | `ls -l bin/status.sh` must show `-rwxr-x---`. |
| The status line still says `development` or `9091` | Recheck step 6 (`env/deploy.env`) or step 7 (the `port=` line only). |
| You are on Windows and permissions never change | Run the whole lab in an Ubuntu (WSL) terminal: Windows file systems do not keep Linux permissions. |
| Your lab state is broken | From the project folder, run `python tests/setup_lab.py`, then repeat the steps in order. |

## Optional: work on your own computer

You only need this if you were not given the project. Clone
`https://github.com/JesterCharles/pep-foundation-git-linux-ai-linux-foundations-lab`,
open the cloned folder in VS Code or another editor, and start at **Quick start**.
