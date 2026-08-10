"""The pin leg bites, once per way a pin stops being one.

Every fixture is a tree of its own. A workflow carrying a version literal inside
`.github/workflows/` would redden the check on `main` for as long as it stayed
there, and a lockfile fixture beside the real one would be a second lockfile
somebody could install from.

The near miss in each pair is the same string one character from a refusal: a
version literal that is an action's pin comment against one that is not, a lock
entry with a hash against the same entry without one, and a name in the manifest
against the same name in the lock.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from raumbuch.gate import toolchain

ROOT = Path(__file__).resolve().parents[1]

MANIFEST = """[build-system]
requires = ["setuptools>=77"]

[project]
name = "fixture"
dependencies = []

[project.optional-dependencies]
dev = ["ruff"]
"""

LOCK = """# A fixture lockfile.
ruff==0.16.2 \\
    --hash=sha256:0000000000000000000000000000000000000000000000000000000000000000
setuptools==84.0.0 \\
    --hash=sha256:1111111111111111111111111111111111111111111111111111111111111111
"""


def entry(name: str, digit: str, via: list[str] | None = None) -> str:
    """A lock entry, with the `# via` comment uv writes under it or without one.

    One parent goes on the `# via` line itself and several go on the indented
    lines under a bare `# via`, which are the two shapes uv emits and the two
    the leg has to read.
    """
    text = f"{name}==1.2.3 \\\n    --hash=sha256:{digit * 64}\n"
    if via is None:
        return text
    if len(via) == 1:
        return text + f"    # via {via[0]}\n"
    return text + "    # via\n" + "".join(f"    #   {parent}\n" for parent in via)


WORKFLOW = """name: fixture

jobs:
  one:
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - run: python3 -m raumbuch gate
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
        ".python-version": "3.14.6\n",
        "requirements.lock": LOCK,
        "pyproject.toml": MANIFEST,
        ".github/workflows/fixture.yml": WORKFLOW,
    }


def judged(files: dict[str, str]) -> list[str]:
    return toolchain.judge(tree(files))


