"""The leg named ``build``: every file compiles and every module imports.

Record 0001 chose a language with no compiler and said what follows from that:
where this project wants a refusal at the earliest moment, it has to be a check
rather than a build failure. This leg is that check, and it is the nearest thing
this means has to a build.

It asks two questions, because one of them does not answer the other.

Every Python file in the tree is compiled. That reaches a file nothing imports -
a fixture, a module a verb nobody ran on this branch touches - which is where a
syntax error survives longest.

Every module of the package is then imported, which compiling proves nothing
about. A name that moved, a module that was deleted from under an import, a
cycle between two modules: all three compile and none of them imports. The
import happens in a subprocess, and that is not caution about speed. Importing
into the process running the gate would leave whatever a module does at import
time inside the interpreter that goes on to judge the rest of the tree, and a
leg that changes the thing it judges is not a check. For the same reason the
subprocess is told to write no bytecode, so judging a tree does not add files to
it.

What this leg does not do is run anything. A module that imports and then fails
when it is called is the suite's question, and the ``tests`` leg asks it.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from raumbuch import gate

PACKAGE = Path("src")

# Directories that are not the tree. A checkout carries build artefacts and
# caches, and none of them is work this repository is answerable for. The set is
# written here rather than derived from git, so this leg judges a plain
# directory and needs no repository to do it.
NOT_THE_TREE = frozenset({".git", ".ruff_cache", "__pycache__", "build", "dist"})

# The file at the root of a virtual environment, which is where the interpreter
# itself looks to find out that it is in one. A directory carrying it, and
# everything under it, is not the tree.
#
# The marker rather than the name. `.venv`, `venv`, `env` and a bare version
# number are all names people give an environment, and each of them is also a
# name this repository could give a directory it wrote, so a list of names is
# wrong in both directions at once. The marker is written by the module that
# creates the environment and is not something anyone chooses.
#
# What it is for: an environment in the checkout is several hundred files
# somebody else wrote. Compiling them makes the count in the report a number
# about an environment rather than about this project, and it puts a
# dependency's syntax between this repository and a green leg whose whole
# subject is this repository's own source.
ENVIRONMENT_MARKER = "pyvenv.cfg"

# How many failures are printed before the count stands in for the rest. A
# hundred import errors from one deleted module are one fault, and a reader
# needs the first of them rather than all of them.
SHOWN = 10

# Imports are done by this program rather than by the gate's own interpreter, so
# every failure is reported rather than only the first. It exits non-zero when
# any module did not import, and prints one line per module that did not.
PROGRAM = """
import importlib
import sys

failed = 0
for name in sys.argv[1:]:
    try:
        importlib.import_module(name)
    except BaseException as error:
        failed += 1
        print(f"{name}: {type(error).__name__}: {error}")
sys.exit(1 if failed else 0)
"""


def is_an_environment(directory: Path) -> bool:
    return (directory / ENVIRONMENT_MARKER).is_file()


def python_files(root: Path) -> list[Path]:
    """Every Python file under the root, in a fixed order.

    What is not the tree is pruned during the walk rather than filtered out of
    its result. A directory this leg has decided it is not answerable for is
    then never descended into, so the environment nobody asked it to read costs
    nothing to skip, and one place decides what the tree is for both questions
    the leg asks.
    """
    found: list[Path] = []
    for current, directories, files in os.walk(root):
        here = Path(current)
        directories[:] = [
            name
            for name in directories
            if name not in NOT_THE_TREE
            and not name.endswith(".egg-info")
            and not is_an_environment(here / name)
        ]
        found.extend(here / name for name in files if name.endswith(".py"))
    return sorted(found)


def sources(root: Path) -> list[Path]:
    """Every Python file of the tree, relative to the root, in a fixed order."""
    return [path.relative_to(root) for path in python_files(root)]


def modules(root: Path) -> list[str]:
    """The dotted name of every module under ``src/``, in a fixed order.

    A package is named by its directory, so ``__init__`` never appears in a name
    and importing the package is what imports it.
    """
    source_root = root / PACKAGE
    names = []
    for path in python_files(source_root):
        relative = path.relative_to(source_root)
        parts = list(relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        if parts:
            names.append(".".join(parts))
    return names


def uncompilable(root: Path, paths: list[Path]) -> list[str]:
    """The files that are not Python, each with the line the compiler stopped at.

    The bytes are compiled rather than the decoded text, so a file declaring its
    own encoding is read the way the interpreter reads it and a file declaring a
    broken one is refused here instead of at a run.
    """
    broken = []
    for relative in paths:
        try:
            compile((root / relative).read_bytes(), relative.as_posix(), "exec")
        except SyntaxError as error:
            where = f":{error.lineno}" if error.lineno else ""
            broken.append(f"{relative.as_posix()}{where}: {error.msg}")
        except ValueError as error:
            # A declared encoding nothing can read, and a null byte in the
            # source, arrive here rather than as a SyntaxError.
            broken.append(f"{relative.as_posix()}: {error}")
    return broken


def summarise(what: str, failures: list[str]) -> str:
    rest = len(failures) - SHOWN
    shown = failures[:SHOWN]
    if rest > 0:
        shown.append(f"and {rest} more of the same kind")
    return f"{len(failures)} {what}\n" + "\n".join(shown)


def imported(root: Path, names: list[str]) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    # The tree at this root is what is judged, ahead of whatever is installed in
    # the environment the gate happens to be running in.
    existing = environment.get("PYTHONPATH")
    source_root = str(root / PACKAGE)
    environment["PYTHONPATH"] = (
        f"{source_root}{os.pathsep}{existing}" if existing else source_root
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-c", PROGRAM, *names],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def run(root: Path) -> gate.Verdict:
    paths = sources(root)
    if not paths:
        return gate.refused(
            "no Python file was found under this root, so there is nothing here "
            "for a build to be a build of"
        )
    broken = uncompilable(root, paths)
    if broken:
        return gate.refused(summarise("file(s) that do not compile", broken))
    names = modules(root)
    if not names:
        return gate.refused(
            f"{len(paths)} file(s) compile and no module was found under "
            f"{PACKAGE.as_posix()}/, so the package record 0001 puts there is "
            "not in this tree"
        )
    result = imported(root, names)
    if result.returncode != 0:
        failures = [line for line in result.stdout.splitlines() if line.strip()]
        if not failures:
            return gate.refused(
                "the import run could not judge this tree, so this leg fails "
                "closed rather than reading a broken run as a clean tree "
                f"(exit {result.returncode})\n" + result.stderr.strip()
            )
        return gate.refused(summarise("module(s) that do not import", failures))
    return gate.passed(
        f"{len(paths)} file(s) compile and {len(names)} module(s) under "
        f"{PACKAGE.as_posix()}/ import"
    )
