"""Grading guard: a check that did not run is a failure, never a pass.

The checks skip themselves when the lab was never set up (the folders that
test/setup_lab.py creates are missing). For Run Tests and for grading, every
such skip is reported as a failure that says how to set the lab up, so an
untouched project can never pass. A run that collects no checks at all already
fails: pytest exits with code 5.

This file never runs test/setup_lab.py, because that would reset the
learner's work.
"""

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.skipped and not hasattr(report, "wasxfail"):
        longrepr = report.longrepr
        reason = longrepr[2] if isinstance(longrepr, tuple) else str(longrepr)
        reason = reason.removeprefix("Skipped: ")
        report.outcome = "failed"
        report.longrepr = f"Not run: {reason}"
