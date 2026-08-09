"""The determinism leg bites, and it bites for the reason it names.

The important test here is the second class. A replay check that has never been
shown to fail is a check nobody has run against a violation, which record 0012
says of this issue by name, so the fixture whose output depends on iteration
order is driven through the real leg rather than described.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from raumbuch.gate import determinism

ROOT = Path(__file__).resolve().parents[1]


class TheLegPassesOnThisTree(unittest.TestCase):
    def test_the_declared_inputs_replay_to_the_same_thing(self) -> None:
        verdict = determinism.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)

    def test_the_report_names_both_runs_so_the_variation_is_in_the_log(
        self,
    ) -> None:
        verdict = determinism.run(ROOT)
        for seed, workers in determinism.RUNS:
            self.assertIn(f"hash seed {seed}", verdict.detail)
            self.assertIn(f"{workers} worker(s)", verdict.detail)

    def test_the_report_names_the_excluded_fields(self) -> None:
        verdict = determinism.run(ROOT)
        for field in determinism.EXCLUDED:
            self.assertIn(field, verdict.detail)


class TheRunsAreWhatRecord0012Requires(unittest.TestCase):
    def test_the_hash_seed_is_varied(self) -> None:
        seeds = {seed for seed, _ in determinism.RUNS}
        self.assertGreater(len(seeds), 1)

    def test_more_than_one_worker_runs_in_at_least_one_of_them(self) -> None:
        """Two single-threaded runs agree for reasons that are not the property.

        Record 0012 asks for this outright, because a check made of two
        single-threaded runs would pass on a tree that violated the property
        everywhere.
        """
        self.assertTrue(any(workers > 1 for _, workers in determinism.RUNS))

    def test_the_worker_count_is_varied_too(self) -> None:
        counts = {workers for _, workers in determinism.RUNS}
        self.assertGreater(len(counts), 1)


class TheFixtureThatDependsOnIterationOrderReddensIt(unittest.TestCase):
    def test_the_leg_refuses_it(self) -> None:
        verdict = determinism.replay(ROOT, ("native-order",))
        self.assertEqual(verdict.state, "refused")

    def test_the_refusal_names_the_first_differing_line_and_not_the_whole_run(
        self,
    ) -> None:
        verdict = determinism.replay(ROOT, ("native-order",))
        differing = [
            line for line in verdict.detail.splitlines() if line.startswith(("+", "-"))
        ]
        self.assertEqual(len(differing), 1)
        self.assertIn("coordinate-", differing[0])

    def test_it_is_not_one_of_the_inputs_the_leg_replays(self) -> None:
        """It stays in the tree and out of the run, which is the whole point.

        A fixture that violates the property cannot be one of the inputs the gate
        replays, or the gate is red for ever. It is declared beside them, reached
        by name, and the test above is what runs it.
        """
        self.assertNotIn("native-order", determinism.INPUTS)
        self.assertIn("native-order", determinism.RENDERERS)

    def test_the_fixture_carries_enough_keys_to_fail_reliably(self) -> None:
        """A set of two reorders under a new seed only sometimes.

        Twelve names means two seeds agree only if one permutation out of twelve
        factorial recurs. The number is in the fixture's own docstring with the
        reasoning, and this is what stops somebody shrinking it to a pair while
        tidying up and turning the proof into a flake.
        """
        rendered = determinism.native_order(ROOT)
        self.assertGreaterEqual(len(rendered.split()), 12)


class TheComparisonExcludesWhatRecord0012PutsOutsideThePromise(unittest.TestCase):
    def test_an_excluded_field_is_dropped_before_the_comparison(self) -> None:
        text = "a.date = one\nprovenance.transcribed_on = two\nid = three"
        self.assertEqual(determinism.compared(text), ["id = three"])

    def test_a_field_that_is_not_excluded_survives(self) -> None:
        self.assertEqual(determinism.compared("version = 1"), ["version = 1"])

    def test_the_exclusions_are_a_list_in_the_check(self) -> None:
        """Record 0012 asks for a list rather than a rule a reader rebuilds."""
        self.assertEqual(determinism.EXCLUDED, ("date", "transcribed_on", "cost"))


if __name__ == "__main__":
    unittest.main()
