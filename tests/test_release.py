"""The release artefacts bite, once per way an artefact would say something
untrue about itself.

Two halves, and they are proved differently on purpose.

The bill of materials is judged against fixture trees, because every way it can
be wrong is a disagreement between two files and needs no build. Each fixture is
a tree of its own: a lockfile beside the real one is a second lockfile somebody
could install from, and one carrying a hash that is not the real hash is the
worse version of that.

Reproducibility is judged against this checkout, because the property is about
the artefact this project ships and a fixture package would prove it of a
different one. The two builds are the expensive test here and they are the only
thing that answers the question, so the cost is paid rather than approximated
with a stored hash that somebody would have to update on every commit.

The near miss in each pair is one character from a pass: a hash with a digit
changed against the hash itself, a version bumped by one against the pinned one,
and a tarball whose times differ against one whose contents do.
"""

from __future__ import annotations

import copy
import gzip
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from raumbuch import release

ROOT = Path(__file__).resolve().parents[1]

MANIFEST = """[build-system]
requires = ["setuptools>=77"]

[project]
name = "fixture"
version = "0.0.0"
license = "AGPL-3.0-only"
dependencies = []

[project.optional-dependencies]
dev = ["ruff"]
"""

LOCK = """# A fixture lockfile.
ruff==0.16.2 \\
    --hash=sha256:0000000000000000000000000000000000000000000000000000000000000000 \\
    --hash=sha256:1111111111111111111111111111111111111111111111111111111111111111
setuptools==84.0.0 \\
    --hash=sha256:2222222222222222222222222222222222222222222222222222222222222222
"""


def tree(files: dict[str, str]) -> Path:
    directory = Path(tempfile.mkdtemp())
    for name, text in files.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return directory


def fixture(lock: str = LOCK, manifest: str = MANIFEST) -> Path:
    return tree(
        {
            "requirements.lock": lock,
            "pyproject.toml": manifest,
            ".python-version": "3.14.6\n",
        }
    )


def document(root: Path) -> dict:
    """A bill of materials for a fixture tree, without the commit stamp.

    ``bom`` reads the commit date, and a fixture tree is not a repository. What
    every test below is about is the component list, so it is built from the
    same function the document's own components come from.
    """
    return {
        "components": [
            {
                "type": "library",
                "name": component.name,
                "version": component.version,
                "hashes": [
                    {"alg": "SHA-256", "content": h.removeprefix("--hash=sha256:")}
                    for h in component.hashes
                ],
            }
            for component in release.components(root)
        ]
    }


def tarball(path: Path, when: int, payload: bytes = b"content") -> None:
    """A one-member tarball whose member time and gzip time are ``when``."""
    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode="w", format=tarfile.GNU_FORMAT) as archive:
        member = tarfile.TarInfo("package-1.0/PKG-INFO")
        member.size = len(payload)
        member.mtime = when
        archive.addfile(member, io.BytesIO(payload))
    with (
        open(path, "wb") as out,
        gzip.GzipFile(fileobj=out, mode="wb", mtime=when) as stream,
    ):
        stream.write(inner.getvalue())


class TheBillOfMaterialsMatchesTheLock(unittest.TestCase):
    def test_a_document_built_from_the_lock_is_accepted(self) -> None:
        root = fixture()
        release.verify(root, document(root))

    def test_a_changed_hash_is_refused(self) -> None:
        """The Done-when's fixture: one hash that is not the lock's."""
        root = fixture()
        edited = copy.deepcopy(document(root))
        content = edited["components"][0]["hashes"][0]["content"]
        edited["components"][0]["hashes"][0]["content"] = "9" + content[1:]
        with self.assertRaises(release.Refused) as refusal:
            release.verify(root, edited)
        self.assertIn("ruff", str(refusal.exception))
        self.assertIn("not among them", str(refusal.exception))

    def test_a_dropped_hash_is_refused(self) -> None:
        root = fixture()
        edited = copy.deepcopy(document(root))
        edited["components"][0]["hashes"].pop()
        with self.assertRaises(release.Refused):
            release.verify(root, edited)

    def test_a_changed_version_is_refused(self) -> None:
        root = fixture()
        edited = copy.deepcopy(document(root))
        edited["components"][0]["version"] = "0.16.3"
        with self.assertRaises(release.Refused) as refusal:
            release.verify(root, edited)
        self.assertIn("0.16.3", str(refusal.exception))

    def test_a_component_the_lock_does_not_pin_is_refused(self) -> None:
        root = fixture()
        edited = copy.deepcopy(document(root))
        edited["components"].append(
            {"type": "library", "name": "requests", "version": "2.0.0", "hashes": []}
        )
        with self.assertRaises(release.Refused) as refusal:
            release.verify(root, edited)
        self.assertIn("requests", str(refusal.exception))

    def test_a_component_the_lock_pins_and_the_document_omits_is_refused(self) -> None:
        root = fixture()
        edited = copy.deepcopy(document(root))
        edited["components"] = [
            component
            for component in edited["components"]
            if component["name"] != "setuptools"
        ]
        with self.assertRaises(release.Refused) as refusal:
            release.verify(root, edited)
        self.assertIn("setuptools", str(refusal.exception))