class AVersionLiteralInAWorkflow(unittest.TestCase):
    def test_a_tool_version_written_into_a_job(self) -> None:
        files = clean()
        files[".github/workflows/fixture.yml"] = WORKFLOW.replace(
            "    steps:", '    env:\n      TOOL_VERSION: "1.26.1"\n    steps:'
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("1.26.1", faults[0])
        self.assertIn("the second copy this pin exists to prevent", faults[0])

    def test_and_the_pin_comment_after_an_action_hash_is_not_one(self) -> None:
        # The near miss, and the direction a broad rule gets wrong. The comment
        # after a forty character hash is what makes the pinning convention
        # readable, and a check that deleted it would cost the reader the other
        # half of this issue.
        self.assertEqual(judged(clean()), [])
        self.assertIn("# v7.0.1", WORKFLOW)

    def test_a_two_part_number_is_not_a_version_this_file_pins(self) -> None:
        # A standard's identifier in a comment is two parts, and a rule reaching
        # it would refuse a line that pins nothing. The pattern is three parts
        # for that reason.
        files = clean()
        files[".github/workflows/fixture.yml"] = WORKFLOW.replace(
            "name: fixture", "# OpenSSF Silver, OSPS-LE-01.01\nname: fixture"
        )
        self.assertEqual(judged(files), [])


class TheLockAgainstTheManifest(unittest.TestCase):
    def test_a_declared_distribution_that_is_not_locked(self) -> None:
        files = clean()
        files["pyproject.toml"] = MANIFEST.replace(
            'dev = ["ruff"]', 'dev = ["ruff"]\naudit = ["zizmor"]'
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("zizmor is declared in pyproject.toml and not pinned", faults[0])

    def test_a_locked_distribution_that_is_declared_nowhere(self) -> None:
        files = clean()
        files["requirements.lock"] = LOCK + entry("zizmor", "2")
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("declared nowhere in pyproject.toml", faults[0])
        self.assertIn("carries no `# via` saying what requires it", faults[0])
        self.assertIn("declare it in pyproject.toml", faults[0])

    def test_the_build_requirement_counts_as_declared(self) -> None:
        # An unpinned build backend is as much a supply-chain surface as a
        # runtime dependency and a less visible one, so it is in the set.
        self.assertIn("setuptools", toolchain.declared(MANIFEST))

    def test_a_name_spelled_differently_is_the_same_name(self) -> None:
        files = clean()
        files["pyproject.toml"] = MANIFEST.replace('dev = ["ruff"]', 'dev = ["Ruff"]')
        self.assertEqual(judged(files), [])


class ADistributionSomethingDeclaredRequires(unittest.TestCase):
    """The manifest says what was chosen and the lock says what that drags in.

    Comparing the two files as sets of names asks the manifest to carry a
    resolver's output, and the four names `jsonschema` requires were written
    into it for that reason. What admits a transitive distribution instead is
    the `# via` comment the lock already carries.
    """

    def test_a_via_naming_a_declared_distribution_admits_it(self) -> None:
        files = clean()
        files["requirements.lock"] = LOCK + entry("attrs", "2", ["ruff"])
        self.assertEqual(judged(files), [])

    def test_and_a_via_naming_something_nothing_declares_does_not(self) -> None:
        # The near miss. One entry, one comment, and the only difference is
        # whether the name after `# via` is a distribution this tree installs.
        # A rule that read the presence of the comment rather than the name it
        # gives would pass this and admit anything carrying three words.
        files = clean()
        files["requirements.lock"] = LOCK + entry("attrs", "2", ["ruffian"])
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("attrs is pinned in requirements.lock", faults[0])
        self.assertIn("carries `# via ruffian`", faults[0])
        self.assertIn("which nothing declared roots", faults[0])

    def test_a_via_block_of_several_parents_is_read(self) -> None:
        files = clean()
        files["requirements.lock"] = LOCK + entry("attrs", "2", ["ruffian", "ruff"])
        self.assertEqual(judged(files), [])

    def test_the_chain_runs_further_than_one_step(self) -> None:
        # `referencing` is required by `jsonschema-specifications`, which is
        # required by `jsonschema`, which is the declared one. A rule reading
        # one step would refuse the outermost of the three.
        files = clean()
        files["pyproject.toml"] = MANIFEST.replace(
            'dev = ["ruff"]', 'dev = ["ruff"]\nschema = ["jsonschema"]'
        )
        files["requirements.lock"] = (
            LOCK
            + entry("jsonschema", "2")
            + entry("jsonschema-specifications", "3", ["jsonschema"])
            + entry("referencing", "4", ["jsonschema-specifications"])
        )
        self.assertEqual(judged(files), [])

    def test_a_ring_of_names_nothing_declares_admits_none_of_them(self) -> None:
        files = clean()
        files["requirements.lock"] = (
            LOCK + entry("attrs", "2", ["rpds-py"]) + entry("rpds-py", "3", ["attrs"])
        )
        faults = judged(files)
        self.assertEqual(len(faults), 2, faults)
        self.assertIn("attrs is pinned", faults[0])
        self.assertIn("rpds-py is pinned", faults[1])

    def test_a_via_block_stops_at_the_next_entry(self) -> None:
        # The indented names under a bare `# via` belong to the entry above
        # them. A parser that carried the list across the next `name==version`
        # line would hand a second entry parents it does not have, and admit it.
        files = clean()
        files["requirements.lock"] = (
            LOCK + entry("attrs", "2", ["ruff", "setuptools"]) + entry("rpds-py", "3")
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("rpds-py is pinned", faults[0])

    def test_a_via_written_as_prose_names_no_distribution(self) -> None:
        # The lock on this tree carries one, saying which extra of the manifest
        # asked for `jsonschema`. It roots nothing, which is the direction that
        # fails closed: prose admits an entry only where the manifest already
        # does.
        files = clean()
        files["requirements.lock"] = LOCK + entry(
            "attrs", "2", ["the schema extra of pyproject.toml"]
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("attrs is pinned", faults[0])

    def test_a_declared_distribution_still_has_to_be_locked(self) -> None:
        # The other direction is untouched, and a parent that is itself
        # unlocked roots nothing: both halves are refused rather than one
        # covering for the other.
        files = clean()
        files["pyproject.toml"] = MANIFEST.replace(
            'dev = ["ruff"]', 'dev = ["ruff"]\naudit = ["zizmor"]'
        )
        files["requirements.lock"] = LOCK + entry("attrs", "2", ["zizmor"])
        faults = judged(files)
        self.assertEqual(len(faults), 2, faults)
        self.assertIn("zizmor is declared in pyproject.toml and not pinned", faults[0])
        self.assertIn("attrs is pinned", faults[1])


class TheLockItself(unittest.TestCase):
    def test_an_entry_with_no_hash(self) -> None:
        files = clean()
        files["requirements.lock"] = LOCK.replace(
            " \\\n    --hash=sha256:" + "0" * 64, ""
        )
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("carries no hash", faults[0])

    def test_an_entry_pinned_by_a_range(self) -> None:
        files = clean()
        files["requirements.lock"] = LOCK.replace("ruff==0.16.2", "ruff>=0.16.2")
        faults = judged(files)
        self.assertIn("pins nothing", faults[0])

    def test_the_hashes_of_an_entry_are_counted_across_its_lines(self) -> None:
        found = toolchain.locked(LOCK)
        self.assertEqual(found["ruff"], ("0.16.2", 1))
        self.assertEqual(found["setuptools"], ("84.0.0", 1))


class TheInterpreter(unittest.TestCase):
    def test_a_pin_file_that_is_not_there(self) -> None:
        files = clean()
        del files[".python-version"]
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn(".python-version", faults[0])

    def test_a_pin_that_names_a_series_rather_than_a_version(self) -> None:
        # `3.14` is whichever patch the runner happens to have that week, which
        # is what this file exists to stop.
        files = clean()
        files[".python-version"] = "3.14\n"
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("pinned to anything but one X.Y.Z version", faults[0])


class TheLegFailsClosed(unittest.TestCase):
    def test_a_tree_with_no_workflows_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verdict = toolchain.run(Path(directory))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("fails closed", verdict.detail)

    def test_a_tree_with_no_lockfile(self) -> None:
        files = clean()
        del files["requirements.lock"]
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("requirements.lock is not in this tree", faults[0])

    def test_a_tree_with_no_manifest(self) -> None:
        files = clean()
        del files["pyproject.toml"]
        faults = judged(files)
        self.assertEqual(len(faults), 1, faults)
        self.assertIn("pyproject.toml is not in this tree", faults[0])

    def test_the_leg_carries_a_departure_out_as_a_refusal(self) -> None:
        files = clean()
        files[".python-version"] = "3.14\n"
        verdict = toolchain.run(tree(files))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("1 way(s) the pin is not a pin", verdict.detail)


class OnThisTree(unittest.TestCase):
    def test_the_pin_holds_here(self) -> None:
        verdict = toolchain.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("no version literal", verdict.detail)

    def test_the_lock_answers_for_what_the_manifest_does_not_declare(self) -> None:
        # The four `jsonschema` requires are locked, are named nowhere in the
        # manifest, and are admitted by their own `# via` comments. Reading the
        # tree rather than a list written here, so the assertion follows the
        # lock when the next dependency with dependencies arrives.
        lock = (ROOT / toolchain.LOCK).read_text(encoding="utf-8")
        wanted = toolchain.declared(
            (ROOT / toolchain.MANIFEST).read_text(encoding="utf-8")
        )
        pinned = set(toolchain.locked(lock))
        parents = toolchain.required_by(lock)
        transitive = pinned - wanted
        self.assertTrue(transitive)
        self.assertEqual(
            transitive, toolchain.reachable(pinned, parents, wanted) - wanted
        )
        for name in transitive:
            self.assertTrue(parents[name] & pinned, name)

    def test_every_locked_distribution_carries_more_than_one_hash(self) -> None:
        # One hash per file the version published, so a wheel for a platform
        # this project is not built on today is pinned before somebody runs the
        # gate there.
        found = toolchain.locked((ROOT / toolchain.LOCK).read_text(encoding="utf-8"))
        self.assertTrue(found)
        for name, (version, hashes) in found.items():
            self.assertGreater(hashes, 1, f"{name}=={version}")


if __name__ == "__main__":
    unittest.main()
