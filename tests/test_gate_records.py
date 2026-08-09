"""The records leg bites, once per reason, and it reads its rules off record 0000.

Every fixture below is a directory of its own, and that is not incidental. The
refusals this leg exists for are malformed decision records, and a malformed
decision record inside `docs/decisions/` would redden the check on `main` for as
long as it stayed there. So the checker takes the directory it judges, the
fixtures live in a temporary one, and nothing here depends on an exclusion that
somebody could later remove without noticing what it was holding.

Each fixture departs from the shape in exactly one way, and each test asserts
what the leg said about that one thing and that it said nothing about the
others. A fixture that reddens the check by accident of a second fault proves
that the check is red, which is not the same as proving why.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from raumbuch.gate import records

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / records.DECISIONS

# The shape record, cut down to the two fenced blocks this leg reads out of it
# and the sections record 0000 requires of every record including itself. It is
# a fixture vocabulary rather than a copy of the real record: a fixture judged
# against the tree's own documents proves the state of the tree on the day it
# ran and not the guard.
SHAPE = """# 0000. How a decision is recorded

## Status

Accepted

## Date

2026-08-07

## Question

What shape does a decision record take here?

### The required sections

```
# NNNN. Title
## Status
## Date
## Question
## Answer
## Rejected alternatives
## What depends on this
```

`## Status` holds exactly one of these words or phrases and nothing else:

```
Proposed
Accepted
Superseded by NNNN
```

## Answer

The shape above.

## Rejected alternatives

None, in a fixture.

## What depends on this

The check this file is a fixture for.
"""

WELL_FORMED = """# 0001. A record that is fine

## Status

Accepted

## Date

2026-08-08

## Question

Is this record well formed?

## Answer

It is.

## Rejected alternatives

Being malformed, rejected because the fixtures below already are.

## What depends on this

Nothing.
"""

FINE = "0001-a-record-that-is-fine.md"
ROW = f"| [0001]({FINE}) | A record that is fine | Accepted |\n"
MISSING_ROW = "| [0002](0002-a-record-nobody-wrote.md) | Nobody wrote it | Accepted |\n"

INDEX = (
    """# Decision records

The prose above the table links to record [0000](0000-how-a-decision-is-recorded.md)
as well, which is the index doing its job and not a second row.

