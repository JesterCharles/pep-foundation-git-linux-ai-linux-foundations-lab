#!/usr/bin/env bash
# Task 2: triage the log with pipes and grep.
# Runs inside the incident folder.
set -euo pipefail

# TODO: write the number of ERROR lines in app/logs/app.log to triage/error-count.txt
#       (pipe grep into wc -l, then redirect with >).

# TODO: write only the ERROR lines that are not retry attempts to triage/real-errors.txt
#       (grep ERROR, then grep -v retrying).
