"""The tests leg bites, and it declines rather than recursing.

Every fixture below is a tree of its own, because a leg that ran this repository's
own suite from inside this repository's own suite is the thing the leg refuses to
do, and a test of it would be the first thing to hang.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from raumbuch.gate import suite

PASSES = """
import unittest


class Two(unittest.TestCase):
    def test_one(self) -> None:
        self.assertEqual(1, 1)

    def test_two(self) -> None:
        self.assertEqual(2, 2)
"""

FAILS = """
import unittest


class One(unittest.TestCase):
    def test_it_passes(self) -> None:
        self.assertEqual(1, 1)

    def test_it_does_not(self) -> None:
        self.assertEqual(1, 2)
"""

# Discovery imports a test module before it runs anything in it, and `os._exit`
# leaves no traceback, no ERROR line and no count behind. The two differ only in
# the status the runner leaves with, which is the whole of what these prove.
DIES_LOUDLY = """
import os

os._exit(3)
"""

DIES_QUIETLY = """
import os

os._exit(0)
"""


def tree(root: Path, text: str) -> None:
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests/test_fixture.py").write_text(text, encoding="utf-8")


def outside_a_suite_run():
    """Run as though no gate-started suite were in progress.

    This suite may itself be running inside one, and every fixture below is
    about what the leg does when it is not.
    """
    patched = mock.patch.dict(os.environ)
    patched.start()
    os.environ.pop(suite.INSIDE, None)
    return patched


class InsideASuiteRun(unittest.TestCase):
    def test_the_leg_declines_and_says_what_running_it_costs(self) -> None:
        with mock.patch.dict(os.environ, {suite.INSIDE: "1"}):
            verdict = suite.run(Path("."))
        self.assertEqual(verdict.state, "not run")
        self.assertIn("not run", verdict.detail)
        self.assertIn("costs", verdict.detail)
        self.assertIn(suite.INSIDE, verdict.detail)

    def test_the_subprocess_is_told_it_is_one(self) -> None:
        # This is what bounds the recursion at two: whatever the suite runs, a
        # gate inside it sees the variable and declines.
        self.assertEqual(suite.environment(Path("."))[suite.INSIDE], "1")


class TheLegRefuses(unittest.TestCase):
    def test_a_suite_with_a_failing_test_in_it_naming_the_test(self) -> None:
        patched = outside_a_suite_run()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                tree(root, FAILS)
                verdict = suite.run(root)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, "refused")
        self.assertIn("1 test(s) of 2 did not pass", verdict.detail)
        self.assertIn("test_it_does_not", verdict.detail)
        self.assertNotIn("test_it_passes", verdict.detail)

    def test_a_run_that_died_before_it_named_anything(self) -> None:
        # A test module calling `os._exit` at import time takes the runner with
        # it, so the run comes back non-zero having printed no FAIL and no ERROR
        # line. There is nothing to name and nothing that says the suite passed,
        # and the leg refuses rather than reading an empty report as a clean one.
        patched = outside_a_suite_run()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                tree(root, DIES_LOUDLY)
                verdict = suite.run(root)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, "refused")
        self.assertIn("could not judge this tree", verdict.detail)
        self.assertIn("exit 3", verdict.detail)

    def test_a_run_that_exited_zero_without_running_a_suite(self) -> None:
        # The near miss of the fixture above, and the worse of the two: the same
        # module leaves with a zero status, which is what a runner that passed
        # also does. The count is the only thing that separates them, so a leg
        # reading the status alone reports a green suite over nothing at all.
        patched = outside_a_suite_run()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                tree(root, DIES_QUIETLY)
                verdict = suite.run(root)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, "refused")
        self.assertIn("without saying how many tests it ran", verdict.detail)

    def test_a_tree_carrying_no_suite(self) -> None:
        patched = outside_a_suite_run()
        try:
            with tempfile.TemporaryDirectory() as directory:
                verdict = suite.run(Path(directory))
        finally:
            patched.stop()
        self.assertEqual(verdict.state, "refused")
        self.assertIn("no unit suite", verdict.detail)


class TheLegPasses(unittest.TestCase):
    def test_a_suite_that_passes_and_carries_the_count_back(self) -> None:
        patched = outside_a_suite_run()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                tree(root, PASSES)
                verdict = suite.run(root)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("2 test(s)", verdict.detail)


class ReadingWhatARunSaid(unittest.TestCase):
    def test_the_count_comes_off_the_line_that_reports_it(self) -> None:
        self.assertEqual(suite.counted(["Ran 121 tests in 15.899s", "OK"]), 121)
        self.assertEqual(suite.counted(["Ran 1 test in 0.001s"]), 1)

    def test_a_run_that_never_said_how_many_it_ran(self) -> None:
        self.assertIsNone(suite.counted(["Traceback (most recent call last):"]))


if __name__ == "__main__":
    unittest.main()
