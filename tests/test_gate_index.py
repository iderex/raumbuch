"""The index leg bites, and it bites for the reason it names.

The refusals themselves are proved in `test_catalogue.py`, against the module
that decides them. What is proved here is the leg: that a refused catalogue
reaches the gate as a refusal carrying which record and which reason, that an
absent directory fails closed rather than reading as a catalogue with nothing
wrong in it, and that the count a passing run prints is the count it read.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import catalogue_corpus

from raumbuch import catalogue
from raumbuch.gate import index

ROOT = Path(__file__).resolve().parents[1]


def tree(root: Path, half: catalogue_corpus.Half) -> None:
    directory = root / catalogue.DIRECTORY
    for source, data in half.decoded():
        path = directory / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


class TheLegRefuses(unittest.TestCase):
    def test_a_catalogue_spending_one_id_twice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, catalogue_corpus.FIXTURES["id-carried-by-two-records"].refused)
            verdict = index.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("id-carried-by-two-records", verdict.detail)
        self.assertIn("kerr", verdict.detail)

    def test_a_supersession_written_from_one_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, catalogue_corpus.FIXTURES["half-written-supersession"].refused)
            verdict = index.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("half-written-supersession", verdict.detail)

    def test_a_correction_list_with_a_gap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                catalogue_corpus.FIXTURES[
                    "correction-list-does-not-run-to-the-version"
                ].refused,
            )
            verdict = index.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("correction-list-does-not-run-to-the-version", verdict.detail)

    def test_a_tree_with_no_catalogue_directory_fails_closed(self) -> None:
        """Absent is not empty, and reading it as empty is a green run over nothing."""
        with tempfile.TemporaryDirectory() as directory:
            verdict = index.run(Path(directory))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)


class TheLegPasses(unittest.TestCase):
    def test_a_catalogue_whose_links_are_written_both_ways(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, catalogue_corpus.FIXTURES["half-written-supersession"].accepted)
            verdict = index.run(root)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("2 record(s)", verdict.detail)
        self.assertIn("1 of them superseded", verdict.detail)

    def test_the_count_it_prints_is_the_count_it_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, catalogue_corpus.FIXTURES["id-carried-by-two-records"].accepted)
            verdict = index.run(root)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("2 record(s)", verdict.detail)
        self.assertIn("0 of them superseded", verdict.detail)

    def test_on_this_tree(self) -> None:
        """Which holds no entry until issue #73, and the run says the number."""
        verdict = index.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("record(s)", verdict.detail)


if __name__ == "__main__":
    unittest.main()
