# Service will not start

A small service called `status-page` is unhealthy. The on-call teammate left you a
folder of evidence: logs, a config file, a runbook and a launch checklist. You use
the Linux shell to find the real errors, fix a file permission, set an environment
variable and fix the port mismatch behind `connection refused`. The service never
actually runs: all the evidence is in files.

You write the commands for each task into a bash script in `src/`. The tests copy
the incident folder into a fresh temporary folder, run your script there and check
what it left behind. So try your commands in a practice copy first, then put the
ones that work into the script.

- **Time:** about 15 minutes. If you pass 20, pause and finish in self-study.
- **You need:** the lab's Linux terminal (bash). Permissions are part of the lab, so
  it does not work in a Windows terminal.
- **Offline:** no account, network or AI assistant.

## Your path

```text
Run Tests: 5 fail -> practice copy -> Tasks 1-5 (one script each) -> Run Tests: 5 pass -> Submit
```

In words: run the tests and see all 5 fail, make a practice copy, work through the
five tasks, writing each task's commands into its script, then select **Run Tests**
again and select **Submit** when all 5 pass.

## Quick start

1. Select **Run Tests** before you change anything.

   **All 5 visible tests fail at first. That is expected: the scripts only hold
   `TODO` comments.** Every failure message starts with its task number, such as
   `Task 2:`.
2. **Make a practice copy of the incident.** Open a terminal with
   **Terminal > New Terminal** (it starts in the project folder) and run:

   ```text
   python -m test.sandbox
   ```

   **Expect:** `Practice incident ready in ...` and a `cd` line. Run that `cd` line:
   you are now in a throwaway copy of the incident. Try commands there as much as you
   like; `python -m test.sandbox` (from the project folder) makes a fresh copy.
3. Work through the checklist below. For each task, try the commands in the practice
   copy, then put them in the task's script in `src/`, in the order you ran them.
   Select **Run Tests** after each task and read the remaining `Task N:` messages.
4. **You are finished when all 5 tests pass.** Then select **Submit**. Submitting also
   runs held-out tests you can't see. They run your scripts again, for example on a
   log with different errors, so write commands that work things out rather than
   typing in the answers.

## Checklist

- [ ] Task 1: `src/task1_checklist.sh` copies the launch checklist into `triage/`
- [ ] Task 2: `src/task2_triage.sh` saves the error count and the real errors
- [ ] Task 3: `src/task3_permissions.sh` makes `bin/status.sh` mode `750`
- [ ] Task 4: `src/task4_environment.sh` creates `env/deploy.env` with mode `600`
- [ ] Task 5: `src/task5_port.sh` records the diagnosis and fixes the port

A task is done when no failure message starts with its number.

## How your scripts run

- Each script runs with `bash` **inside the incident folder**, the one that holds
  `app/`, `bin/`, `docs/`, `env/`, `release notes/` and `triage/`. Use paths relative
  to it, such as `app/logs/app.log`. Do not `cd` anywhere else.
- Every test starts from a fresh copy of the incident and runs only that task's
  script. So each script must do its whole task by itself.
- The scripts start with `set -euo pipefail`: the script stops at the first command
  that fails, and the test shows bash's error message.
- To run one of your scripts on your practice copy, run it from the incident folder:
  `bash <project folder>/src/task2_triage.sh`. `python -m test.sandbox` prints the
  exact path.

## Task steps

Paths below are relative to the incident folder.

### Task 1: Find your way around

Look around the practice copy:

```text
pwd
ls -a
cat docs/RUNBOOK.md
```

**Expect:** the list shows `app`, `bin`, `docs`, `env`, `release notes` and `triage`.
The runbook describes how the healthy service should look.

<details>
<summary>Hint</summary>

Relative paths such as `app/logs` start from where you are; `..` is the parent folder
(so `cd ../..` goes up two levels) and `~` is your home folder.

</details>

A path with a space falls apart into two words unless you quote it:

```text
ls "release notes"
cp "release notes/launch-checklist.txt" triage/
```

**Expect:** `ls triage` now shows `launch-checklist.txt`. Put the `cp` command in
`src/task1_checklist.sh`. Copy the file; do not move it.

