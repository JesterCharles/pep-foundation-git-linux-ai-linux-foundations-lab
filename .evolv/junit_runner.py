#!/usr/bin/env python3
"""Run this lab's checks for Exa grading and write a JUnit XML report.

It runs exactly the checks of `python -m unittest discover -s tests -v`, with
the same output, and adds two things for grading:

- a JUnit XML report at reports/junit.xml;
- a non-zero exit when nothing really ran. If the lab was never set up, the
  checks skip themselves; here every skip, and a run with zero tests, counts as
  a failure, so an untouched project never passes.

Standard library only (Python 3.11 or newer). It never runs tests/setup_lab.py,
because that would reset the learner's work.
"""
import sys
import time
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
REPORT = ROOT / "reports" / "junit.xml"


class RecordingResult(unittest.TextTestResult):
    """TextTestResult that also records every outcome for the XML report."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self._started = {}

    def startTest(self, test):
        self._started[test.id()] = time.perf_counter()
        super().startTest(test)

    def _record(self, test, outcome, message="", detail=""):
        started = self._started.pop(test.id(), None)
        elapsed = time.perf_counter() - started if started is not None else 0.0
        if isinstance(test, unittest.TestCase):
            classname, _, name = test.id().rpartition(".")
        else:  # class- or module-level problem, e.g. a skip raised in setUpClass
            classname = name = getattr(test, "description", str(test))
        self.records.append((classname, name, outcome, message, detail, elapsed))

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "failure", str(err[1]), self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "error", str(err[1]), self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "not-run", f"Not run: {reason}", f"Not run: {reason}")


def write_report(result, elapsed):
    failures = sum(1 for r in result.records if r[2] in ("failure", "not-run"))
    errors = sum(1 for r in result.records if r[2] == "error")
    suite = ET.Element("testsuite", {
        "name": "lab-checks",
        "tests": str(max(len(result.records), 1)),
        "failures": str(failures + (0 if result.records else 1)),
        "errors": str(errors),
        "skipped": "0",
        "time": f"{elapsed:.3f}",
    })
    for classname, name, outcome, message, detail, took in result.records:
        case = ET.SubElement(suite, "testcase", {"classname": classname, "name": name, "time": f"{took:.3f}"})
        if outcome in ("failure", "not-run"):
            ET.SubElement(case, "failure", {"message": message, "type": "AssertionError" if outcome == "failure" else "NotRun"}).text = detail
        elif outcome == "error":
            ET.SubElement(case, "error", {"message": message, "type": "Error"}).text = detail
    if not result.records:
        case = ET.SubElement(suite, "testcase", {"classname": "lab-checks", "name": "no_checks_ran", "time": "0.000"})
        ET.SubElement(case, "failure", {"message": "No checks ran.", "type": "NotRun"}).text = "No checks ran."
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element("testsuites")
    root.append(suite)
    ET.ElementTree(root).write(REPORT, encoding="utf-8", xml_declaration=True)


def main():
    suite = unittest.defaultTestLoader.discover(start_dir=str(TESTS), top_level_dir=str(TESTS))
    runner = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult)
    started = time.perf_counter()
    result = runner.run(suite)
    write_report(result, time.perf_counter() - started)
    not_run = [r for r in result.records if r[2] == "not-run"]
    if not result.records or result.testsRun == 0 or not_run:
        print("\nFAILED: the checks did not run. Set up the lab first with: python tests/setup_lab.py",
              file=sys.stderr)
        return 1
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
