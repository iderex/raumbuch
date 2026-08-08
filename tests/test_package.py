"""The package and the placeholder module import, and the verb is reachable."""

from __future__ import annotations

import contextlib
import io
import unittest

import raumbuch
import raumbuch.algebra
from raumbuch import cli


class ThePackage(unittest.TestCase):
    def test_it_carries_a_version(self) -> None:
        self.assertIsInstance(raumbuch.__version__, str)
        self.assertTrue(raumbuch.__version__)


class TheAlgebraBoundary(unittest.TestCase):
    def test_the_placeholder_imports_and_declares_nothing_yet(self) -> None:
        self.assertEqual(raumbuch.algebra.__all__, ())


class TheEntryPoint(unittest.TestCase):
    def test_the_gate_verb_is_the_one_verb_that_exists(self) -> None:
        # argparse writes its refusal to stderr, which is held here so that a
        # passing suite prints nothing a reader has to decide is not a failure.
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.parser().parse_args(["classify"])

    def test_the_gate_verb_parses_and_takes_a_root(self) -> None:
        arguments = cli.parser().parse_args(["gate", "--root", "somewhere"])
        self.assertEqual(arguments.verb, "gate")
        self.assertEqual(str(arguments.root), "somewhere")


if __name__ == "__main__":
    unittest.main()
