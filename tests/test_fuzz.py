"""The fuzz harness finds what it claims to, and what it found stays found.

Two halves, and the second is what makes the first worth having. Every crasher
the harness has produced is kept here as the input that produced it, and each
one is asked for the reason it is refused by rather than only for the absence of
a traceback: a crasher repaired into a different crash would otherwise read as
fixed. And every target is run against a component that breaks the property it
watches, because a watcher nobody has seen report anything is a watcher that may
report nothing.

The `nothing-executes` target installs an audit hook, which cannot be taken off
again once it is on. Everything about that target therefore happens in a
subprocess, so the interpreter that goes on to judge the rest of the suite is
not the one carrying it.
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

import fuzz

from raumbuch import expression, refusal

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent

# What the suite can afford on every run. The scheduled workflow is where the
# budget is large; this is the size that keeps the unit suite a unit suite.
ROUNDS = 300


def environment() -> dict[str, str]:
    variables = dict(os.environ)
    existing = variables.get("PYTHONPATH")
    source = str(ROOT / "src")
    variables["PYTHONPATH"] = f"{source}{os.pathsep}{existing}" if existing else source
    return variables


def apart(program: str) -> subprocess.CompletedProcess[str]:
    """Run a program in its own interpreter, out of the tests directory."""
    return subprocess.run(
        [sys.executable, "-c", program],
        cwd=HERE,
        env=environment(),
        capture_output=True,
        text=True,
        check=False,
    )


class EveryCrasherStaysFixed(unittest.TestCase):
    def test_each_one_is_refused_by_the_reason_it_is_recorded_under(self) -> None:
        for name, crasher in fuzz.CRASHERS.items():
            if not crasher.reason:
                continue
            with self.subTest(crasher=name):
                with self.assertRaises(refusal.Refused) as raised:
                    fuzz.read(crasher.kind, crasher.data())
                self.assertEqual(raised.exception.reason, crasher.reason)

    def test_the_one_that_is_legal_input_returns_instead(self) -> None:
        # A sum long enough to exhaust a recursive walker is not a record
        # anybody should be refused for writing. The repair there is that
        # reading it returns, so this crasher carries no reason and this is
        # the assertion that it is the other kind.
        crasher = fuzz.CRASHERS["a-sum-longer-than-the-walker-recurses"]
        self.assertEqual(crasher.reason, "")
        node = fuzz.read(crasher.kind, crasher.data())
        self.assertIsInstance(node, expression.Operation)

    def test_no_two_of_them_are_the_same_input(self) -> None:
        encoded = [crasher.encoded for crasher in fuzz.CRASHERS.values()]
        self.assertEqual(len(encoded), len(set(encoded)))


class TheGeneratorIsReproducible(unittest.TestCase):
    def test_one_seed_produces_one_list(self) -> None:
        self.assertEqual(fuzz.inputs(7, 50), fuzz.inputs(7, 50))

    def test_another_seed_produces_another(self) -> None:
        self.assertNotEqual(fuzz.inputs(7, 50), fuzz.inputs(8, 50))

    def test_the_corpus_is_in_it_before_any_mutation(self) -> None:
        # The seeds are the refusal fixtures and the near misses beside them.
        # A generator that started from nothing would spend its budget
        # rediscovering what a record looks like.
        self.assertEqual(fuzz.inputs(0, 0), fuzz.seeds())
        self.assertGreater(len(fuzz.seeds()), len(fuzz.EXPRESSION_SEEDS))


class TheTargetsBite(unittest.TestCase):
    def test_nothing_crashes_reports_an_exception_that_is_not_a_refusal(self) -> None:
        kept = fuzz.read
        try:
            fuzz.read = _raising(ZeroDivisionError("no"))
            report = fuzz.nothing_crashes([("expression", b"1")])
        finally:
            fuzz.read = kept
        self.assertEqual(len(report.failures), 1)
        self.assertIn("ZeroDivisionError", report.failures[0])

    def test_and_passes_the_same_component_refusing_by_name(self) -> None:
        # The near miss of the test above, one exception class apart. A
        # refusal from the closed vocabulary is the outcome this target is
        # written to admit, so a target reporting it would report every
        # fixture in the corpus.
        kept = fuzz.read
        try:
            fuzz.read = _raising(refusal.Refused(refusal.UNKNOWN_CHARACTER, "no"))
            report = fuzz.nothing_crashes([("expression", b"1")])
        finally:
            fuzz.read = kept
        self.assertEqual(report.failures, [])

    def test_grammar_containment_reports_a_function_outside_the_list(self) -> None:
        kept = fuzz.read
        try:
            fuzz.read = _returning(
                expression.Apply("system", expression.Name("x")),
            )
            report = fuzz.grammar_containment([("expression", b"1")])
        finally:
            fuzz.read = kept
        self.assertEqual(len(report.failures), 1)
        self.assertIn("'system'", report.failures[0])

    def test_grammar_containment_reports_a_node_of_a_foreign_kind(self) -> None:
        kept = fuzz.read
        try:
            fuzz.read = _returning(expression.Negate("a string, not a node"))
            report = fuzz.grammar_containment([("expression", b"1")])
        finally:
            fuzz.read = kept
        self.assertEqual(len(report.failures), 1)
        self.assertIn("str in a tree", report.failures[0])

    def test_memory_is_bounded_reports_a_tree_larger_than_its_text(self) -> None:
        deep = expression.Name("x")
        for _ in range(10):
            deep = expression.Negate(deep)
        kept = fuzz.read
        try:
            fuzz.read = _returning(deep)
            report = fuzz.memory_is_bounded([("expression", b"x")])
        finally:
            fuzz.read = kept
        self.assertEqual(len(report.failures), 1)
        self.assertIn("11 node(s) out of 1 character(s)", report.failures[0])

    def test_nothing_executes_reports_a_component_that_compiles_something(self) -> None:
        # In a subprocess, because the hook this target installs stays
        # installed. The stub compiles a string, which is the shortest thing a
        # loader could do that would mean a record had run.
        result = apart(
            "import fuzz\n"
            "fuzz.read = lambda kind, data: compile('1', '<record>', 'eval')\n"
            "report = fuzz.nothing_executes([('record', b'x')])\n"
            "print(report.failures)\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("compile", result.stdout)


class TheCampaignIsClean(unittest.TestCase):
    def test_on_this_tree(self) -> None:
        result = apart(
            f"import fuzz, sys\nsys.exit(fuzz.main(['--seed', '0', "
            f"'--rounds', '{ROUNDS}']))\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for target in fuzz.TARGETS:
            self.assertIn(f"{target}: ", result.stdout)
        self.assertNotIn("failure(s)", result.stdout)


def _raising(error: BaseException):
    def read(kind: str, data: bytes) -> object:
        raise error

    return read


def _returning(value: object):
    def read(kind: str, data: bytes) -> object:
        return value

    return read


if __name__ == "__main__":
    unittest.main()
