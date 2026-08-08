"""The hook leg bites on a hook that carries anything besides the gate verb."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from raumbuch.gate import hook

ROOT = Path(__file__).resolve().parents[1]


def tree(contents: str | None) -> Path:
    directory = Path(tempfile.mkdtemp())
    if contents is not None:
        (directory / hook.HOOK).parent.mkdir(parents=True)
        (directory / hook.HOOK).write_text(contents, encoding="utf-8")
    return directory


class ReadingAShellFile(unittest.TestCase):
    def test_the_shebang_a_comment_and_a_blank_line_carry_nothing(self) -> None:
        text = "#!/bin/sh\n\n# why this exists\nexec python3 -m raumbuch gate\n"
        self.assertEqual(hook.instructions(text), [hook.COMMAND])

    def test_a_second_instruction_is_read_as_one(self) -> None:
        text = f"#!/bin/sh\necho pushing\n{hook.COMMAND}\n"
        self.assertEqual(hook.instructions(text), ["echo pushing", hook.COMMAND])


class TheLegRefuses(unittest.TestCase):
    def test_a_hook_that_does_one_thing_before_the_gate(self) -> None:
        verdict = hook.run(tree(f"#!/bin/sh\necho pushing\n{hook.COMMAND}\n"))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("echo pushing", verdict.detail)

    def test_a_hook_that_runs_a_leg_itself_instead_of_the_verb(self) -> None:
        verdict = hook.run(tree("#!/bin/sh\nexec python3 -m unittest discover tests\n"))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("something other than the gate verb", verdict.detail)

    def test_a_tree_with_no_hook_in_it(self) -> None:
        verdict = hook.run(tree(None))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("is not in the tree", verdict.detail)


class TheLegPasses(unittest.TestCase):
    def test_on_this_tree(self) -> None:
        verdict = hook.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)

    def test_on_a_hook_that_is_the_command_and_comments(self) -> None:
        verdict = hook.run(tree(f"#!/bin/sh\n# a comment\n{hook.COMMAND}\n"))
        self.assertEqual(verdict.state, "passed", verdict.detail)


if __name__ == "__main__":
    unittest.main()
