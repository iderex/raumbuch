"""The leg named ``format``: the formatter would change nothing in this tree.

It refuses rather than advises. A formatter that suggests produces a diff
argument in every review and a tree that is formatted in as many styles as it
has had contributors; a formatter that refuses produces neither, because the
question is settled before the change is read.

What it does not do is reformat anything. The leg reads the tree and says no.
Repairing it is one command, and it is the contributor's to run.
"""

from __future__ import annotations

from pathlib import Path

from raumbuch import gate
from raumbuch.gate import tool

ARGUMENTS = ["format", "--check", "."]
REPAIR = "python3 -m ruff format ."


def reformatted(lines: list[str]) -> list[str]:
    """The files the formatter would change, read out of what it printed.

    The tool points at each one with an arrow and a position. Everything else it
    prints is the change it would make, which the leg does not repeat.
    """
    paths = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("--> "):
            paths.append(stripped[4:].rsplit(":", 2)[0])
    return sorted(set(paths))


def run(root: Path) -> gate.Verdict:
    if not tool.installed():
        return gate.skipped(tool.absent("formats"))
    result = tool.invoke(root, ARGUMENTS)
    lines = tool.output(result)
    if result.returncode == 0:
        return gate.passed(
            f"the formatter would change nothing: {lines[-1] if lines else 'no file'}"
        )
    if result.returncode == 1:
        paths = reformatted(lines)
        return gate.refused(
            f"the formatter would change {len(paths)} file(s), and this tree is "
            f"the one it would change them from. Repair with {REPAIR}\n"
            + "\n".join(paths)
        )
    return gate.refused(
        "the formatter could not judge this tree, so this leg fails closed "
        f"rather than reading a broken tool as a clean tree (exit "
        f"{result.returncode})\n" + "\n".join(lines[-5:])
    )
