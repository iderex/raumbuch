"""The index refuses what record 0004 says it refuses, and the report is quiet.

Two kinds of test here and they prove different things.

The corpus half is driven from the enumeration, the same way `test_corpus.py`
drives the loader's: a reason with no fixture fails, the refused half triggers
that reason and no other, and the near miss beside it is accepted. That is what
makes the corpus complete with respect to the vocabulary rather than with
respect to whoever last added to it.

The rest reaches the refusal sites the corpus cannot separate. Two of these
reasons are refused at two places in the operator, one for each end of a
supersession link, and a corpus that compares sets of reasons cannot tell one
site from the other: a fixture reaching only the forward end would leave the
backward end deletable with nothing going red. Each site is reached by name
below.
"""

from __future__ import annotations

import base64
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import catalogue_corpus

from raumbuch import catalogue, refusal

BASE64_ONLY = re.compile(r"[A-Za-z0-9+/=]+")


def reasons_of(half: catalogue_corpus.Half) -> set[str]:
    """The set of reasons reading this catalogue produced. Empty where it read.

    Building stops at the first refusal, so the set holds one reason at most,
    and the near miss beside the fixture is what says nothing else was wrong
    with it.
    """
    try:
        index = catalogue.build(half.decoded())
        if half.pin is not None:
            catalogue.pinned(index, *half.pin)
    except refusal.Refused as refused:
        return {refused.reason}
    return set()


class EveryCatalogueReasonHasAFixture(unittest.TestCase):
    def test_no_reason_is_without_one(self) -> None:
        self.assertEqual(set(catalogue_corpus.FIXTURES), set(refusal.CATALOGUE_REASONS))

    def test_the_count_is_the_count_of_the_vocabulary(self) -> None:
        self.assertEqual(len(catalogue_corpus.FIXTURES), len(refusal.CATALOGUE_REASONS))


class EachFixtureTriggersExactlyItsOwnReason(unittest.TestCase):
    def test_the_refused_half_triggers_that_reason_and_no_other(self) -> None:
        for reason, fixture in catalogue_corpus.FIXTURES.items():
            with self.subTest(reason=reason, note=fixture.note):
                self.assertEqual(reasons_of(fixture.refused), {reason})

    def test_the_near_miss_beside_it_is_accepted(self) -> None:
        for reason, fixture in catalogue_corpus.FIXTURES.items():
            with self.subTest(reason=reason, note=fixture.note):
                self.assertEqual(reasons_of(fixture.accepted), set())

    def test_the_near_miss_differs_from_the_refused_one(self) -> None:
        for reason, fixture in catalogue_corpus.FIXTURES.items():
            with self.subTest(reason=reason):
                self.assertNotEqual(fixture.refused, fixture.accepted)

    def test_every_fixture_says_what_the_one_difference_is(self) -> None:
        for reason, fixture in catalogue_corpus.FIXTURES.items():
            with self.subTest(reason=reason):
                self.assertTrue(fixture.note.strip())

    def test_every_record_is_stored_base64_and_not_as_a_literal(self) -> None:
        for reason, fixture in catalogue_corpus.FIXTURES.items():
            for half in (fixture.refused, fixture.accepted):
                for _, data in half.documents:
                    with self.subTest(reason=reason):
                        self.assertIsNotNone(BASE64_ONLY.fullmatch(data))


class BothEndsOfASupersessionAreReached(unittest.TestCase):
    """The sites the corpus cannot separate, reached one at a time.

    The corpus fixture for each of these two reasons refuses at the end that
    reads ``superseded_by``. The end that reads ``supersedes`` refuses for the
    same reason, so deleting it would move no set of reasons anywhere. These
    two tests are what makes it deletable only with something going red.
    """

    def test_supersedes_naming_an_id_the_catalogue_does_not_hold(self) -> None:
        documents = [
            (
                "kerr-schild.toml",
                base64.b64decode(catalogue_corpus.KERR_SCHILD_SUPERSEDING),
            )
        ]
        with self.assertRaises(refusal.Refused) as raised:
            catalogue.build(documents)
        self.assertEqual(raised.exception.reason, refusal.SUPERSESSION_NAMES_NO_RECORD)
        self.assertIn("supersedes", raised.exception.detail)

    def test_supersedes_whose_other_end_says_nothing(self) -> None:
        half = catalogue_corpus.Half(
            documents=(
                ("kerr.toml", catalogue_corpus.KERR),
                ("kerr-schild.toml", catalogue_corpus.KERR_SCHILD_SUPERSEDING),
            )
        )
        with self.assertRaises(refusal.Refused) as raised:
            catalogue.build(half.decoded())
        self.assertEqual(raised.exception.reason, refusal.HALF_WRITTEN_SUPERSESSION)


