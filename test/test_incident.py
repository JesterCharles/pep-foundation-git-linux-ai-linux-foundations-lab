"""Trainer-authored tests — restored over the learner checkout at grade time.

One check per task. Each one runs that task's script from src/ on a fresh copy
of the incident (see test/support.py) and checks what it left behind.
"""

from test.support import (
    INCIDENT_FIXTURE,
    lines_of,
    make_incident,
    mode_of,
    read,
    run_task,
)


def test_task1_checklist_copied(tmp_path):
    incident = make_incident(tmp_path)
    run_task(1, incident)
    target = incident / "triage" / "launch-checklist.txt"
    assert target.exists(), (
        "Task 1: triage/launch-checklist.txt does not exist. In src/task1_checklist.sh, copy it "
        'out of the folder whose name contains a space: cp "release notes/launch-checklist.txt" triage/'
    )
    assert read(target) == read(INCIDENT_FIXTURE / "release notes" / "launch-checklist.txt"), (
        "Task 1: triage/launch-checklist.txt differs from the release manager's copy. "
        'Copy it with cp "release notes/launch-checklist.txt" triage/ and do not change it.'
    )


def test_task2_log_triaged(tmp_path):
    incident = make_incident(tmp_path)
    run_task(2, incident)
    count = incident / "triage" / "error-count.txt"
    assert count.exists(), (
        "Task 2: triage/error-count.txt does not exist. Count the ERROR lines by piping grep "
        "into wc -l: grep ERROR app/logs/app.log | wc -l > triage/error-count.txt"
    )
    assert read(count).strip() == "4", (
        f"Task 2: triage/error-count.txt holds {read(count).strip()!r}, but app/logs/app.log has "
        "4 ERROR lines. Build it with grep ERROR app/logs/app.log | wc -l > triage/error-count.txt"
    )
    real = incident / "triage" / "real-errors.txt"
    assert real.exists(), (
        "Task 2: triage/real-errors.txt does not exist. Keep the ERROR lines but drop the retry "
        "noise: grep ERROR app/logs/app.log | grep -v retrying > triage/real-errors.txt"
    )
    assert len(lines_of(real)) == 2, (
        f"Task 2: triage/real-errors.txt has {len(lines_of(real))} lines, but exactly two ERROR "
        "lines are not retry attempts. Build it with "
        "grep ERROR app/logs/app.log | grep -v retrying > triage/real-errors.txt"
    )


def test_task3_status_script_is_750(tmp_path):
    incident = make_incident(tmp_path)
    run_task(3, incident)
    mode = mode_of(incident / "bin" / "status.sh")
    assert mode == "750", (
        f"Task 3: bin/status.sh has mode {mode}, but the runbook asks for 750 (owner "
        "read-write-execute, group read-execute, others nothing). Use: chmod 750 bin/status.sh"
    )


def test_task4_deploy_env_created(tmp_path):
    incident = make_incident(tmp_path)
    run_task(4, incident)
    env_file = incident / "env" / "deploy.env"
    assert env_file.exists(), (
        "Task 4: env/deploy.env does not exist. Create it from the example: "
        "cp env/deploy.env.example env/deploy.env"
    )
    assert "export DEPLOY_ENV=staging" in lines_of(env_file), (
        "Task 4: env/deploy.env must set the staging deployment with the whole line "
        "export DEPLOY_ENV=staging (without export, programs you start cannot see the variable). "
        "sed can change the example's line, for example: "
        "sed -i 's/^export DEPLOY_ENV=.*/export DEPLOY_ENV=staging/' env/deploy.env"
    )
    mode = mode_of(env_file)
    assert mode == "600", (
        f"Task 4: env/deploy.env has mode {mode}, but deployment settings are for the owner "
        "only: chmod 600 env/deploy.env"
    )


def test_task5_port_fixed_and_diagnosed(tmp_path):
    incident = make_incident(tmp_path)
    run_task(5, incident)
    diagnosis = incident / "triage" / "port-diagnosis.txt"
    assert diagnosis.exists(), (
        "Task 5: triage/port-diagnosis.txt does not exist. Write the two lines symptom=... and "
        "cause=... from Task 5 of the lab instructions."
    )
    lines = lines_of(diagnosis)
    assert "symptom=connection-refused" in lines, (
        "Task 5: the diagnosis needs the line symptom=connection-refused: that is what the health "
        "check hit on port 8080."
    )
    assert "cause=nothing-listening" in lines, (
        "Task 5: the diagnosis needs the cause the evidence supports, picked from the three in the "
        "lab instructions. Connection refused means no program is listening on that port; "
        "address already in use means two programs want the same port."
    )
    config = lines_of(incident / "app" / "config" / "app.conf")
    assert "port=8080" in config, (
        "Task 5: app/config/app.conf still has the wrong port. The runbook says the service must "
        "listen on http://localhost:8080. Change the port= line, for example with "
        "sed -i 's/^port=.*/port=8080/' app/config/app.conf"
    )
