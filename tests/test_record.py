"""The loader: what it builds, and what it refuses by name.

Every fixture here is the worked Schwarzschild record with one thing changed,
and the record is read out of `docs/record-format.md` rather than copied. So a
fixture is a plausible mistake against the record this project actually holds,
and a change to that record is a change to what these fixtures are made of.

The corpus proper, one fixture per reason with a near miss beside it stored so
version control cannot normalise the bytes, is issue #38. What is here is the
narrower thing this issue owes: every reason in the loader's enumeration is
reachable, and each fixture triggers the reason it was written for rather than
some other refusal on the way.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from test_expression import ESCAPES

from raumbuch import expression, record, refusal

ROOT = Path(__file__).resolve().parents[1]
RECORD_FORMAT = ROOT / "docs" / "record-format.md"
STEM = "schwarzschild"

SECOND_CHART = """
[[chart]]
name = "interior"
coordinates = ["t", "r", "theta", "phi"]
region = "inside the horizon"
range = ["r > 0", "r < 2*M"]

[[chart.metric]]
i = "t"
j = "t"
value = "-(1 - 2*M/r)"
"""

RELATION = """
[chart.relation]
kind = "extends"
chart = "exterior"
"""


def worked() -> str:
    """The worked record, as the text `docs/record-format.md` carries it."""
    text = RECORD_FORMAT.read_text(encoding="utf-8")
    start = text.index("```toml")
    return text[start + len("```toml") : text.index("```", start + 3)]


def changed(*replacements: tuple[str, str], appended: str = "") -> bytes:
    """The worked record with each replacement made, and a block appended."""
    text = worked()
    for old, new in replacements:
        if old not in text:
            raise AssertionError(f"the worked record no longer carries {old!r}")
        text = text.replace(old, new)
    return (text + appended).encode("utf-8")


def with_metric_value(value: str) -> bytes:
    """The worked record with one metric component replaced by ``value``.

    The replacement goes in as a TOML literal string, so a value carrying a
    quotation mark reaches the loader as the bytes somebody wrote rather than
    as a TOML parse error, which would refuse the fixture before the parser
    ever saw it.
    """
    text = worked().replace('value = "r^2"', f"value = '''{value}'''")
    return text.encode("utf-8")


def verification(state: str, extra: str = "") -> str:
    return f"""
