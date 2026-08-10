"""The documents leg bites, once per way a page promises what the tree does not.

Every fixture is a tree of its own. A README with a drifted paragraph beside the
real one would be a second README, and a document linking at nothing would
redden the check on `main` for as long as it stayed there.

The near miss in each pair is the same document one edit from a refusal: a
quoted paragraph with one word changed against the paragraph the record fixes,
and a link one filename away from the file it points at.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from raumbuch.gate import documents

ROOT = Path(__file__).resolve().parents[1]

POSITIVE = """A fixture paragraph. It says what a positive answer means, in the
words the record argues for and in no others.
"""

NETWORK = """A fixture paragraph about the network, which is the second record
this leg reads.
"""

SAME_MEANS = f"""# 0007. Fixture

The positive paragraph:

```
{POSITIVE.rstrip()}
```

The limiting paragraph:

```
A fixture paragraph. It says what a positive answer does not mean.
```
"""

NETWORK_RECORD = f"""# 0014. Fixture

### The paragraph the documentation quotes

```
{NETWORK.rstrip()}
```
"""

READ_ME = f"""# fixture

{POSITIVE.rstrip()}

A fixture paragraph. It says what a positive answer does not mean.

{NETWORK.rstrip()}

See [the shape of a record](docs/decisions/0007-what-same-means.md).
"""


def tree(files: dict[str, str]) -> Path:
    directory = Path(tempfile.mkdtemp())
    for name, text in files.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return directory


def clean() -> dict[str, str]:
    return {
        "README.md": READ_ME,
        "docs/decisions/0007-what-same-means.md": SAME_MEANS,
        "docs/decisions/0014-network-and-personal-data.md": NETWORK_RECORD,
    }


def judged(files: dict[str, str]) -> list[str]:
    return documents.judge(tree(files))


class TheFixtureTreeIsClean(unittest.TestCase):
    def test_nothing_is_refused_before_a_departure_is_written_in(self) -> None:
        self.assertEqual(judged(clean()), [])


class AQuotedParagraphThatDrifted(unittest.TestCase):
    def test_one_word_changed_in_the_carrier(self) -> None:
        files = clean()
        files["README.md"] = READ_ME.replace("in no others", "in no other words")
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("README.md does not carry the paragraph", faults[0])
        self.assertIn("0007-what-same-means.md", faults[0])
        self.assertIn("byte for byte", faults[0])

    def test_and_the_same_paragraph_unchanged_is_not_a_departure(self) -> None:
        # The near miss. The carrier is the record's own text in both trees and
        # the only difference is two words inside it, which is the edit that
        # turns a limitation into something more comfortable to read.
        self.assertEqual(judged(clean()), [])
        self.assertIn("in no others", READ_ME)

    def test_a_paragraph_the_carrier_reflowed(self) -> None:
        # Reflowing reads as a formatting change and is a change to the bytes a
        # consumer sees. The record fences the paragraph for that reason, so a
        # comparison that normalised whitespace would pass this.
        files = clean()
        files["README.md"] = READ_ME.replace(
            "in the\nwords the record argues for", "in the words the record argues for"
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("README.md does not carry the paragraph", faults[0])

    def test_a_carrier_that_dropped_the_paragraph_altogether(self) -> None:
        files = clean()
        files["README.md"] = "# fixture\n\nNothing quoted here.\n"
        faults = judged(files)
        self.assertEqual(len(faults), 3, faults)

    def test_every_quotation_is_compared_and_not_only_the_first(self) -> None:
        files = clean()
        files["README.md"] = READ_ME.replace("about the network", "about networks")
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("0014-network-and-personal-data.md", faults[0])

    def test_a_record_whose_anchor_sentence_moved(self) -> None:
        # The table in the module names the sentence each record introduces its
        # block with. A record that renames it leaves this leg with nothing to
        # read, and saying so is the difference between failing closed and
        # passing with nothing compared.
        files = clean()
        files["docs/decisions/0007-what-same-means.md"] = SAME_MEANS.replace(
            "The positive paragraph:", "The paragraph about a positive answer:"
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("carries no fenced block after", faults[0])

    def test_a_record_that_is_not_in_the_tree(self) -> None:
        files = clean()
        del files["docs/decisions/0014-network-and-personal-data.md"]
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("it is not in this tree", faults[0])


class ALinkThatResolves(unittest.TestCase):
    def test_a_link_to_a_file_that_is_not_there(self) -> None:
        files = clean()
        files["README.md"] = READ_ME.replace(
            "docs/decisions/0007-what-same-means.md", "docs/cost.md"
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("README.md links to docs/cost.md", faults[0])
        self.assertIn("is not in this tree", faults[0])

    def test_and_the_same_link_one_filename_along_resolves(self) -> None:
        # The near miss, and the mistake somebody actually makes: a document
        # renamed and one pointer at the old name left behind.
        self.assertEqual(judged(clean()), [])
        self.assertIn("(docs/decisions/0007-what-same-means.md)", READ_ME)

    def test_a_link_relative_to_the_document_rather_than_the_root(self) -> None:
        files = clean()
        files["docs/notes.md"] = (
            "See [the record](decisions/0007-what-same-means.md).\n"
        )
        self.assertEqual(judged(files), [])

    def test_and_the_same_target_read_from_the_root_would_not_resolve(self) -> None:
        # The direction a rule resolving every link against the root gets
        # wrong. `decisions/` is under `docs/`, and nothing of that name sits at
        # the top of the tree.
        files = clean()
        files["notes.md"] = "See [the record](decisions/0007-what-same-means.md).\n"
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("notes.md links to", faults[0])

    def test_an_anchor_on_a_target_is_dropped_and_the_path_is_judged(self) -> None:
        files = clean()
        files["notes.md"] = "See [a heading](README.md#fixture).\n"
        self.assertEqual(judged(files), [])

    def test_a_link_that_is_only_an_anchor_is_not_judged(self) -> None:
        files = clean()
        files["notes.md"] = "See [below](#what-this-does-not-cover).\n"
        self.assertEqual(judged(files), [])

    def test_an_address_is_not_fetched(self) -> None:
        files = clean()
        files["notes.md"] = (
            "See [a paper](https://example.invalid/paper) and "
            "[the maintainer](mailto:nobody@example.invalid).\n"
        )
        self.assertEqual(judged(files), [])

    def test_a_reference_definition_is_a_link(self) -> None:
        files = clean()
        files["notes.md"] = "See [the record][one].\n\n[one]: docs/cost.md\n"
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("links to docs/cost.md", faults[0])

    def test_a_path_inside_a_fence_is_text_rather_than_a_pointer(self) -> None:
        # `docs/checks.md` quotes commands and record 0003 carries a worked
        # example. A rule reading inside a fence would refuse a document for
        # showing what a path looks like.
        files = clean()
        files["notes.md"] = "```\nSee [a file](docs/cost.md).\n```\n"
        self.assertEqual(judged(files), [])

    def test_a_directory_is_a_target_that_resolves(self) -> None:
        files = clean()
        files["notes.md"] = "See [the records](docs/decisions).\n"
        self.assertEqual(judged(files), [])


class TheLegFailsClosed(unittest.TestCase):
    def test_a_tree_with_no_decision_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verdict = documents.run(Path(directory))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)

    def test_a_departure_is_carried_out_as_a_refusal(self) -> None:
        files = clean()
        files["README.md"] = READ_ME.replace("in no others", "in no other words")
        verdict = documents.run(tree(files))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("1 way(s) a document promises", verdict.detail)

    def test_an_environment_left_in_the_checkout_is_not_the_tree(self) -> None:
        # A virtual environment carries hundreds of documents somebody else
        # wrote, and their links are not this repository's promise.
        files = clean()
        files[".venv/pyvenv.cfg"] = "home = /nowhere\n"
        files[".venv/lib/README.md"] = "See [nothing](nowhere.md).\n"
        self.assertEqual(judged(files), [])


class OnThisTree(unittest.TestCase):
    def test_the_documents_hold_here(self) -> None:
        verdict = documents.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)

    def test_every_quotation_names_a_record_and_a_carrier_that_exist(self) -> None:
        for quotation in documents.QUOTED:
            record = ROOT / documents.DECISIONS / quotation.record
            self.assertTrue(record.is_file(), quotation.record)
            self.assertIsNotNone(
                documents.block_after(
                    record.read_text(encoding="utf-8"), quotation.introduced_by
                ),
                quotation.introduced_by,
            )
            for name in quotation.carried_by:
                self.assertTrue((ROOT / name).is_file(), name)

    def test_the_readme_is_a_carrier_of_every_quotation(self) -> None:
        # Record 0007 names three carriers and record 0014 names two. The
        # report constant is the one this leg does not reach, and it is issue
        # #105 rather than a carrier missing from the table here.
        for quotation in documents.QUOTED:
            self.assertIn("README.md", quotation.carried_by)


if __name__ == "__main__":
    unittest.main()
