"""The build leg bites, and it bites for the reason it names.

The two halves are proved against each other rather than only against a clean
tree. A file that does not compile and a file that compiles and does not import
are one character apart in how they are written and nothing alike in what finds
them, so each fixture below is the near miss of the other.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from raumbuch.gate import importing

ROOT = Path(__file__).resolve().parents[1]

PACKAGE = "src/pkg/__init__.py"


def tree(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class WhatCountsAsTheTree(unittest.TestCase):
    def test_a_python_file_anywhere_in_it_is_found(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "tests/test_a.py": "", "one.py": ""})
            found = [path.as_posix() for path in importing.sources(root)]
        self.assertEqual(found, ["one.py", "src/pkg/__init__.py", "tests/test_a.py"])

    def test_a_build_artefact_or_a_cache_is_not_the_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    PACKAGE: "",
                    "build/lib/pkg/__init__.py": "def (",
                    "src/pkg/__pycache__/x.cpython-311.py": "def (",
                    "src/pkg.egg-info/y.py": "def (",
                },
            )
            found = [path.as_posix() for path in importing.sources(root)]
            verdict = importing.run(root)
        self.assertEqual(found, [PACKAGE])
        self.assertEqual(verdict.state, "passed", verdict.detail)

    def test_a_virtual_environment_in_the_checkout_is_not_the_tree(self) -> None:
        # The file under the environment does not compile, so if the leg reads
        # it at all this fixture is red. What is proved is the pruning and not
        # only the count: a passing verdict here is the leg never having opened
        # a file this repository did not write.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    PACKAGE: "",
                    ".venv/pyvenv.cfg": "home = /usr/bin\nversion = 3.14.6\n",
                    ".venv/lib/site-packages/dep/__init__.py": "def (",
                },
            )
            found = [path.as_posix() for path in importing.sources(root)]
            verdict = importing.run(root)
        self.assertEqual(found, [PACKAGE])
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("1 file(s) compile", verdict.detail)

    def test_the_same_directory_without_the_marker_is_the_tree(self) -> None:
        # The near miss of the fixture above, and the whole distance between
        # them is one file. A rule reading the directory name would leave this
        # one alone too, and a directory somebody called `.venv` and wrote code
        # in is work this repository is answerable for.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root, {PACKAGE: "", ".venv/lib/site-packages/dep/__init__.py": "def ("}
            )
            verdict = importing.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn(".venv/lib/site-packages/dep/__init__.py", verdict.detail)

    def test_an_environment_under_a_name_no_list_would_carry(self) -> None:
        # The other direction of the same near miss. The name here is one
        # nobody would put in a list of names for an environment, and the
        # marker says what it is.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    PACKAGE: "",
                    "py314/pyvenv.cfg": "home = /usr/bin\n",
                    "py314/lib/dep.py": "def (",
                },
            )
            found = [path.as_posix() for path in importing.sources(root)]
        self.assertEqual(found, [PACKAGE])

    def test_an_environment_under_src_contributes_no_module_name(self) -> None:
        # The import half asks the same question separately, so it needs the
        # same answer. An environment installed under `src/` would otherwise be
        # imported module by module into a subprocess this leg then reads a
        # verdict out of.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(
                root,
                {
                    PACKAGE: "",
                    "src/.venv/pyvenv.cfg": "home = /usr/bin\n",
                    "src/.venv/lib/dep/__init__.py": "",
                },
            )
            names = importing.modules(root)
        self.assertEqual(names, ["pkg"])

    def test_a_package_is_named_by_its_directory_and_not_by_its_init(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "src/pkg/inner/__init__.py": ""})
            names = importing.modules(root)
        self.assertEqual(names, ["pkg", "pkg.inner"])


class TheLegRefuses(unittest.TestCase):
    def test_a_file_that_does_not_compile_naming_it_and_the_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "tests/test_a.py": "x = 1\ndef (\n"})
            verdict = importing.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("do not compile", verdict.detail)
        self.assertIn("tests/test_a.py:2", verdict.detail)
        self.assertNotIn(PACKAGE, verdict.detail)

    def test_a_module_that_compiles_and_does_not_import(self) -> None:
        # The near miss of the fixture above. Nothing here is a syntax error, so
        # the compile half passes it and only the import half finds it.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "src/pkg/late.py": "import no_such_module\n"})
            verdict = importing.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("do not import", verdict.detail)
        self.assertIn("pkg.late: ModuleNotFoundError", verdict.detail)

    def test_a_module_that_raises_when_it_is_imported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "src/pkg/loud.py": "raise RuntimeError('no')\n"})
            verdict = importing.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("pkg.loud: RuntimeError: no", verdict.detail)

    def test_an_import_run_that_died_without_saying_which_module_died(self) -> None:
        # The near miss of the two fixtures above, and one character from
        # `sys.exit`. A module raising SystemExit is caught, named and reported
        # by the import program; a module calling `os._exit` kills that program
        # where it stands, so the run comes back non-zero with an empty report.
        # Reading that as a clean tree is how a whole package stops being
        # judged, so the leg fails closed and says the run could not judge.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "src/pkg/gone.py": "import os\n\nos._exit(3)\n"})
            verdict = importing.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("could not judge this tree", verdict.detail)
        self.assertIn("exit 3", verdict.detail)
        self.assertNotIn("do not import", verdict.detail)

    def test_the_same_module_exiting_the_way_that_can_be_reported(self) -> None:
        # The other half of the pair: `sys.exit` raises, so the module is named
        # and the leg takes the reporting path rather than the fail-closed one.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "src/pkg/gone.py": "import sys\n\nsys.exit(3)\n"})
            verdict = importing.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("1 module(s) that do not import", verdict.detail)
        self.assertIn("pkg.gone: SystemExit", verdict.detail)

    def test_a_tree_carrying_no_package_under_src(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {"tests/test_a.py": "x = 1\n"})
            verdict = importing.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("src/", verdict.detail)

    def test_a_tree_with_no_python_in_it_at_all(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verdict = importing.run(Path(directory))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("nothing here for a build", verdict.detail)


class TheLegLeavesTheTreeAsItFoundIt(unittest.TestCase):
    def test_judging_a_tree_writes_no_bytecode_into_it(self) -> None:
        # A leg that adds files to the tree it judges is a leg the next check
        # judges the output of. The import runs with bytecode writing off.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree(root, {PACKAGE: "", "src/pkg/inner.py": "value = 1\n"})
            verdict = importing.run(root)
            written = sorted(path.name for path in root.rglob("__pycache__"))
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertEqual(written, [])


class TheLegPasses(unittest.TestCase):
    def test_on_this_tree(self) -> None:
        verdict = importing.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("import", verdict.detail)

    def test_and_the_package_is_among_what_it_imported(self) -> None:
        names = importing.modules(ROOT)
        self.assertIn("raumbuch", names)
        self.assertIn("raumbuch.gate.importing", names)
        self.assertIn("raumbuch.cli", names)


if __name__ == "__main__":
    unittest.main()
