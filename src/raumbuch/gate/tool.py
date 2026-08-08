"""Running ruff, which is the one tool behind the `format` and `lint` legs.

One tool does both jobs, which is one dependency to lock and one version to
pin rather than two. It is reached as a module of the interpreter running the
gate, so a leg judges the tree with the tool that interpreter has, and never a
different one that happens to be first on the path.

A leg whose tool is absent is not a leg that passed. It reports that it did not
run, why, and what running it would cost, which is the same accounting the gate
gives a leg that was not asked for.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

TOOL = "ruff"
INSTALL = 'python3 -m pip install -e ".[dev]"'


def installed() -> bool:
    return importlib.util.find_spec(TOOL) is not None


def absent(job: str) -> str:
    """What a leg says when the tool it needs is not there."""
    return (
        f"not run: {TOOL} is not installed for {sys.executable}, so nothing "
        f"{job} this tree. Running it costs installing the development extra, "
        f"{INSTALL}"
    )


def invoke(root: Path, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", TOOL, *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def output(result: subprocess.CompletedProcess[str]) -> list[str]:
    """The lines the tool wrote, from wherever it wrote them."""
    combined = f"{result.stdout}\n{result.stderr}"
    return [line for line in combined.splitlines() if line.strip()]
