"""The leg named ``documents``: what the pages promise, and where they point.

Two properties, both about the documents a reader meets before any code runs.

A paragraph a decision record fixes and the documentation quotes is carried byte
for byte. Records 0007 and 0014 each write such a paragraph inside a fence and
say in their own text that it is quoted and never paraphrased, because one
limitation restated in three voices is three chances for one of them to come out
more reassuring than the record argued for. Nothing compared the copies until
this leg, so the drift the fences were written against was invisible.

A link resolves. A document pointing at a file that is not there is a promise
the tree does not keep, and the reader who finds out is the one who needed the
page.

What this leg does not judge, and each of these is a bound rather than an
omission.

The report ``is_this_new`` returns is the third carrier record 0007 names, and
its copy is a constant in code rather than a document. Nothing here compares it,
and issue #105 holds that copy.

An anchor is not resolved. ``docs/checks.md#the-pin`` is judged as
``docs/checks.md``, and whether the heading exists is not asked. A link that is
only an anchor is not judged at all.

An address is not fetched. ``http``, ``https`` and ``mailto`` targets are left
alone, because reaching one would put a network call inside the gate, which
record 0014 refuses.

A link inside a fenced block is not a link. Record 0003 carries a worked example
and ``docs/checks.md`` quotes commands, and a path inside a fence is text being
shown rather than a pointer being followed.

Which paragraphs are quoted is a table in this module, anchored to the sentence
each record introduces its block with. A record that moves or renames that
sentence reddens this leg saying the anchor was not found, rather than passing
with nothing compared.
"""

from __future__ import annotations

import dataclasses
import os
import re
from pathlib import Path

from raumbuch import gate
from raumbuch.gate.importing import ENVIRONMENT_MARKER, NOT_THE_TREE
from raumbuch.gate.records import outside_fences

DECISIONS = Path("docs/decisions")

# An inline link, and a reference definition at the start of a line. The title
# a target may carry is dropped: it is prose, and what has to resolve is the
# path in front of it.
INLINE = re.compile(r"\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+[\"'(][^)]*)?\)")
REFERENCE = re.compile(r"^\[[^\]]+\]:\s*<?([^>\s]+)>?")

# Targets that are not a path in this tree. An address is not fetched and an
# anchor alone points inside the page it is written on.
ELSEWHERE = ("http://", "https://", "mailto:", "#")

# How many refusals of one kind are printed before the count stands in for the
# rest. A reader repairing a document needs the first of them, not all of them.
SHOWN = 10


@dataclasses.dataclass(frozen=True)
class Quotation:
    """A paragraph a record fixes, and the documents that carry it verbatim.

    ``introduced_by`` is the start of the line the record writes in front of the
    block. It is the anchor rather than the block's own text, because the text
    is what this leg is comparing and an anchor made of it would compare a thing
    to itself.
    """

    record: str
    introduced_by: str
    carried_by: tuple[str, ...]


# The two records that fix a quoted paragraph, and where each one writes it.
# Record 0007 names three carriers and one of them is the report constant, which
# is in code and is issue #105 rather than this leg.
QUOTED: tuple[Quotation, ...] = (
    Quotation("0007-what-same-means.md", "The positive paragraph:", ("README.md",)),
    Quotation("0007-what-same-means.md", "The limiting paragraph:", ("README.md",)),
    Quotation(
        "0014-network-and-personal-data.md",
        "### The paragraph the documentation quotes",
        ("README.md",),
    ),
)


def block_after(text: str, opening: str) -> str | None:
    """The first fenced block after a line, exactly as the record writes it.

    Nothing is stripped and nothing is joined differently from the source. The
    record fences the paragraph so that what a consumer reads is byte-identical
    to what was argued for, and a reader that normalised whitespace would pass a
    copy that is not.
    """
    lines = text.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.startswith(opening)),
        None,
    )
    if start is None:
        return None
    found: list[str] = []
    inside = False
    for line in lines[start + 1 :]:
        if line.startswith("```"):
            if inside:
                return "\n".join(found)
            inside = True
            continue
        if inside:
            found.append(line)
    return None


