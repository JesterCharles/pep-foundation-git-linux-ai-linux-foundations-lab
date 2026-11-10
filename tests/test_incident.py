"""Checks for the "Service will not start" lab. Run from the lab folder:

    python -m unittest discover -s tests -v

Each failure message names the next action.
"""

import subprocess
import unittest

from lab_support import FIXTURES, INCIDENT, SPACED, TRIAGE, mode_of, require_posix

SETUP_HINT = "Run `python tests/setup_lab.py` from the lab folder first."


def read(path):
    return path.read_text(encoding="utf-8")


class IncidentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_posix()
        if not SPACED.exists() or not TRIAGE.exists():
            raise unittest.SkipTest(f"The incident folder is missing. {SETUP_HINT}")

    def test_checklist_copied_from_spaced_folder(self):
        target = TRIAGE / "launch-checklist.txt"
        self.assertTrue(
            target.exists(),
            'Copy the checklist out of the folder whose name contains a space: '
            'cp "release notes/launch-checklist.txt" triage/ '
            "(the quotes keep the space from splitting the path).",
        )
        self.assertEqual(
            read(FIXTURES / "launch-checklist.txt"),
            read(target),
            "triage/launch-checklist.txt differs from the release manager's copy. "
            'Copy it again with cp "release notes/launch-checklist.txt" triage/.',
        )

    def test_error_count_via_pipe(self):
        target = TRIAGE / "error-count.txt"
        self.assertTrue(
            target.exists(),
            "Count the ERROR lines by piping grep into wc -l and redirect the result: "
            "grep ERROR app/logs/app.log | wc -l > triage/error-count.txt",
        )
        self.assertEqual(
            "4",
            read(target).strip(),
            "triage/error-count.txt should hold the number of ERROR lines in app/logs/app.log. "
            "Rebuild it with: grep ERROR app/logs/app.log | wc -l > triage/error-count.txt",
        )

    def test_real_errors_filtered(self):
        target = TRIAGE / "real-errors.txt"
        self.assertTrue(
            target.exists(),
            "Keep the ERROR lines but drop the retry noise: "
            "grep ERROR app/logs/app.log | grep -v retrying > triage/real-errors.txt",
        )
        lines = [line for line in read(target).splitlines() if line.strip()]
        self.assertEqual(
            2,
            len(lines),
            "triage/real-errors.txt should hold exactly the two ERROR lines that are not "
            "retry attempts. Rebuild it with: "
            "grep ERROR app/logs/app.log | grep -v retrying > triage/real-errors.txt",
        )
        self.assertTrue(
            all("ERROR" in line and "retrying" not in line for line in lines),
            "triage/real-errors.txt contains a non-ERROR or retrying line. "
            "The first grep keeps ERROR lines; grep -v retrying then removes the retries.",
        )

    def test_script_is_executable_750(self):
        script = INCIDENT / "bin" / "status.sh"
        self.assertEqual(
            "750",
            mode_of(script),
            f"bin/status.sh has mode {mode_of(script)}, but the runbook asks for 750 "
            "(owner read-write-execute, group read-execute, others nothing). "
            "Run: chmod 750 bin/status.sh",
        )

    def test_env_file_exists_with_export_and_600(self):
        env_file = INCIDENT / "env" / "deploy.env"
        self.assertTrue(
            env_file.exists(),
            "Create the deployment settings file from its example: "
            "cp env/deploy.env.example env/deploy.env, then edit the value.",
        )
        self.assertIn(
            "export DEPLOY_ENV=staging",
            read(env_file),
            "env/deploy.env must set the staging deployment with an export line, exactly: "
            "export DEPLOY_ENV=staging "
            "(without export, a variable set in your shell is invisible to programs you start).",
        )
        self.assertEqual(
            "600",
            mode_of(env_file),
            f"env/deploy.env has mode {mode_of(env_file)}, but deployment settings are for the "
            "owner only: chmod 600 env/deploy.env",
        )

    def test_config_port_matches_runbook(self):
        config = read(INCIDENT / "app" / "config" / "app.conf")
        self.assertIn(
            "port=8080",
            config,
            "app/config/app.conf still points at the wrong port. The runbook says the service "
            "must listen on http://localhost:8080, and the log shows the health check being "
            "refused there. Edit the port= line to 8080.",
        )
        self.assertIn(
            "host=localhost",
            config,
            "Keep host=localhost in app/config/app.conf: the service and its health check run "
            "on this machine.",
        )

    def test_port_diagnosis_recorded(self):
        target = TRIAGE / "port-diagnosis.txt"
        self.assertTrue(
            target.exists(),
            "Record your diagnosis in triage/port-diagnosis.txt with the two lines from "
            "step 7 of the README (Find and fix the port mismatch).",
        )
        diagnosis = read(target)
        self.assertIn(
            "symptom=connection-refused",
            diagnosis,
            "The first line must be symptom=connection-refused: that is what the health "
            "check hit on port 8080.",
        )
        self.assertIn(
            "cause=nothing-listening",
            diagnosis,
            "The second line must name the cause from the README's three choices. "
            "Connection refused means no program is listening on that port; compare "
            "address already in use, which means two programs want the same port.",
        )

    def test_status_script_runs_directly_and_reports_staging(self):
        script = INCIDENT / "bin" / "status.sh"
        if mode_of(script) != "750":
            self.fail("Make bin/status.sh executable first: chmod 750 bin/status.sh")
        result = subprocess.run(
            ["./bin/status.sh"],
            cwd=INCIDENT,
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin"},
        )
        self.assertEqual(
            0,
            result.returncode,
            f"./bin/status.sh failed: {result.stderr.strip()} - "
            "check the execute permission and the deploy.env file.",
        )
        self.assertEqual(
            "status-page (staging) expects http://localhost:8080/status",
            result.stdout.strip(),
            "The status line is wrong. It should name the staging deployment (from "
            "env/deploy.env) and port 8080 (from app/config/app.conf).",
        )


if __name__ == "__main__":
    unittest.main()