class WhatAPinnedConsumerIsTold(unittest.TestCase):
    def index_of(self, half: catalogue_corpus.Half) -> catalogue.Index:
        return catalogue.build(half.decoded())

    def test_a_pin_that_matches_says_nothing(self) -> None:
        """Record 0004: the quiet case has to stay quiet."""
        index = self.index_of(catalogue_corpus.FIXTURES["unknown-identifier"].accepted)
        report = index.pinned("kerr", 1)
        self.assertTrue(report.quiet)
        self.assertEqual(report.lines(), [])

    def test_a_pin_below_the_current_version_is_told_it_was_corrected(self) -> None:
        index = self.index_of(catalogue_corpus.CORRECTED)
        report = index.pinned("kerr", 1)
        self.assertFalse(report.quiet)
        self.assertEqual(report.pinned, 1)
        self.assertEqual(report.current, 2)
        self.assertEqual(len(report.corrections), 1)
        self.assertEqual(report.corrections[0]["version"], 2)
        self.assertIn("was corrected", report.lines()[0])
        self.assertIn("Petrov type", "\n".join(report.lines()))

    def test_a_correction_before_the_pin_is_not_reported_again(self) -> None:
        """A consumer pinned to 2 has already been told about the entry for 2."""
        index = self.index_of(catalogue_corpus.CORRECTED)
        report = index.pinned("kerr", 2)
        self.assertTrue(report.quiet)
        self.assertEqual(report.corrections, ())

    def test_a_pin_on_a_superseded_record_names_the_successor(self) -> None:
        index = self.index_of(
            catalogue_corpus.FIXTURES["half-written-supersession"].accepted
        )
        report = index.pinned("kerr", 1)
        self.assertFalse(report.quiet)
        self.assertEqual(report.superseded_by, "kerr-schild")
        self.assertIn("superseded by kerr-schild", "\n".join(report.lines()))

    def test_nothing_is_redirected(self) -> None:
        """Record 0004 rejects the silent redirect, so the report is all there is."""
        index = self.index_of(
            catalogue_corpus.FIXTURES["half-written-supersession"].accepted
        )
        self.assertEqual(index.pinned("kerr", 1).id, "kerr")

    def test_a_pin_above_the_current_version_says_the_two_numbers(self) -> None:
        index = self.index_of(catalogue_corpus.CORRECTED)
        report = index.pinned("kerr", 5)
        self.assertFalse(report.quiet)
        self.assertIn("which is lower", "\n".join(report.lines()))
        self.assertEqual(report.corrections, ())

    def test_an_unknown_id_is_refused_rather_than_returned_empty(self) -> None:
        index = self.index_of(catalogue_corpus.CORRECTED)
        with self.assertRaises(refusal.Refused) as raised:
            index.pinned("gravitational-wave", 1)
        self.assertEqual(raised.exception.reason, refusal.UNKNOWN_IDENTIFIER)
        self.assertIn("this release never held it", raised.exception.detail)


class ReadingADirectory(unittest.TestCase):
    def written(self, root: Path, half: catalogue_corpus.Half) -> None:
        for source, data in half.decoded():
            path = root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def test_an_empty_directory_is_an_empty_index(self) -> None:
        with TemporaryDirectory() as directory:
            index = catalogue.read(Path(directory))
        self.assertEqual(len(index), 0)
        self.assertEqual(index.ids, ())

    def test_the_walk_descends_and_finds_the_id_spent_twice(self) -> None:
        """The refusal is reachable from a directory, which is what it is for.

        A walk that stopped at the top could never meet it: two files with one
        name in one directory is a thing the filesystem refuses first.
        """
        fixture = catalogue_corpus.FIXTURES["id-carried-by-two-records"]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.written(root, fixture.refused)
            with self.assertRaises(refusal.Refused) as raised:
                catalogue.read(root)
        self.assertEqual(raised.exception.reason, refusal.ID_CARRIED_BY_TWO_RECORDS)

    def test_two_ids_in_two_directories_are_two_entries(self) -> None:
        fixture = catalogue_corpus.FIXTURES["id-carried-by-two-records"]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.written(root, fixture.accepted)
            index = catalogue.read(root)
        self.assertEqual(index.ids, ("kerr", "kerr-newman"))
        self.assertEqual(index.superseded, ())

    def test_a_superseded_entry_is_in_the_state_record_0004_names(self) -> None:
        fixture = catalogue_corpus.FIXTURES["half-written-supersession"]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.written(root, fixture.accepted)
            index = catalogue.read(root)
        self.assertEqual(index.superseded, ("kerr",))
        self.assertEqual(index.entries["kerr"].state, catalogue.SUPERSEDED)
        self.assertEqual(index.entries["kerr-schild"].state, catalogue.CURRENT)


class TheCatalogueInThisTree(unittest.TestCase):
    """Against the real directory rather than a fixture one.

    It holds no entry until issue #73 lands, so what this proves today is that
    the walk reaches it and the empty case is a pass rather than a crash. The
    assertions are written to hold once entries arrive, because a test that has
    to be rewritten by whoever lands the first entry is a test that gets
    deleted instead.
    """

    def index(self) -> catalogue.Index:
        root = Path(__file__).resolve().parents[1]
        return catalogue.read(root / catalogue.DIRECTORY)

    def test_it_reads(self) -> None:
        self.assertEqual(len(self.index()), len(self.index().ids))

    def test_every_id_is_the_stem_of_what_it_was_read_from(self) -> None:
        for identifier, entry in self.index().entries.items():
            with self.subTest(id=identifier):
                self.assertEqual(identifier, Path(entry.source).stem)


if __name__ == "__main__":
    unittest.main()