### Task 2: Triage the log with pipes and grep

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
`UNHEALTHY` verdict. Put the two commands that write the files in
`src/task2_triage.sh`. The held-out tests run it on a different log, so let `grep`
and `wc` find the answers.

### Task 3: Fix the permissions

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
Both `development` and `9091` are still wrong; Tasks 4 and 5 fix them. Put the
`chmod` command in `src/task3_permissions.sh`. Do not change the script's content.

### Task 4: Set the deployment through the environment

`bin/status.sh` reads the deployment name from the `DEPLOY_ENV` environment variable.
In your practice copy (with Task 3 done there), try it without and then with
`export`:

```text
DEPLOY_ENV=staging
./bin/status.sh
export DEPLOY_ENV=staging
./bin/status.sh
```

**Expect:** first `(development)`, then `(staging)`. A program you start only sees
exported variables.

An exported variable disappears when the terminal closes, so the service reads its
settings from a file. Create it from the example, set the value, and make it private:

```text
cp env/deploy.env.example env/deploy.env
sed -i 's/^export DEPLOY_ENV=.*/export DEPLOY_ENV=staging/' env/deploy.env
chmod 600 env/deploy.env
cat env/deploy.env
ls -l env/deploy.env
```

**Expect:** the last line of the file is exactly `export DEPLOY_ENV=staging`, and
`ls -l` shows `-rw-------`. `sed -i 's/old/new/' file` edits a file in place: here it
replaces the whole line that starts with `export DEPLOY_ENV=`. Put the three commands
that change files in `src/task4_environment.sh`. Keep the example file as it is.

### Task 5: Find and fix the port mismatch

```text
grep ERROR app/logs/app.log | grep -v retrying
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

Your diagnosis goes in `triage/port-diagnosis.txt`, two lines. For the cause, pick
the one the evidence supports: `nothing-listening`, `port-already-in-use` or
`dns-failure`.

```text
symptom=connection-refused
cause=<your pick>
```

`printf` writes several lines in one command, one `%s\n` per line:

```text
printf '%s\n' 'symptom=connection-refused' 'cause=<your pick>' > triage/port-diagnosis.txt
```

Then change only the `port=` line of `app/config/app.conf` to the runbook's port, and
keep `host=localhost`:

```text
sed -i 's/^port=.*/port=<the runbook port>/' app/config/app.conf
```

Put both commands, with your values filled in, in `src/task5_port.sh`. In your
practice copy, with Tasks 3 to 5 done, `./bin/status.sh` now prints
`status-page (staging) expects http://localhost:8080/status`.

## Reference

- **What the 5 visible tests check:** the copied checklist; the error count and the
  real errors; the script's permission; the settings file, its export line and its
  permission; your diagnosis and the config port. Each one runs only its own task's
  script on a fresh copy of the incident.
- **Held-out tests**, run on Submit, also check that the originals stay in place,
  that your scripts work on different evidence, that only the lines you were asked
  to change change, and that `./bin/status.sh` prints the healthy line once all your
  scripts have run.
- **Run Tests** runs `python -m pytest -q` in the project folder. To run the checks
  for one task only, add `-k` and the task: `python -m pytest -q -k task2`.
- **Edit only the scripts in `src/`.** The tests in `test/` and the incident in
  `test/fixtures/` are restored to their original state before your work is graded,
  so changes to them do not count.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Task N: src/... stopped with exit code 1` | bash's message is shown after it. Run the script on your practice copy to see the same error. A `grep` that matches nothing also stops the script. |
| `No such file or directory` for `app/...` or `triage/...` | The script runs inside the incident folder. Remove any `cd` lines and use paths such as `app/logs/app.log`. |
| `cp: release notes: No such file or directory` | Put quotes around the path that contains the space. |
| The error count is right in practice but wrong in the test | Make sure the script counts with `grep ... \| wc -l` rather than writing a number. |
| `./bin/status.sh: permission denied` after `chmod` | `ls -l bin/status.sh` must show `-rwxr-x---`. |
| The status line still says `development` or `9091` | Recheck Task 4 (`env/deploy.env`) or Task 5 (the `port=` line only). |
| `This lab runs on Linux` | Use the lab's Linux terminal. Windows file systems do not keep Linux permissions. |
| Your practice copy is a mess | From the project folder, run `python -m test.sandbox` again and use the new copy. |
