"""The format and lint legs refuse, and say what the tool found.

The tool itself is not re-tested here. What is tested is the three things the
leg decides on top of it: a clean tree passes, a tree the tool objects to is
refused, and a tool that could not judge is refused rather than read as clean.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest import mock

from raumbuch.gate import formatting, linting, tool

ROOT = Path(__file__).resolve().parents[1]

REFORMAT = """unformatted: File would be reformatted
 --> src/raumbuch/cli.py:1:3
  |
  - x   =  1
  |
1 file would be reformatted, 11 files already formatted
"""

FINDINGS = """src/raumbuch/cli.py:22:89: E501 Line too long (89 > 88)
src/raumbuch/gate/layout.py:56:89: E501 Line too long (91 > 88)
Found 2 errors.
"""


def tool_says(returncode: int, stdout: str = "", stderr: str = ""):
    """The tool, installed, answering exactly this.

    Both halves are patched. A leg asks whether the tool is there before it asks
    it anything, so a fixture that answers without being installed tests a
    branch the leg never reaches, and the suite would then pass where the tool
    is absent and fail where it is present.
    """
    completed = subprocess.CompletedProcess(
        args=["ruff"], returncode=returncode, stdout=stdout, stderr=stderr
    )
    return mock.patch.multiple(
        tool,
        invoke=mock.Mock(return_value=completed),
        installed=mock.Mock(return_value=True),
    )


class TheFormatLeg(unittest.TestCase):
    def test_it_refuses_a_tree_the_formatter_would_change(self) -> None:
        with tool_says(1, REFORMAT):
            verdict = formatting.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("would change 1 file(s)", verdict.detail)
        self.assertIn("src/raumbuch/cli.py", verdict.detail)

    def test_it_names_the_repair_rather_than_making_it(self) -> None:
        with tool_says(1, REFORMAT):
            verdict = formatting.run(ROOT)
        self.assertIn(formatting.REPAIR, verdict.detail)

    def test_a_tool_that_could_not_judge_is_refused_not_read_as_clean(self) -> None:
        with tool_says(2, "", "error: invalid rule selector"):
            verdict = formatting.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)

    def test_a_clean_tree_passes(self) -> None:
        with tool_says(0, "12 files already formatted\n"):
            verdict = formatting.run(ROOT)
        self.assertEqual(verdict.state, "passed")

    def test_an_absent_tool_is_reported_not_passed(self) -> None:
        with mock.patch.object(tool, "installed", return_value=False):
            verdict = formatting.run(ROOT)
        self.assertEqual(verdict.state, "not run")
        self.assertIn(tool.INSTALL, verdict.detail)


class TheLintLeg(unittest.TestCase):
    def test_it_refuses_a_tree_with_findings_and_carries_them(self) -> None:
        with tool_says(1, FINDINGS):
            verdict = linting.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("2 finding(s)", verdict.detail)
        self.assertIn("E501", verdict.detail)

    def test_the_tool_s_own_count_line_is_not_read_as_a_finding(self) -> None:
        with tool_says(1, FINDINGS):
            verdict = linting.run(ROOT)
        self.assertNotIn("Found 2 errors", verdict.detail)

    def test_a_tool_that_could_not_judge_is_refused_not_read_as_clean(self) -> None:
        with tool_says(2, "", "error: unknown rule"):
            verdict = linting.run(ROOT)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)

    def test_a_clean_tree_passes(self) -> None:
        with tool_says(0, "All checks passed!\n"):
            verdict = linting.run(ROOT)
        self.assertEqual(verdict.state, "passed")

    def test_an_absent_tool_is_reported_not_passed(self) -> None:
        with mock.patch.object(tool, "installed", return_value=False):
            verdict = linting.run(ROOT)
        self.assertEqual(verdict.state, "not run")
        self.assertIn("lints", verdict.detail)


class ReadingWhatTheFormatterPrinted(unittest.TestCase):
    def test_each_file_is_named_once_however_many_changes_it_carries(self) -> None:
        lines = tool.output(
            subprocess.CompletedProcess(["ruff"], 1, REFORMAT + REFORMAT, "")
        )
        self.assertEqual(formatting.reformatted(lines), ["src/raumbuch/cli.py"])


if __name__ == "__main__":
    unittest.main()
