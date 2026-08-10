"""The fixture corpus does what it says: every reason, exactly, with a near miss.

A loader is only as good as the things it says no to, and a refusal nobody has
watched fire is a refusal that may not work. So the corpus is driven from the
enumeration rather than from a list somebody keeps: a reason with no fixture
fails here, which is what makes the corpus complete with respect to the
vocabulary rather than with respect to whoever last added to it.

"Exactly its own reason" is two assertions rather than one. The refused fixture
triggers that reason and no other, and the near miss beside it, one plausible
mistake away, is accepted. The second is what makes the first mean something: if
a fixture carried a second defect, repairing only the first would leave the near
miss refused, and this would say so.
"""

from __future__ import annotations

import base64
import re
import unittest
from pathlib import Path

import catalogue_corpus
import corpus

from raumbuch import record, refusal

ROOT = Path(__file__).resolve().parents[1]
RECORD_FORMAT = ROOT / "docs" / "record-format.md"
BASE64_ONLY = re.compile(r"[A-Za-z0-9+/=]+")


def reasons_of(data: bytes, stem: str) -> set[str]:
    """The set of reasons loading these bytes produced. Empty where it loaded.

    A set rather than a boolean, because a fixture that fails is not evidence
    about the rule it was written for. The loader stops at the first refusal, so
    the set holds one reason at most, and the near miss is what says nothing
    else was wrong with the fixture.
    """
    try:
        record.loads(data, stem)
    except refusal.Refused as refused:
        return {refused.reason}
    return set()


class EveryReasonHasAFixture(unittest.TestCase):
    """Two corpora, because a reason is decided by what it reads.

    This file's fixtures are one document each, which is what the parser and
    the loader read. The reasons that need the set of records are in
    `catalogue_corpus.py`, whose fixture is a catalogue rather than a record.
    The split is the vocabulary's own, and the union below is what stops a
    reason falling between the two files and being covered by neither.
    """

    def test_no_reason_is_without_one(self) -> None:
        self.assertEqual(
            set(corpus.FIXTURES) | set(catalogue_corpus.FIXTURES),
            set(refusal.REASONS),
        )

    def test_the_corpus_holds_no_fixture_for_a_reason_that_is_not_declared(
        self,
    ) -> None:
        self.assertEqual(set(corpus.FIXTURES) - set(refusal.REASONS), set())

    def test_neither_corpus_covers_a_reason_the_other_covers(self) -> None:
        self.assertEqual(set(corpus.FIXTURES) & set(catalogue_corpus.FIXTURES), set())

    def test_this_corpus_is_the_reasons_one_document_decides(self) -> None:
        self.assertEqual(
            set(corpus.FIXTURES),
            set(refusal.PARSER_REASONS) | set(refusal.LOADER_REASONS),
        )

    def test_the_count_is_the_count_of_the_vocabulary(self) -> None:
        self.assertEqual(
            len(corpus.FIXTURES) + len(catalogue_corpus.FIXTURES),
            len(refusal.REASONS),
        )


class EachFixtureTriggersExactlyItsOwnReason(unittest.TestCase):
    def test_the_refused_fixture_triggers_that_reason_and_no_other(self) -> None:
        for reason, fixture in corpus.FIXTURES.items():
            with self.subTest(reason=reason, note=fixture.note):
                self.assertEqual(
                    reasons_of(fixture.refused_bytes(), fixture.refused_stem),
                    {reason},
                )

    def test_the_near_miss_beside_it_is_accepted(self) -> None:
        for reason, fixture in corpus.FIXTURES.items():
            with self.subTest(reason=reason, note=fixture.note):
                self.assertEqual(
                    reasons_of(fixture.accepted_bytes(), fixture.accepted_stem),
                    set(),
                )

    def test_the_near_miss_differs_from_the_refused_one(self) -> None:
        """Nothing here proves the difference is small. It proves there is one.

        How small the change is, and whether it is the mistake somebody will
        actually make, is the note beside each fixture and a judgement a reader
        makes. What a test can say is that the pair is a pair.
        """
        for reason, fixture in corpus.FIXTURES.items():
            with self.subTest(reason=reason):
                self.assertNotEqual(
                    (fixture.refused_bytes(), fixture.refused_stem),
                    (fixture.accepted_bytes(), fixture.accepted_stem),
                )

    def test_every_fixture_says_what_the_one_difference_is(self) -> None:
        for reason, fixture in corpus.FIXTURES.items():
            with self.subTest(reason=reason):
                self.assertTrue(fixture.note.strip())


class TheBytesSurviveVersionControl(unittest.TestCase):
    def test_every_fixture_is_stored_base64_and_not_as_a_literal(self) -> None:
        """The storage rule, checked rather than described.

        A raw TOML literal in a tracked text file is normalised on the way in
        and on the way out, and normalisation deletes exactly the byte a fixture
        might exist to prove. A field carrying anything outside the base64
        alphabet is a fixture somebody pasted in raw.
        """
        for reason, fixture in corpus.FIXTURES.items():
            for half in (fixture.refused, fixture.accepted):
                with self.subTest(reason=reason):
                    self.assertIsNotNone(BASE64_ONLY.fullmatch(half))

    def test_the_carriage_return_fixture_still_carries_its_carriage_returns(
        self,
    ) -> None:
        """The claim above, executed.

        These bytes went into the tree with carriage returns in them and come
        out with the same ones. A record stored as a TOML literal could not
        promise that, because what a checkout does to a line ending is a fact of
        each clone's configuration and no tree holds it.
        """
        data = base64.b64decode(corpus.CARRIAGE_RETURN)
        self.assertIn(b"\r\n", data)
        self.assertEqual(data.count(b"\r\n"), data.count(b"\n"))
        loaded = record.loads(data, "schwarzschild")
        self.assertEqual(loaded.id, "schwarzschild")


class TheBaselineIsStillTheRecordTheDocumentCarries(unittest.TestCase):
    def test_the_frozen_baseline_matches_the_worked_record(self) -> None:
        """Where a re-freeze is decided rather than happening quietly.

        The corpus is exact bytes and deliberately does not follow the document.
        This is the one place the two are compared, so a change to the worked
        record reddens here and names its own repair, instead of leaving forty
        fixtures quietly testing a record nobody writes any more.
        """
        text = RECORD_FORMAT.read_text(encoding="utf-8")
        start = text.index("```toml")
        worked = text[start + len("```toml") : text.index("```", start + 3)]
        self.assertEqual(
            base64.b64decode(corpus.BASELINE).decode("utf-8"),
            worked,
            "the worked record moved; rebuild the corpus deliberately",
        )

    def test_the_baseline_loads(self) -> None:
        loaded = record.loads(base64.b64decode(corpus.BASELINE), "schwarzschild")
        self.assertEqual(loaded.dimension, 4)


if __name__ == "__main__":
    unittest.main()
