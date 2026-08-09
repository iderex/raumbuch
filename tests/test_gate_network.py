"""The network leg bites, and it refuses to ask where the answer is not a denial.

Nothing here opens a connection. Every test below either patches the route probe
or patches the fixture run, because a suite that reached the network to prove
that nothing reaches the network would be the thing it is testing for.

The leg's own proof that the denial is real is the fixture, and the fixture is
run only in a job that has denied the network. That is a bound rather than a
gap: the refusal for a fixture that got out is exercised here with the fixture
patched, and the environment where the denial is genuinely in force is the job
named `No network in the test suite` rather than a developer's machine.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from raumbuch import gate
from raumbuch.gate import network, suite

ROOT = Path(__file__).resolve().parents[1]


def outside_a_suite_run():
    """Run as though no gate-started suite were in progress."""
    patched = mock.patch.dict(os.environ)
    patched.start()
    os.environ.pop(suite.INSIDE, None)
    return patched


def ran(returncode: int, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout="", stderr=stderr)


def denied():
    """An environment with no route out of it, said rather than made."""
    return mock.patch.object(network, "routable", return_value=False)


def posix():
    """Answer as a POSIX environment would, without moving `os.name` itself.

    Patching `os.name` reaches further than this leg: pathlib reads it when a
    Path is made, and a fixture that moved it would fail on a machine whose
    paths are the other kind.
    """
    return mock.patch.object(network, "on_posix", return_value=True)


class WhereTheContractIsNotAbout(unittest.TestCase):
    def test_inside_a_suite_a_leg_started(self) -> None:
        with mock.patch.dict(os.environ, {suite.INSIDE: "1"}):
            verdict = network.run(ROOT)
        self.assertEqual(verdict.state, gate.NOT_RUN)
        self.assertIn("without terminating", verdict.detail)
        self.assertIn("costs", verdict.detail)

    def test_off_posix_where_no_namespace_is_made(self) -> None:
        patched = outside_a_suite_run()
        try:
            with mock.patch.object(network, "on_posix", return_value=False):
                verdict = network.run(ROOT)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, gate.NOT_RUN)
        self.assertIn("network namespace", verdict.detail)
        self.assertIn("costs", verdict.detail)

    def test_where_a_route_out_of_the_environment_exists(self) -> None:
        # The common case on a workstation, and the one that matters most: a
        # suite passing with the network available proves nothing here, and a
        # leg reporting green over it would be the whole check made vacuous.
        patched = outside_a_suite_run()
        try:
            with posix(), mock.patch.object(network, "routable", return_value=True):
                verdict = network.run(ROOT)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, gate.NOT_RUN)
        self.assertIn("a route out of this environment exists", verdict.detail)
        self.assertIn("costs", verdict.detail)

    def test_the_route_probe_sends_nothing_and_answers_anyway(self) -> None:
        # A datagram socket connected to a documentation address asks the kernel
        # which interface would carry a packet there. No packet is sent, which
        # is what makes it safe to ask on a machine somebody is sitting at.
        self.assertIsInstance(network.routable(), bool)
        self.assertEqual(network.ELSEWHERE[0], "192.0.2.1")


class TheLegRefuses(unittest.TestCase):
    def test_a_fixture_that_got_out_of_a_denied_environment(self) -> None:
        # The denial is the environment's, so the leg has to notice one that
        # stopped denying. Without this the leg would report on a namespace it
        # never confirmed.
        patched = outside_a_suite_run()
        try:
            with (
                posix(),
                denied(),
                mock.patch.object(network, "ask", return_value=ran(0, "it got out")),
            ):
                verdict = network.run(ROOT)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, gate.REFUSED)
        self.assertIn("opened a connection", verdict.detail)
        self.assertIn("it got out", verdict.detail)

    def test_a_tree_with_the_fixture_missing(self) -> None:
        patched = outside_a_suite_run()
        try:
            with tempfile.TemporaryDirectory() as directory, posix(), denied():
                root = Path(directory)
                (root / suite.SUITE).mkdir()
                verdict = network.run(root)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, gate.REFUSED)
        self.assertIn("is not in the tree", verdict.detail)

    def test_a_suite_that_did_not_pass_under_the_denial(self) -> None:
        patched = outside_a_suite_run()
        try:
            with (
                posix(),
                denied(),
                mock.patch.object(network, "ask", return_value=ran(1)),
                mock.patch.object(
                    suite, "judge", return_value=gate.refused("1 test(s) did not pass")
                ),
                mock.patch.object(suite, "invoke", return_value=ran(1)),
            ):
                verdict = network.run(ROOT)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, gate.REFUSED)
        self.assertIn("did not pass with outbound access denied", verdict.detail)
        self.assertIn("1 test(s) did not pass", verdict.detail)


class TheLegPasses(unittest.TestCase):
    def test_a_denied_environment_whose_suite_passed(self) -> None:
        patched = outside_a_suite_run()
        try:
            with (
                posix(),
                denied(),
                mock.patch.object(network, "ask", return_value=ran(1)),
                mock.patch.object(
                    suite, "judge", return_value=gate.passed("170 test(s) passed")
                ),
                mock.patch.object(suite, "invoke", return_value=ran(0)),
            ):
                verdict = network.run(ROOT)
        finally:
            patched.stop()
        self.assertEqual(verdict.state, gate.PASSED, verdict.detail)
        self.assertIn("nothing got out of this environment", verdict.detail)
        self.assertIn("170 test(s) passed", verdict.detail)

    def test_and_it_says_what_a_green_run_here_does_not_cover(self) -> None:
        # Record 0014 states the bound in its own text rather than leaving the
        # reader to work it out, and the leg says it in the line a reader sees.
        patched = outside_a_suite_run()
        try:
            with (
                posix(),
                denied(),
                mock.patch.object(network, "ask", return_value=ran(1)),
                mock.patch.object(
                    suite, "judge", return_value=gate.passed("170 test(s) passed")
                ),
                mock.patch.object(suite, "invoke", return_value=ran(0)),
            ):
                verdict = network.run(ROOT)
        finally:
            patched.stop()
        self.assertIn("covers the suite and not the library", verdict.detail)


class TheFixtureIsNotCollected(unittest.TestCase):
    def test_no_default_pattern_picks_it_up(self) -> None:
        # By construction rather than by a note somebody has to read. The three
        # contract fixtures are named so that neither unittest discovery nor
        # pytest collects them, which is what keeps them out of `unit tests`.
        self.assertTrue((ROOT / network.FIXTURE).is_file())
        self.assertFalse(network.FIXTURE.name.startswith("test"))
        self.assertFalse(network.FIXTURE.name.endswith("_test.py"))

    def test_and_the_suite_did_not_collect_it(self) -> None:
        loaded = unittest.defaultTestLoader.discover(str(ROOT / suite.SUITE))
        names = {
            test.id().split(".")[0]
            for group in loaded
            for case in group
            for test in case
        }
        self.assertNotIn(network.FIXTURE.stem, names)


if __name__ == "__main__":
    unittest.main()