| Number | Title | Status |
| --- | --- | --- |
| [0000](0000-how-a-decision-is-recorded.md) | How a decision is recorded | Accepted |
"""
    + ROW
)


def written(directory: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        (directory / name).write_text(text, encoding="utf-8")


def clean() -> dict[str, str]:
    """The smallest set of files this leg passes on."""
    return {
        records.SHAPE: SHAPE,
        FINE: WELL_FORMED,
        records.INDEX: INDEX,
    }


def judged(files: dict[str, str]) -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        written(root, files)
        return records.judge(root)


class TheRulesComeOffRecord0000(unittest.TestCase):
    def test_the_required_sections_are_read_out_of_its_fenced_block(self) -> None:
        self.assertEqual(
            records.required(SHAPE),
            [
                "## Status",
                "## Date",
                "## Question",
                "## Answer",
                "## Rejected alternatives",
                "## What depends on this",
            ],
        )

    def test_the_status_words_are_read_out_of_its_other_one(self) -> None:
        self.assertEqual(
            records.allowed(SHAPE), ["Proposed", "Accepted", "Superseded by NNNN"]
        )

    def test_a_shape_record_whose_block_moved_is_a_refusal_and_not_a_pass(self) -> None:
        # The lists are read rather than copied, so the failure mode of reading
        # is a leg that requires nothing at all. It fails closed instead.
        files = clean()
        files[records.SHAPE] = SHAPE.replace(
            "### The required sections", "### Sections"
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("no required section list could be read", faults[0])


class AFenceIsNotAHeading(unittest.TestCase):
    def test_the_shape_record_passes_the_check_it_specifies(self) -> None:
        # A line scan that ignores fences reads the required section list as
        # seven headings of record 0000 itself and refuses the record that
        # defines what a heading is.
        self.assertEqual(judged(clean()), [])

    def test_and_a_scan_that_ignored_fences_would_see_them_as_sections(self) -> None:
        naive = [line for line in SHAPE.splitlines() if line.startswith("## ")]
        aware = [line for line in records.headings(SHAPE) if line.startswith("## ")]
        self.assertEqual(len(naive), 12)
        self.assertEqual(len(aware), 6)
        # Six sections, each counted twice: once where the record carries it and
        # once where the record specifies it. The duplicates are the six lines of
        # the required section list, which is written inside a fence.
        self.assertEqual(sorted(set(naive)), sorted(aware))


class OneRefusalPerReason(unittest.TestCase):
    def test_a_record_missing_a_required_section(self) -> None:
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Rejected alternatives\n\nBeing malformed, rejected because the "
            "fixtures below already are.\n\n",
            "",
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("missing required section(s) ## Rejected alternatives", faults[0])

    def test_a_record_whose_status_is_not_one_of_the_allowed_words(self) -> None:
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Status\n\nAccepted", "## Status\n\nApproved"
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("## Status carries 'Approved'", faults[0])
        self.assertIn("Proposed, Accepted, Superseded by NNNN", faults[0])

    def test_a_record_superseded_by_one_that_does_not_exist(self) -> None:
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Status\n\nAccepted", "## Status\n\nSuperseded by 0021"
        )
        files[records.INDEX] = INDEX.replace(
            "| A record that is fine | Accepted |",
            "| A record that is fine | Superseded by 0021 |",
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("superseded by record 0021, which is not in", faults[0])

    def test_and_the_same_status_pointing_at_a_record_that_does_exist(self) -> None:
        # The near miss of the fixture above, one digit apart. The status form
        # is identical and the pointer resolves, so nothing is refused.
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Status\n\nAccepted", "## Status\n\nSuperseded by 0000"
        )
        files[records.INDEX] = INDEX.replace(
            "| A record that is fine | Accepted |",
            "| A record that is fine | Superseded by 0000 |",
        )
        self.assertEqual(judged(files), [])

    def test_a_record_that_is_absent_from_the_index(self) -> None:
        files = clean()
        files[records.INDEX] = INDEX.replace(ROW, "")
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn(f"no row for {FINE}", faults[0])

    def test_an_index_row_pointing_at_a_file_that_is_not_there(self) -> None:
        files = clean()
        files[records.INDEX] = INDEX + MISSING_ROW
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn(
            "the row for 0002 points at 0002-a-record-nobody-wrote.md, which is "
            "not in the tree",
            faults[0],
        )


class WhatRecord0000HandsThisLegAboutACorrection(unittest.TestCase):
    def test_a_correction_heading_carrying_no_date(self) -> None:
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Answer\n\nIt is.",
            "## Answer\n\nIt is.\n\n### Correction, on the sentence above"
            "\n\nIt was not.",
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("carries no YYYY-MM-DD date after the comma", faults[0])

    def test_and_the_same_heading_one_date_later(self) -> None:
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Answer\n\nIt is.",
            "## Answer\n\nIt is.\n\n### Correction, 2026-08-09, on the sentence "
            "above\n\nIt was not.",
        )
        self.assertEqual(judged(files), [])

    def test_a_correction_on_a_record_that_was_superseded(self) -> None:
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Status\n\nAccepted", "## Status\n\nSuperseded by 0000"
        ).replace(
            "## Answer\n\nIt is.",
            "## Answer\n\nIt is.\n\n### Correction, 2026-08-09, on the sentence "
            "above\n\nIt was not.",
        )
        files[records.INDEX] = INDEX.replace(
            "| A record that is fine | Accepted |",
            "| A record that is fine | Superseded by 0000 |",
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("on a record superseded by 0000", faults[0])
        self.assertIn("no correction", faults[0])

    def test_a_correction_inside_a_fence_is_an_example_and_not_a_correction(
        self,
    ) -> None:
        # Record 0000 writes the correction heading form out in its own text.
        # A scan that ignored fences would read the specification as an instance
        # of the thing it specifies.
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Answer\n\nIt is.",
            "## Answer\n\nIt is. One looks like this:\n\n```\n"
            "### Correction, YYYY-MM-DD, on what it corrects\n```",
        )
        self.assertEqual(judged(files), [])


class TheHeadingsThemselves(unittest.TestCase):
    def test_a_title_naming_a_number_the_filename_does_not(self) -> None:
        # The number is what an index row, a supersession and a reader all cite,
        # so a record whose title says one and whose name says another is a
        # record two of them resolve differently.
        files = clean()
        files[FINE] = WELL_FORMED.replace("# 0001. ", "# 0002. ")
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("record 0000 requires '# 0001. Title'", faults[0])

    def test_the_required_sections_present_and_out_of_order(self) -> None:
        # The near miss of a missing section, and the one a reader is least
        # likely to see: nothing is absent, so a check counting sections passes
        # it. Record 0000 fixes the order as well as the set.
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Status\n\nAccepted\n\n## Date\n\n2026-08-08",
            "## Date\n\n2026-08-08\n\n## Status\n\nAccepted",
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("out of the order record 0000 fixes", faults[0])
        self.assertIn("## Date ## Status", faults[0])

    def test_a_file_that_no_number_resolves(self) -> None:
        files = clean()
        files["a-record-somebody-named-by-hand.md"] = WELL_FORMED
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("not named NNNN-short-title.md", faults[0])
        self.assertIn("no index row can point at it", faults[0])


class ReadingTheIndex(unittest.TestCase):
    def test_a_link_in_the_prose_is_not_a_second_row(self) -> None:
        # Counting occurrences of a filename in the index refuses a correct
        # index, because the paragraph above the table links to record 0000 too.
        self.assertEqual(INDEX.count("(0000-how-a-decision-is-recorded.md)"), 2)
        self.assertEqual(
            records.rows(INDEX),
            [
                ("0000", "0000-how-a-decision-is-recorded.md"),
                ("0001", "0001-a-record-that-is-fine.md"),
            ],
        )

    def test_a_record_listed_twice(self) -> None:
        files = clean()
        files[records.INDEX] = INDEX + ROW
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("2 rows for 0001", faults[0])


class TheLegFailsClosed(unittest.TestCase):
    def test_a_tree_with_no_decisions_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verdict = records.run(Path(directory))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)

    def test_a_directory_with_no_shape_record_in_it(self) -> None:
        files = clean()
        del files[records.SHAPE]
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("what this leg requires cannot be read", faults[0])

    def test_a_directory_with_no_index_in_it(self) -> None:
        files = clean()
        del files[records.INDEX]
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("is the index and it is not in the tree", faults[0])

    def test_the_leg_carries_a_departure_out_as_a_refusal(self) -> None:
        # Everything above judges the directory. This is the one that says the
        # leg turns what it found into a verdict, rather than finding it and
        # reporting green.
        files = clean()
        files[FINE] = WELL_FORMED.replace(
            "## Status\n\nAccepted", "## Status\n\nApproved"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / records.DECISIONS).mkdir(parents=True)
            written(root / records.DECISIONS, files)
            verdict = records.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("1 departure(s) from the shape record 0000 fixes", verdict.detail)
        self.assertIn("## Status carries 'Approved'", verdict.detail)


class OnThisTree(unittest.TestCase):
    def test_every_landed_record_is_already_well_formed(self) -> None:
        # The day this check lands it has to be green on `main` without any
        # record moving. Where it reddens a landed record, the checker is wrong
        # rather than the record.
        self.assertEqual(records.judge(DECISIONS), [])

    def test_the_leg_passes_and_says_how_many_it_read(self) -> None:
        verdict = records.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("record(s) under docs/decisions/", verdict.detail)

    def test_the_real_shape_record_yields_the_two_lists(self) -> None:
        # The fixture vocabulary above is a fixture, so this is the one place
        # the real record is read, and it is read for the lists rather than
        # judged against them.
        shape = (DECISIONS / records.SHAPE).read_text(encoding="utf-8")
        self.assertEqual(records.required(shape)[0], "## Status")
        self.assertIn("Superseded by NNNN", records.allowed(shape))


if __name__ == "__main__":
    unittest.main()
