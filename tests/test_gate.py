"""The gate runs its legs in order, stops at the first refusal, and says so."""

from __future__ import annotations

import io
import unittest
from pathlib import Path

from raumbuch import gate

ROOT = Path(__file__).resolve().parents[1]


def leg(name: str, verdict: gate.Verdict, seen: list[str]) -> gate.Leg:
    def run(root: Path) -> gate.Verdict:
        seen.append(name)
        return verdict

    return gate.Leg(name, run)


class LegsRunInOrder(unittest.TestCase):
    def test_every_declared_leg_runs_when_none_refuses(self) -> None:
        seen: list[str] = []
        legs = (
            leg("first", gate.passed("held"), seen),
            leg("second", gate.passed("held"), seen),
        )
        results = gate.run(ROOT, legs)
        self.assertEqual(seen, ["first", "second"])
        self.assertEqual(
            [verdict.state for _, verdict in results], ["passed", "passed"]
        )

    def test_a_refusal_stops_the_run_and_the_rest_is_reported_not_dropped(self) -> None:
        seen: list[str] = []
        legs = (
            leg("first", gate.refused("a fixture refusal"), seen),
            leg("second", gate.passed("held"), seen),
        )
        results = gate.run(ROOT, legs)
        self.assertEqual(seen, ["first"], "the leg after a refusal must not run")
        self.assertEqual(
            [verdict.state for _, verdict in results], ["refused", "not run"]
        )
        self.assertIn("the gate stopped at first", results[1][1].detail)
        self.assertIn("running the gate again", results[1][1].detail)


class TheReportSaysWhatItExamined(unittest.TestCase):
    def test_every_leg_appears_with_its_state_and_its_reason(self) -> None:
        seen: list[str] = []
        legs = (
            leg("first", gate.refused("a fixture refusal"), seen),
            leg("second", gate.passed("held"), seen),
        )
        lines = gate.report(ROOT, gate.run(ROOT, legs))
        body = "\n".join(lines)
        for name in ("first", "second"):
            self.assertIn(name, body)
        self.assertIn("a fixture refusal", body)
        self.assertIn("2 leg(s) declared: 0 passed, 1 refused, 1 not run.", lines[-1])

    def test_the_counts_add_up_to_the_legs_declared(self) -> None:
        seen: list[str] = []
        legs = (leg("only", gate.passed("held"), seen),)
        lines = gate.report(ROOT, gate.run(ROOT, legs))
        self.assertIn("1 leg(s) declared: 1 passed, 0 refused, 0 not run.", lines[-1])


class TheExitCode(unittest.TestCase):
    def test_zero_when_every_leg_passed(self) -> None:
        seen: list[str] = []
        legs = (leg("only", gate.passed("held"), seen),)
        self.assertEqual(gate.main(ROOT, legs, out=io.StringIO()), 0)

    def test_non_zero_when_a_leg_refused(self) -> None:
        seen: list[str] = []
        legs = (leg("only", gate.refused("a fixture refusal"), seen),)
        self.assertEqual(gate.main(ROOT, legs, out=io.StringIO()), 1)

    def test_the_report_is_printed_whatever_the_verdict(self) -> None:
        seen: list[str] = []
        out = io.StringIO()
        gate.main(
            ROOT, (leg("only", gate.refused("a fixture refusal"), seen),), out=out
        )
        self.assertIn("a fixture refusal", out.getvalue())


class AskingForOneLeg(unittest.TestCase):
    def test_only_the_asked_for_leg_runs(self) -> None:
        seen: list[str] = []
        legs = (
            leg("first", gate.passed("held"), seen),
            leg("second", gate.passed("held"), seen),
        )
        gate.run(ROOT, legs, only=["second"])
        self.assertEqual(seen, ["second"])

    def test_a_leg_nobody_asked_for_is_reported_and_not_dropped(self) -> None:
        seen: list[str] = []
        legs = (
            leg("first", gate.passed("held"), seen),
            leg("second", gate.passed("held"), seen),
        )
        results = gate.run(ROOT, legs, only=["second"])
        self.assertEqual([leg.name for leg, _ in results], ["first", "second"])
        self.assertEqual(results[0][1].state, "not run")
        self.assertIn("not asked for", results[0][1].detail)
        self.assertIn("--only first", results[0][1].detail)

    def test_a_limited_run_cannot_be_read_as_a_whole_one(self) -> None:
        seen: list[str] = []
        legs = (
            leg("first", gate.passed("held"), seen),
            leg("second", gate.passed("held"), seen),
        )
        lines = gate.report(ROOT, gate.run(ROOT, legs, only=["second"]))
        self.assertIn("2 leg(s) declared: 1 passed, 0 refused, 1 not run.", lines[-1])


class RequiringALeg(unittest.TestCase):
    def test_a_required_leg_that_did_not_run_is_refused(self) -> None:
        seen: list[str] = []
        legs = (
            leg("first", gate.passed("held"), seen),
            leg("second", gate.passed("held"), seen),
        )
        results = gate.run(ROOT, legs, only=["first"], required=["second"])
        self.assertEqual(results[1][1].state, "refused")
        self.assertIn("required second to run and it did not", results[1][1].detail)

    def test_the_reason_it_did_not_run_survives_into_the_refusal(self) -> None:
        seen: list[str] = []
        legs = (leg("only", gate.passed("held"), seen),)
        results = gate.run(ROOT, legs, only=["nothing"], required=["only"])
        self.assertIn("not asked for", results[0][1].detail)

    def test_a_required_leg_that_ran_is_left_alone(self) -> None:
        seen: list[str] = []
        legs = (leg("only", gate.passed("held"), seen),)
        results = gate.run(ROOT, legs, required=["only"])
        self.assertEqual(results[0][1].state, "passed")

    def test_requiring_a_leg_that_refused_changes_nothing(self) -> None:
        seen: list[str] = []
        legs = (leg("only", gate.refused("a fixture refusal"), seen),)
        results = gate.run(ROOT, legs, required=["only"])
        self.assertEqual(results[0][1].detail, "a fixture refusal")


class ADetailOfSeveralLines(unittest.TestCase):
    def test_every_line_of_it_reaches_the_report(self) -> None:
        seen: list[str] = []
        legs = (leg("only", gate.refused("a summary\nand a finding"), seen),)
        lines = gate.report(ROOT, gate.run(ROOT, legs))
        self.assertIn("a summary", lines[1])
        self.assertIn("and a finding", lines[2])


class TheDeclaredLegs(unittest.TestCase):
    def test_no_leg_refuses_this_tree(self) -> None:
        results = gate.run(ROOT)
        refused = [
            (leg.name, verdict.detail)
            for leg, verdict in results
            if verdict.state == "refused"
        ]
        self.assertEqual(refused, [], "the gate must be green on a clean checkout")

    def test_a_leg_that_did_not_run_here_says_why_and_what_running_it_costs(
        self,
    ) -> None:
        # Not every leg can run everywhere. The `headless` leg judges an
        # environment with no display and no privilege, which a developer
        # machine is not, and a run that omitted it in silence would report a
        # contract as met that nothing had asked about.
        for leg, verdict in gate.run(ROOT):
            if verdict.state == "not run":
                self.assertIn("not run", verdict.detail, leg.name)
                self.assertIn("costs", verdict.detail, leg.name)

    def test_no_leg_is_declared_twice(self) -> None:
        names = [leg.name for leg in gate.LEGS]
        self.assertEqual(sorted(names), sorted(set(names)))


if __name__ == "__main__":
    unittest.main()
