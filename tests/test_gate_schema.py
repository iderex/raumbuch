"""The schema leg bites, and it bites for the reason it names.

Each fixture below breaks exactly one thing and the assertion is on what the
refusal says, because a leg that refuses for the wrong reason passes a test that
counts refusals. The records are the catalogue corpus's smallest valid one with
one substitution, which is the idiom `test_record.py` already uses: what these
fixtures are about is a field's value, and the byte-exactness the frozen corpus
exists for is not the property under test here.
"""

from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

import catalogue_corpus

from raumbuch import catalogue
from raumbuch.gate import schema

ROOT = Path(__file__).resolve().parents[1]

VALID = base64.b64decode(catalogue_corpus.KERR)


def changed(*substitutions: tuple[str, str]) -> bytes:
    data = VALID
    for before, after in substitutions:
        assert before.encode() in data, before
        data = data.replace(before.encode(), after.encode(), 1)
    return data


def tree(root: Path, records: dict[str, bytes], schemas: bool = True) -> None:
    """A checkout carrying the named records and, by default, this tree's schemas."""
    (root / catalogue.DIRECTORY).mkdir(parents=True, exist_ok=True)
    for name, data in records.items():
        (root / catalogue.DIRECTORY / name).write_bytes(data)
    if not schemas:
        return
    (root / schema.DIRECTORY).mkdir(parents=True, exist_ok=True)
    for path in (ROOT / schema.DIRECTORY).glob(f"{schema.PREFIX}*{schema.SUFFIX}"):
        (root / schema.DIRECTORY / path.name).write_bytes(path.read_bytes())


class TheVersionSelectsTheSchema(unittest.TestCase):
    def test_the_versions_this_tree_carries_are_read_off_the_filenames(self) -> None:
        found = schema.available(ROOT / schema.DIRECTORY)
        self.assertEqual(sorted(found), ["1"])
        self.assertTrue(found["1"].is_file())

    def test_a_record_naming_a_version_this_tree_has_no_schema_for(self) -> None:
        """The message names the version it found and the versions there are."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    "kerr.toml": changed(
                        ('schema_version = "1"', 'schema_version = "2"')
                    )
                },
            )
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("'2'", verdict.detail)
        self.assertIn("'1'", verdict.detail)
        self.assertIn("kerr.toml", verdict.detail)

    def test_a_record_naming_no_version_at_all(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {"kerr.toml": changed(('schema_version = "1"\n', ""))})
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("declares no schema_version", verdict.detail)


class TheLegRefusesAShapeTheSchemaRejects(unittest.TestCase):
    def test_a_signature_that_is_not_a_sign_string(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    "kerr.toml": changed(
                        ('signature = "-+++"', 'signature = "mostly plus"')
                    )
                },
            )
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("signature", verdict.detail)

    def test_a_field_the_schema_does_not_admit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    "kerr.toml": changed(
                        ("dimension = 4", 'petrov = "D"\ndimension = 4')
                    )
                },
            )
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("petrov", verdict.detail)

    def test_every_record_is_judged_rather_than_the_first(self) -> None:
        """A run that stopped at the first would report one fault where two broke."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    "kerr.toml": changed(('signature = "-+++"', 'signature = "up"')),
                    "kerr-newman.toml": base64.b64decode(
                        catalogue_corpus.KERR_NEWMAN
                    ).replace(b'signature = "-+++"', b'signature = "down"', 1),
                },
            )
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("2 fault(s)", verdict.detail)
        self.assertIn("2 record(s)", verdict.detail)
        self.assertIn("kerr.toml", verdict.detail)
        self.assertIn("kerr-newman.toml", verdict.detail)


class TheLegFailsClosed(unittest.TestCase):
    def test_a_tree_carrying_no_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {"kerr.toml": VALID}, schemas=False)
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)


class TheLegPasses(unittest.TestCase):
    def test_a_record_of_the_shape_the_schema_fixes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {"kerr.toml": VALID})
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("1 record(s)", verdict.detail)

    def test_the_count_is_every_record_and_not_a_sample(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    "kerr.toml": VALID,
                    "kerr-newman.toml": base64.b64decode(catalogue_corpus.KERR_NEWMAN),
                },
            )
            verdict = schema.run(root)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("2 record(s)", verdict.detail)

    def test_the_report_says_a_shape_is_not_a_whole_record(self) -> None:
        """The claim the leg is allowed to make is narrower than a valid record."""
        verdict = schema.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("A shape is not a whole record", verdict.detail)


class TheSchemaInThisTreeIsReadable(unittest.TestCase):
    def test_it_parses_and_declares_the_version_its_filename_carries(self) -> None:
        for version, path in schema.available(ROOT / schema.DIRECTORY).items():
            with self.subTest(version=version):
                document = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    document["properties"]["schema_version"]["const"], version
                )


if __name__ == "__main__":
    unittest.main()
