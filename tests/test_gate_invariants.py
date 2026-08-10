"""Every pattern bites, and each fixture reddens only its own.

The second half of that sentence is what carries the weight. A fixture that trips
three patterns at once proves that something refused it and says nothing about
which rule did the refusing, so every fixture below is compared against the set
of pattern names it triggered rather than against the fact of a refusal.

Each fixture is a tree of two files: one under `src/raumbuch/` and one under
`tests/`, because the patterns differ in which of those they are about. The near
miss beside each is the same tree with the one thing removed, which is the
mistake somebody makes on the line before.

The fixture bodies are written here rather than base64 because what they are
about is a name in a line of code, not a byte a checkout might normalise. That
is the same reason `test_record.py` writes its substitutions in the open.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from raumbuch.gate import invariants

ROOT = Path(__file__).resolve().parents[1]

CLEAN = '"""A module carrying none of the three patterns."""\n\nCOUNT = 4\n'


def tree(files: dict[str, str]) -> Path:
    """A checkout carrying `src/raumbuch/` and `tests/`, plus the named files."""
    directory = tempfile.mkdtemp()
    root = Path(directory)
    (root / "src" / "raumbuch").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "src" / "raumbuch" / "clean.py").write_text(CLEAN, encoding="utf-8")
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def triggered(files: dict[str, str]) -> set[str]:
    """Which patterns this tree trips, by name. Empty where it trips none."""
    root = tree(files)
    return {line.split(":", 1)[0] for line in invariants.faults(root)}


#: One file per pattern, each one thing away from the clean module above.
BOUNDARY = '"""A module reaching past the boundary."""\n\nfrom sympy import Symbol\n'
FLOAT = '"""A module branching on a float."""\n\nTOLERANCE = 1e-9\n'
OUTBOUND = '"""A module that can reach out."""\n\nimport urllib.request\n'

#: The near miss beside each, one plausible step short of the refusal.
BOUNDARY_NEAR = (
    '"""A module reaching for the interface rather than past it."""\n\n'
    "from raumbuch.algebra import reduce\n"
)
FLOAT_NEAR = (
    '"""A module with the exact quotient instead."""\n\nTOLERANCE = 1 / 1000000000\n'
)
OUTBOUND_NEAR = '"""A module reading a file instead."""\n\nimport pathlib\n'


class EveryPatternNamesItsRecord(unittest.TestCase):
    def test_no_pattern_is_without_one(self) -> None:
        for pattern in invariants.PATTERNS:
            with self.subTest(pattern=pattern.name):
                self.assertRegex(pattern.record, r"^[0-9]{4}$")
                self.assertTrue(
                    (ROOT / "docs" / "decisions").glob(f"{pattern.record}-*.md")
                )

    def test_the_record_it_names_is_in_the_tree(self) -> None:
        for pattern in invariants.PATTERNS:
            with self.subTest(pattern=pattern.name):
                found = sorted(
                    (ROOT / "docs" / "decisions").glob(f"{pattern.record}-*.md")
                )
                self.assertEqual(len(found), 1, found)

    def test_every_pattern_says_what_it_refuses(self) -> None:
        for pattern in invariants.PATTERNS:
            with self.subTest(pattern=pattern.name):
                self.assertTrue(pattern.refuses.strip())

    def test_no_two_patterns_share_a_name(self) -> None:
        names = [pattern.name for pattern in invariants.PATTERNS]
        self.assertEqual(len(names), len(set(names)))


class EachFixtureRedddensOnlyItsOwnPattern(unittest.TestCase):
    def test_the_symbolic_layer_outside_its_boundary(self) -> None:
        self.assertEqual(
            triggered({"src/raumbuch/curvature.py": BOUNDARY}),
            {"symbolic-layer-outside-its-boundary"},
        )

    def test_floating_point_in_a_decision_path(self) -> None:
        self.assertEqual(
            triggered({"src/raumbuch/curvature.py": FLOAT}),
            {"floating-point-in-a-decision-path"},
        )

    def test_a_module_that_reaches_the_network(self) -> None:
        self.assertEqual(
            triggered({"src/raumbuch/curvature.py": OUTBOUND}),
            {"network-outside-the-harness-allowed-one"},
        )

    def test_the_network_pattern_is_about_the_suite_as_well(self) -> None:
        """Record 0014: the test suite makes no connection either."""
        self.assertEqual(
            triggered({"tests/test_curvature.py": OUTBOUND}),
            {"network-outside-the-harness-allowed-one"},
        )


class TheNearMissBesideEachIsAccepted(unittest.TestCase):
    def test_the_interface_rather_than_the_library_behind_it(self) -> None:
        self.assertEqual(triggered({"src/raumbuch/curvature.py": BOUNDARY_NEAR}), set())

    def test_the_exact_quotient_rather_than_the_float(self) -> None:
        self.assertEqual(triggered({"src/raumbuch/curvature.py": FLOAT_NEAR}), set())

    def test_reading_a_file_rather_than_a_socket(self) -> None:
        self.assertEqual(triggered({"src/raumbuch/curvature.py": OUTBOUND_NEAR}), set())


class TheSubjectOfEachPatternIsWhereTheRecordPutIt(unittest.TestCase):
    def test_the_algebra_directory_may_name_the_symbolic_layer(self) -> None:
        """Record 0001 puts the boundary at that directory, so this is not a fault."""
        self.assertEqual(
            triggered({"src/raumbuch/algebra/backend.py": BOUNDARY}), set()
        )

    def test_the_network_harness_may_reach_for_a_socket(self) -> None:
        """Two files exist to prove there is no route, and both need one to try."""
        self.assertEqual(
            triggered(
                {
                    "src/raumbuch/gate/network.py": OUTBOUND,
                    "tests/contract_network.py": OUTBOUND,
                }
            ),
            set(),
        )

    def test_a_decimal_point_in_a_message_is_not_arithmetic(self) -> None:
        """The parser's refusal names a decimal in the sentence that refuses it."""
        message = (
            '"""A module refusing a decimal."""\n\n'
            'REASON = "a decimal point: write 1/2 rather than 0.5"\n'
        )
        self.assertEqual(triggered({"src/raumbuch/curvature.py": message}), set())

    def test_a_file_that_does_not_tokenise_is_left_to_the_build_leg(self) -> None:
        broken = '"""A module that does not parse."""\n\ndef missing(\n'
        self.assertEqual(triggered({"src/raumbuch/curvature.py": broken}), set())


class TheLegItself(unittest.TestCase):
    def test_it_refuses_and_names_the_record(self) -> None:
        root = tree({"src/raumbuch/curvature.py": FLOAT})
        verdict = invariants.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("record 0009", verdict.detail)
        self.assertIn("curvature.py", verdict.detail)

    def test_a_tree_with_no_source_directory_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verdict = invariants.run(Path(directory))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)

    def test_it_passes_on_this_tree_and_says_what_it_excluded(self) -> None:
        verdict = invariants.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("0001, 0009, 0014", verdict.detail)
        self.assertIn("2 file(s) that declare and exercise them", verdict.detail)

    def test_the_files_it_excludes_are_in_the_tree(self) -> None:
        """An exclusion naming a path that moved is an exclusion nobody notices."""
        for path in invariants.ITSELF:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