class TheLockIsReadStrictly(unittest.TestCase):
    def test_an_entry_with_no_hash_is_refused(self) -> None:
        root = fixture(lock="ruff==0.16.2\nsetuptools==84.0.0\n")
        with self.assertRaises(release.Refused) as refusal:
            release.components(root)
        self.assertIn("no hash", str(refusal.exception))

    def test_a_declared_distribution_absent_from_the_lock_is_refused(self) -> None:
        root = fixture(
            lock=("setuptools==84.0.0 \\\n    --hash=sha256:" + "2" * 64 + "\n")
        )
        with self.assertRaises(release.Refused) as refusal:
            release.components(root)
        self.assertIn("ruff", str(refusal.exception))

    def test_every_hash_of_an_entry_is_carried(self) -> None:
        root = fixture()
        found = {component.name: component for component in release.components(root)}
        self.assertEqual(len(found["ruff"].hashes), 2)
        self.assertEqual(len(found["setuptools"].hashes), 1)


class TheSdistNormalisationRemovesTheClockAndNothingElse(unittest.TestCase):
    def test_two_tarballs_differing_only_in_time_are_made_identical(self) -> None:
        directory = Path(tempfile.mkdtemp())
        first, second = directory / "a.tar.gz", directory / "b.tar.gz"
        tarball(first, 1_700_000_000)
        tarball(second, 1_800_000_000)
        self.assertNotEqual(
            first.read_bytes(),
            second.read_bytes(),
            "the fixture has to differ before normalisation or it proves nothing",
        )
        release.normalise_sdist(first, 42)
        release.normalise_sdist(second, 42)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_two_tarballs_differing_in_content_still_differ(self) -> None:
        """The bound on the normalisation: it removes a clock, not a change."""
        directory = Path(tempfile.mkdtemp())
        first, second = directory / "a.tar.gz", directory / "b.tar.gz"
        tarball(first, 1_700_000_000, payload=b"content")
        tarball(second, 1_700_000_000, payload=b"changed")
        release.normalise_sdist(first, 42)
        release.normalise_sdist(second, 42)
        self.assertNotEqual(first.read_bytes(), second.read_bytes())

    def test_the_gzip_header_carries_no_time(self) -> None:
        directory = Path(tempfile.mkdtemp())
        path = directory / "a.tar.gz"
        tarball(path, 1_700_000_000)
        release.normalise_sdist(path, 42)
        self.assertEqual(int.from_bytes(path.read_bytes()[4:8], "little"), 0)

    def test_the_member_time_is_the_epoch_it_was_given(self) -> None:
        directory = Path(tempfile.mkdtemp())
        path = directory / "a.tar.gz"
        tarball(path, 1_700_000_000)
        release.normalise_sdist(path, 42)
        with tarfile.open(path, "r:gz") as archive:
            self.assertEqual([member.mtime for member in archive.getmembers()], [42])

    def test_the_members_survive_the_rewrite(self) -> None:
        directory = Path(tempfile.mkdtemp())
        path = directory / "a.tar.gz"
        tarball(path, 1_700_000_000, payload=b"content")
        release.normalise_sdist(path, 42)
        with tarfile.open(path, "r:gz") as archive:
            members = archive.getmembers()
            self.assertEqual(
                [member.name for member in members], ["package-1.0/PKG-INFO"]
            )
            self.assertEqual(archive.extractfile(members[0]).read(), b"content")


class ThisTreesOwnBillOfMaterials(unittest.TestCase):
    def test_it_is_produced_and_agrees_with_the_lock(self) -> None:
        release.verify(ROOT, release.bom(ROOT))

    def test_it_names_the_format_and_the_interpreter(self) -> None:
        produced = release.bom(ROOT)
        self.assertEqual(produced["bomFormat"], release.FORMAT)
        self.assertEqual(produced["specVersion"], release.SPECIFICATION)
        properties = {
            entry["name"]: entry["value"]
            for entry in produced["metadata"]["properties"]
        }
        self.assertEqual(
            properties["raumbuch:interpreter"],
            (ROOT / release.INTERPRETER).read_text(encoding="utf-8").strip(),
        )

    def test_it_serialises_to_the_same_bytes_twice(self) -> None:
        first = json.dumps(release.bom(ROOT), indent=2, sort_keys=True)
        second = json.dumps(release.bom(ROOT), indent=2, sort_keys=True)
        self.assertEqual(first, second)


class TheBuildIsReproducible(unittest.TestCase):
    """Two builds of this checkout, compared byte for byte.

    Skipped where the build backend is not installed, and the skip is a skip
    rather than a pass: a suite run on a checkout with nothing installed reports
    that this was not asked, not that the artefacts agreed. Installing the
    backend costs ``pip install --require-hashes -r requirements.lock``.
    """

    def setUp(self) -> None:
        try:
            import setuptools  # noqa: F401
        except ImportError:
            self.skipTest(
                "the build backend is not installed, so no artefact was built "
                "and nothing here was compared. Running this costs "
                "pip install --require-hashes -r requirements.lock"
            )

    def test_two_builds_of_one_commit_agree_in_every_byte(self) -> None:
        into = Path(tempfile.mkdtemp())
        lines = release.reproducible(ROOT, into)
        self.assertEqual([line for line in lines if line.startswith("DIFFER")], [])
        self.assertEqual(len(lines), 3, lines)


if __name__ == "__main__":
    unittest.main()