[[verification]]
subject = "petrov_type"
stratum = "generic"
chart = "exterior"
state = "{state}"
{extra}
"""


DERIVED_STAMP = """
command = "raumbuch classify"
commit = "0123456789012345678901234567890123456789"
date = "2026-08-09"
"""

# One fixture per loader reason. The value is what the loader must say, and
# nothing here asserts on the message: the reason is what a caller branches on.
ONE_PER_REASON: dict[str, tuple[bytes, str]] = {
    refusal.NOT_A_DOCUMENT: (
        changed(('schema_version = "1"', 'schema_version = "1')),
        STEM,
    ),
    refusal.FIELD_MISSING: (changed(("dimension = 4\n", "")), STEM),
    refusal.FIELD_OF_THE_WRONG_KIND: (
        changed(("dimension = 4", 'dimension = "4"')),
        STEM,
    ),
    refusal.UNKNOWN_SCHEMA_VERSION: (
        changed(('schema_version = "1"', 'schema_version = "2"')),
        STEM,
    ),
    refusal.ID_IS_NOT_THE_FILENAME: (changed(), "schwarzschild-exterior"),
    refusal.DIMENSION_IS_NOT_FOUR: (changed(("dimension = 4", "dimension = 5")), STEM),
    refusal.NO_GENERIC_STRATUM: (changed(("generic = true", "generic = false")), STEM),
    refusal.TWO_GENERIC_STRATA: (
        changed(
            appended=(
                '\n[[stratum]]\nname = "extremal"\ngeneric = true\n'
                'condition = "M > 0"\n'
            )
        ),
        STEM,
    ),
    refusal.UNDECLARED_IDENTIFIER: (changed(('value = "r^2"', 'value = "R^2"')), STEM),
    refusal.STRATUM_NAMES_AN_UNDECLARED_PARAMETER: (
        changed(('condition = "M > 0"', 'condition = "m > 0"')),
        STEM,
    ),
    refusal.METRIC_INDEX_IS_NOT_A_COORDINATE: (
        changed(('i = "t"\nj = "t"', 'i = "x"\nj = "t"')),
        STEM,
    ),
    refusal.METRIC_COMPONENT_DECLARED_TWICE: (
        changed(appended='\n[[chart.metric]]\ni = "r"\nj = "r"\nvalue = "1"\n'),
        STEM,
    ),
    refusal.METRIC_COMPONENT_TRANSPOSED: (
        changed(
            appended=(
                '\n[[chart.metric]]\ni = "t"\nj = "r"\nvalue = "0"\n'
                '\n[[chart.metric]]\ni = "r"\nj = "t"\nvalue = "0"\n'
            )
        ),
        STEM,
    ),
    refusal.METRIC_COMPONENT_OUT_OF_ORDER: (
        changed(appended='\n[[chart.metric]]\ni = "r"\nj = "t"\nvalue = "0"\n'),
        STEM,
    ),
    refusal.CHART_WITHOUT_A_RELATION: (changed(appended=SECOND_CHART), STEM),
    refusal.CHART_RELATION_OUTSIDE_THE_VOCABULARY: (
        changed(appended=SECOND_CHART + RELATION.replace("extends", "touches")),
        STEM,
    ),
    refusal.CHART_RELATION_NAMES_NO_CHART: (
        changed(appended=SECOND_CHART + RELATION.replace('"exterior"', '"outside"')),
        STEM,
    ),
    refusal.VALUE_NAMES_NO_STRATUM: (
        changed(('stratum = "generic"', 'stratum = "Generic"')),
        STEM,
    ),
    refusal.VALUE_NAMES_NO_CHART: (
        changed(('stratum = "generic"', 'stratum = "generic"\nchart = "interior"')),
        STEM,
    ),
    refusal.SOURCE_KIND_OUTSIDE_THE_VOCABULARY: (
        changed(('source_kind = "secondary"', 'source_kind = "book"')),
        STEM,
    ),
    refusal.VERIFICATION_STATE_OUTSIDE_THE_VOCABULARY: (
        changed(appended=verification("checked")),
        STEM,
    ),
    refusal.RECOMPUTATION_WITH_NO_COMMAND: (
        changed(appended=verification("recomputed")),
        STEM,
    ),
    refusal.PUBLICATION_CHECK_WITH_NO_PUBLICATION: (
        changed(appended=verification("checked_against_publication")),
        STEM,
    ),
    refusal.CROSS_CHECK_WITH_NO_IMPLEMENTATION: (
        changed(appended=verification("cross_checked")),
        STEM,
    ),
    refusal.DERIVED_ENTRY_WITHOUT_ITS_STAMP: (
        changed(
            appended=(
                '\n[[derived]]\nfield = "petrov_type"\nvalue = "D"\n'
                'stratum = "generic"\nchart = "exterior"\n'
            )
        ),
        STEM,
    ),
    refusal.DERIVED_VALUE_WITH_NO_VERIFICATION: (
        changed(
            appended=(
                '\n[[derived]]\nfield = "petrov_type"\nvalue = "D"\n'
                'stratum = "generic"\nchart = "exterior"\n' + DERIVED_STAMP
            )
        ),
        STEM,
    ),
}


class TheWorkedRecordBecomesAnObject(unittest.TestCase):
    def setUp(self) -> None:
        self.record = record.loads(worked().encode("utf-8"), STEM)

    def test_the_asserted_fields_arrive(self) -> None:
        self.assertEqual(self.record.id, "schwarzschild")
        self.assertEqual(self.record.version, 1)
        self.assertEqual(self.record.dimension, 4)
        self.assertEqual(self.record.signature, "-+++")
        self.assertEqual(self.record.parameter_names, frozenset({"M"}))
        self.assertEqual(self.record.stratum_names, frozenset({"generic"}))
        self.assertEqual(self.record.chart_names, frozenset({"exterior"}))

    def test_the_metric_is_keyed_by_the_index_pair(self) -> None:
        metric = self.record.charts[0].metric
        self.assertEqual(
            sorted(metric), [("phi", "phi"), ("r", "r"), ("t", "t"), ("theta", "theta")]
        )

    def test_a_metric_component_is_a_tree_and_not_a_string(self) -> None:
        component = self.record.charts[0].metric[("theta", "theta")]
        self.assertEqual(component, expression.Power(expression.Name("r"), 2))

    def test_the_coordinate_ranges_are_conditions(self) -> None:
        chart = self.record.charts[0]
        self.assertEqual(len(chart.ranges), 5)
        for condition in chart.ranges:
            with self.subTest(condition=condition):
                self.assertIsInstance(condition, expression.Comparison)

    def test_the_claimed_block_is_carried_and_not_interpreted(self) -> None:
        fields = [entry["field"] for entry in self.record.claimed]
        self.assertEqual(fields, ["petrov_type", "ricci_type", "killing_dimension"])

    def test_nothing_was_computed_so_the_derived_block_is_empty(self) -> None:
        self.assertEqual(self.record.derived, ())
        self.assertEqual(self.record.verification, ())


class EveryReasonIsReachable(unittest.TestCase):
    def test_each_fixture_triggers_the_reason_it_was_written_for(self) -> None:
        for reason, (data, stem) in ONE_PER_REASON.items():
            with self.subTest(reason=reason):
                with self.assertRaises(refusal.Refused) as refused:
                    record.loads(data, stem)
                self.assertEqual(refused.exception.reason, reason)

    def test_every_declared_loader_reason_has_a_fixture(self) -> None:
        self.assertEqual(set(ONE_PER_REASON), set(refusal.LOADER_REASONS))

    def test_a_reason_belongs_to_the_parser_or_to_the_loader_and_not_to_both(
        self,
    ) -> None:
        self.assertEqual(
            set(refusal.PARSER_REASONS) & set(refusal.LOADER_REASONS), set()
        )
        self.assertEqual(
            set(refusal.REASONS),
            set(refusal.PARSER_REASONS) | set(refusal.LOADER_REASONS),
        )


class LoadingExecutesNothing(unittest.TestCase):
    """The fixture that would execute if it could, shared with issue #40.

    The escape corpus lives in `tests/test_expression.py` and this reads it
    rather than writing a second one, because two corpora drift and the shape
    somebody adds to one is the shape the other never learns about.
    """

    def test_a_metric_component_that_would_run_something_is_refused(self) -> None:
        sentinel = Path(__file__).resolve().parent / "loading-executed-something"
        self.assertFalse(sentinel.exists())
        attempt = f"__import__('os').system('echo x > {sentinel.name}')"
        with self.assertRaises(refusal.Refused) as refused:
            record.loads(with_metric_value(attempt), STEM)
        self.assertEqual(refused.exception.reason, refusal.UNKNOWN_CHARACTER)
        self.assertFalse(sentinel.exists())

    def test_every_escape_shape_is_refused_through_the_loader_too(self) -> None:
        for escape, reason in ESCAPES.items():
            with self.subTest(escape=escape):
                with self.assertRaises(refusal.Refused) as refused:
                    record.loads(with_metric_value(escape), STEM)
                self.assertEqual(refused.exception.reason, reason)


if __name__ == "__main__":
    unittest.main()