def drifted(root: Path) -> list[str]:
    """Every quoted paragraph a document does not carry as its record writes it."""
    faults = []
    for quotation in QUOTED:
        record = root / DECISIONS / quotation.record
        if not record.is_file():
            faults.append(
                f"{(DECISIONS / quotation.record).as_posix()} is where a quoted "
                "paragraph is fixed and it is not in this tree"
            )
            continue
        paragraph = block_after(
            record.read_text(encoding="utf-8"), quotation.introduced_by
        )
        if paragraph is None:
            faults.append(
                f"{(DECISIONS / quotation.record).as_posix()} carries no fenced "
                f"block after {quotation.introduced_by!r}, so what the "
                "documentation is supposed to quote cannot be read out of the "
                "record"
            )
            continue
        for name in quotation.carried_by:
            page = root / name
            if not page.is_file() or paragraph not in page.read_text(encoding="utf-8"):
                faults.append(
                    f"{name} does not carry the paragraph "
                    f"{(DECISIONS / quotation.record).as_posix()} fixes after "
                    f"{quotation.introduced_by!r}, byte for byte. The record is "
                    "the text; a copy that reads better is the drift the fence "
                    "exists against"
                )
    return faults


def documents(root: Path) -> list[Path]:
    """Every Markdown document of the tree, relative to the root, in a fixed order.

    Pruned during the walk on the same terms the build leg uses, so an
    environment or a build directory somebody left in the checkout is never
    descended into and never judged.
    """
    found: list[Path] = []
    for current, directories, files in os.walk(root):
        here = Path(current)
        directories[:] = [
            name
            for name in directories
            if name not in NOT_THE_TREE
            and not name.endswith(".egg-info")
            and not (here / name / ENVIRONMENT_MARKER).is_file()
        ]
        found.extend(
            (here / name).relative_to(root) for name in files if name.endswith(".md")
        )
    return sorted(found)


def targets(text: str) -> list[str]:
    """Every link target of a document that points at something in this tree."""
    found = []
    for line in outside_fences(text):
        for pattern in (INLINE, REFERENCE):
            for target in pattern.findall(line):
                if not target.startswith(ELSEWHERE):
                    found.append(target)
    return found


def broken(root: Path) -> list[str]:
    """Every link pointing at a path this tree does not hold."""
    faults = []
    for document in documents(root):
        text = (root / document).read_text(encoding="utf-8")
        for target in targets(text):
            path = target.split("#", 1)[0]
            if not path:
                continue
            if not (root / document.parent / path).exists():
                faults.append(
                    f"{document.as_posix()} links to {target}, and "
                    f"{(document.parent / path).as_posix()} is not in this tree"
                )
    return faults


def judge(root: Path) -> list[str]:
    """Every way a document promises something the tree does not hold."""
    return drifted(root) + broken(root)


def run(root: Path) -> gate.Verdict:
    if not (root / DECISIONS).is_dir():
        return gate.refused(
            f"{DECISIONS.as_posix()}/ is where the quoted paragraphs are fixed "
            "and it is not in this tree, so this leg fails closed rather than "
            "reading an absent set of records as a set fixing nothing"
        )
    faults = judge(root)
    if faults:
        shown = faults[:SHOWN]
        rest = len(faults) - len(shown)
        detail = f"{len(faults)} way(s) a document promises what the tree does not"
        if rest:
            shown.append(f"and {rest} more")
        return gate.refused(detail + "\n" + "\n".join(shown))
    pages = documents(root)
    links = sum(
        len(targets((root / page).read_text(encoding="utf-8"))) for page in pages
    )
    return gate.passed(
        f"{len(QUOTED)} paragraph(s) fixed by a decision record are carried byte "
        f"for byte where the record says they are, and {links} link(s) into this "
        f"tree from {len(pages)} document(s) resolve. An address is not fetched "
        "and an anchor is not resolved"
    )
