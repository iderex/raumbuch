"""The leg named ``layout``: the directory layout record 0001 fixes is present.

The list of directories is read out of record 0001 rather than copied here, so
there is one list and nothing to drift against. A directory that record 0001
names and the tree does not carry is refused, because the next person to add a
module puts it wherever the tree suggests, and the tree suggests whatever
happens to exist.

Reading it from the record has a second consequence worth naming: a change to
the layout block of record 0001 changes what this leg requires, which is the
intended coupling and the reason the record writes the layout as a fenced block.
"""

from __future__ import annotations

from pathlib import Path

from raumbuch import gate

RECORD = Path("docs/decisions/0001-the-means.md")
HEADING = "### The directory layout"


def declared(text: str) -> list[str]:
    """The directory paths of the layout block, in the order the record writes them.

    The block is the first fenced block after the layout heading. Each line
    carries a path and then prose about it, so the path is the first token, and
    a token is a path here exactly when it ends in a slash.
    """
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == HEADING)
    except StopIteration:
        return []
    inside = False
    paths: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("```"):
            if inside:
                break
            inside = True
            continue
        if not inside:
            continue
        token = line.split()[0] if line.split() else ""
        if token.endswith("/"):
            paths.append(token)
    return paths


def run(root: Path) -> gate.Verdict:
    record = root / RECORD
    if not record.is_file():
        return gate.refused(
            f"record 0001 fixes the layout and is not in the tree at {RECORD.as_posix()}, "
            "so what this leg requires cannot be read"
        )
    paths = declared(record.read_text(encoding="utf-8"))
    if not paths:
        return gate.refused(
            f"no directory layout could be read out of {RECORD.as_posix()}: "
            f"the block under {HEADING!r} is absent or names no path"
        )
    missing = [path for path in paths if not (root / path).is_dir()]
    if missing:
        return gate.refused(
            "named in the directory layout of record 0001 and not in the tree: "
            + ", ".join(missing)
        )
    return gate.passed(
        f"{len(paths)} path(s) named in the layout block of record 0001 are present"
    )
