"""The headless leg refuses an environment that is not the one it describes.

Nothing here opens a display and nothing here asks for elevation. The fixtures
that do both are run by the leg, and what is tested here is what the leg decides
from what they answer, which is the part that can be wrong without anybody
noticing.
"""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from raumbuch.gate import headless

ROOT = Path(__file__).resolve().parents[1]
# Built here rather than inside the patch below: a Path is constructed for
# the platform os.name names at the moment it is built, and the patch says
# posix on a machine that is not.
NOWHERE = ROOT / "no-such-tree"

POSIX = mock.patch.object(os, "name", "posix")


def answered(returncode: int):
    completed = subprocess.CompletedProcess(args=["fixture"], returncode=returncode)
    return mock.patch.object(headless, "ask", return_value=completed)


def unprivileged():
    return mock.patch.object(headless, "privileged", return_value=False)


class WhereTheContractIsNotAbout(unittest.TestCase):
    def test_off_posix_the_leg_does_not_run_and_asks_for_nothing(self) -> None:
        with (
            mock.patch.object(os, "name", "nt"),
            mock.patch.object(headless, "ask") as asked,
        ):
            verdict = headless.run(ROOT)
        asked.assert_not_called()
        self.assertEqual(verdict.state, "not run")
        self.assertIn("consent dialog", verdict.detail)

    def test_with_a_display_attached_the_leg_does_not_run(self) -> None:
        with (
            POSIX,
            mock.patch.dict(os.environ, {"DISPLAY": ":0"}),
            mock.patch.object(headless, "ask") as asked,
        ):
            verdict = headless.run(ROOT)
        asked.assert_not_called()
        self.assertEqual(verdict.state, "not run")
        self.assertIn("DISPLAY", verdict.detail)


class TheLegRefuses(unittest.TestCase):
    def test_a_process_that_is_already_the_superuser(self) -> None:
        with (
            POSIX,
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch.object(headless, "privileged", return_value=True),
        ):
            verdict = headless.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("superuser", verdict.detail)

    def test_an_environment_where_a_display_can_be_opened(self) -> None:
        with (
            POSIX,
            mock.patch.dict(os.environ, {}, clear=True),
            unprivileged(),
            answered(0),
        ):
            verdict = headless.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("opened a display", verdict.detail)

    def test_an_environment_where_elevation_is_granted(self) -> None:
        answers = [
            subprocess.CompletedProcess(["display"], 1),
            subprocess.CompletedProcess(["elevation"], 0),
        ]
        with (
            POSIX,
            mock.patch.dict(os.environ, {}, clear=True),
            unprivileged(),
            mock.patch.object(headless, "ask", side_effect=answers),
        ):
            verdict = headless.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("granted elevation", verdict.detail)

    def test_an_elevation_fixture_that_declined_to_ask_on_posix(self) -> None:
        answers = [
            subprocess.CompletedProcess(["display"], 1),
            subprocess.CompletedProcess(["elevation"], headless.NOT_ASKED),
        ]
        with (
            POSIX,
            mock.patch.dict(os.environ, {}, clear=True),
            unprivileged(),
            mock.patch.object(headless, "ask", side_effect=answers),
        ):
            verdict = headless.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)

    def test_an_environment_with_no_toolkit_is_not_read_as_a_refusal(self) -> None:
        # It is not a refusal either: nothing was asked, so nothing was refused,
        # and the job that has to cover this leg requires it rather than reading
        # this line as a pass.
        with (
            POSIX,
            mock.patch.dict(os.environ, {}, clear=True),
            unprivileged(),
            answered(headless.CANNOT_ASK),
        ):
            verdict = headless.run(ROOT)
        self.assertEqual(verdict.state, "not run")
        self.assertIn("no toolkit to ask with", verdict.detail)
        self.assertIn("costs", verdict.detail)

    def test_a_tree_with_the_fixtures_missing(self) -> None:
        with POSIX, mock.patch.dict(os.environ, {}, clear=True), unprivileged():
            verdict = headless.run(NOWHERE)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("contract_display.py", verdict.detail)


class TheLegPasses(unittest.TestCase):
    def test_when_both_requests_are_refused(self) -> None:
        with (
            POSIX,
            mock.patch.dict(os.environ, {}, clear=True),
            unprivileged(),
            answered(1),
        ):
            verdict = headless.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("elevation was not granted", verdict.detail)


class TheFixturesAreInTheTree(unittest.TestCase):
    def test_both_of_them(self) -> None:
        for fixture in (headless.DISPLAY_FIXTURE, headless.ELEVATION_FIXTURE):
            self.assertTrue((ROOT / fixture).is_file(), fixture.as_posix())

    def test_neither_is_collected_by_the_suite(self) -> None:
        # Excluded by construction rather than by a note somewhere: the default
        # pattern of both runners is a name beginning with `test`.
        for fixture in (headless.DISPLAY_FIXTURE, headless.ELEVATION_FIXTURE):
            self.assertFalse(fixture.name.startswith("test"), fixture.as_posix())


if __name__ == "__main__":
    unittest.main()
