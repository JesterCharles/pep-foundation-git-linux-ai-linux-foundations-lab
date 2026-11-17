"""Held-out tests: graded on submit, never shown to the learner.

Each check first repeats its task's main result, so an untouched starter can
never pass one, then tries an edge case.
"""

import subprocess

from test.support import (
    HEALTHY_STATUS,
    INCIDENT_FIXTURE,
    lines_of,
    make_incident,
    mode_of,
    read,
    run_status,
    run_task,
    run_tasks,
)

VARIANT_LOG = read(INCIDENT_FIXTURE / "app" / "logs" / "app.log") + (
    "2026-01-05T08:03:00Z ERROR disk check failed: /var/lib/status-page is full\n"
    "2026-01-05T08:03:05Z ERROR disk check retrying attempt 2 of 3 failed: no space left\n"
)


def test_task1_original_checklist_stays(tmp_path):
    incident = make_incident(tmp_path)
    run_task(1, incident)
    assert (incident / "triage" / "launch-checklist.txt").exists(), (
        "Task 1: triage/launch-checklist.txt does not exist."
    )
    assert (incident / "release notes" / "launch-checklist.txt").exists(), (
        "Task 1: the release manager's checklist is gone from the release notes folder. "
        "Copy it with cp; do not move it with mv."
    )


def test_task2_real_errors_are_the_right_lines(tmp_path):
    incident = make_incident(tmp_path)
    run_task(2, incident)
    real = incident / "triage" / "real-errors.txt"
    assert real.exists(), "Task 2: triage/real-errors.txt does not exist."
    lines = lines_of(real)
    assert lines, "Task 2: triage/real-errors.txt is empty."
    assert all("ERROR" in line and "retrying" not in line for line in lines), (
        "Task 2: triage/real-errors.txt contains a line that is not an ERROR line, or a retry "
        "attempt. The first grep keeps ERROR lines; grep -v retrying then removes the retries."
    )


def test_task2_works_on_a_different_log(tmp_path):
    incident = make_incident(tmp_path, log_text=VARIANT_LOG)
    run_task(2, incident)
    count = incident / "triage" / "error-count.txt"
    real = incident / "triage" / "real-errors.txt"
    assert count.exists() and real.exists(), (
        "Task 2: triage/error-count.txt or triage/real-errors.txt does not exist."
    )
    assert read(count).strip() == "6", (
        "Task 2: on a log with 6 ERROR lines, triage/error-count.txt holds "
        f"{read(count).strip()!r}. Count the lines with grep and wc -l; do not write the number by hand."
    )
    assert len(lines_of(real)) == 3, (
        f"Task 2: on a log with 3 real errors, triage/real-errors.txt has {len(lines_of(real))} "
        "lines. Filter the log with grep; do not write the lines by hand."
    )


def test_task3_script_unchanged_and_runs_directly(tmp_path):
    incident = make_incident(tmp_path)
    run_task(3, incident)
    script = incident / "bin" / "status.sh"
    assert mode_of(script) == "750", f"Task 3: bin/status.sh has mode {mode_of(script)}, not 750."
    assert read(script) == read(INCIDENT_FIXTURE / "bin" / "status.sh"), (
        "Task 3: bin/status.sh was changed. Only its permissions need fixing; leave its content as it is."
    )
    result = run_status(incident)
    assert result.returncode == 0, (
        f"Task 3: ./bin/status.sh does not run directly: {result.stderr.strip()}"
    )


def test_task4_settings_reach_programs(tmp_path):
    incident = make_incident(tmp_path)
    run_task(4, incident)
    env_file = incident / "env" / "deploy.env"
    assert env_file.exists() and mode_of(env_file) == "600", (
        "Task 4: env/deploy.env is missing or its mode is not 600."
    )
    assert read(incident / "env" / "deploy.env.example") == read(
        INCIDENT_FIXTURE / "env" / "deploy.env.example"
    ), "Task 4: env/deploy.env.example was changed or removed. Copy it with cp and edit the copy."
    shown = subprocess.run(
        ["bash", "-c", ". env/deploy.env && env"],
        cwd=incident,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        timeout=30,
    )
    assert "DEPLOY_ENV=staging" in shown.stdout.splitlines(), (
        "Task 4: after loading env/deploy.env, a program you start does not see DEPLOY_ENV=staging. "
        "The line must export the variable: export DEPLOY_ENV=staging"
    )


def test_task5_only_the_port_line_changes(tmp_path):
    incident = make_incident(tmp_path)
    run_task(5, incident)
    config = lines_of(incident / "app" / "config" / "app.conf")
    assert "port=8080" in config, "Task 5: app/config/app.conf does not have port=8080."
    original = lines_of(INCIDENT_FIXTURE / "app" / "config" / "app.conf")
    expected = ["port=8080" if line.startswith("port=") else line for line in original]
    assert config == expected, (
        "Task 5: change only the port= line of app/config/app.conf; keep host=localhost and "
        "every other line as it is."
    )


def test_tasks_3_to_5_status_line_is_healthy(tmp_path):
    incident = make_incident(tmp_path)
    run_tasks(incident, 1, 2, 3, 4, 5)
    result = run_status(incident)
    assert result.returncode == 0, (
        f"Tasks 3-5: ./bin/status.sh failed after all your scripts ran: {result.stderr.strip()}"
    )
    assert result.stdout.strip() == HEALTHY_STATUS, (
        f"Tasks 3-5: after all your scripts ran, ./bin/status.sh prints {result.stdout.strip()!r}. "
        "It should name the staging deployment (from env/deploy.env) and port 8080 (from "
        "app/config/app.conf)."
    )
