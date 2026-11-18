#!/usr/bin/env bash
# Task 5: find and fix the port mismatch.
# Runs inside the incident folder.
set -euo pipefail

# TODO: write triage/port-diagnosis.txt with two lines:
#         symptom=connection-refused
#         cause=<nothing-listening, port-already-in-use or dns-failure>
#       Pick the cause the evidence supports.

# TODO: change only the port= line of app/config/app.conf to the port the runbook names.
#       Keep host=localhost and every other line.
