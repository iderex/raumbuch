"""The leg named ``index``: the catalogue spends each id once, and links both ways.

Record 0004 makes ``id`` the primary key of the catalogue and the thing a
citation names, and every property that follows from that needs the whole set of
records rather than one of them. This leg is where those refusals run on the
same route as everything else, so a duplicate id, a supersession pointing at
nothing, a link written from one end, or a correction list with a gap in it is
refused before a push rather than found by whoever downloaded the catalogue.

It carries no logic of its own. :mod:`raumbuch.catalogue` decides, and a
consumer validating a directory of records they downloaded runs exactly what
this runs.

**A green run here covers what a directory can decide and no more.** Record 0004
puts two further refusals on the catalogue gate, issue #77, because they compare
a record against what it was when its version landed and therefore read history.
This leg reads a directory, so a record whose asserted content changed under a
version it already published passes here.

The count is printed rather than assumed, including where it is zero. An empty
catalogue is the state of this tree until issue #73 lands, and a leg reporting
"every record is sound" over no records would be a claim about a set nobody
looked at.
"""

from __future__ import annotations

from pathlib import Path

from raumbuch import catalogue, gate, refusal


def run(root: Path) -> gate.Verdict:
    directory = root / catalogue.DIRECTORY
    if not directory.is_dir():
        return gate.refused(
            f"{catalogue.DIRECTORY.as_posix()}/ is not in this tree, so this leg "
            "fails closed rather than reading an absent catalogue as one that "
            "holds nothing wrong"
        )
    try:
        index = catalogue.read(directory)
    except refusal.Refused as refused:
        return gate.refused(
            f"the catalogue at {catalogue.DIRECTORY.as_posix()}/ is refused: {refused}"
        )
    superseded = index.superseded
    return gate.passed(
        f"{len(index)} record(s) under {catalogue.DIRECTORY.as_posix()}/ carry "
        f"{len(index)} distinct id(s) in the scheme record 0004 fixes, "
        f"{len(superseded)} of them superseded, every supersession link written "
        "from both ends and every correction list running to its record's version"
    )
