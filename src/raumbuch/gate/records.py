"""The leg named ``records``: a decision record follows the shape 0000 fixes.

Record 0000 says what a decision record looks like, and a shape nothing refuses
is an explanation rather than a rule. This leg is the refusal.

Nothing here carries a second copy of that shape. The required sections and the
allowed status words are read out of record 0000's own fenced blocks, so a
change to a heading there changes what this leg requires, which is the coupling
the record asks for and the reason it writes both lists inside fences.

Reading a Markdown document by scanning for lines that begin with a hash is the
mistake this leg exists on the far side of, and record 0000 says so in its own
text. Its required section list is written inside a fence, and record 0003
carries a worked example whose comments begin with a hash too. A scanner that
takes those for headings refuses its own specification on the first run. A
heading here is a heading outside a fence, in both directions and everywhere in
this module.

The index is read the same way and in both directions, because an index that
silently misses a record is worse than no index: a reader who trusts it
concludes the decision was never made. A row is a table row anchored at the
start of a line, never an occurrence of a filename, because the prose above the
table links to record 0000 as well and that link is the index doing its job.

What this leg does not judge is written in ``docs/checks.md`` beside what it
does.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from raumbuch import gate

DECISIONS = Path("docs/decisions")
INDEX = "README.md"
SHAPE = "0000-how-a-decision-is-recorded.md"

# Where record 0000 writes each of the two lists this leg reads out of it.
SECTIONS_HEADING = "### The required sections"
STATUS_INTRODUCTION = "`## Status` holds exactly one of these words or phrases"

# A record is named for its number and nothing else resolves it, since the
# number is what an index row, a supersession and a reader all cite.
NAMED = re.compile(r"^(\d{4})-[^/]+\.md$")

# The status that points at another record. Record 0000 writes it with a
# placeholder number, which is what makes the allowed set readable out of the
# record and also what stops a literal comparison from working.
PLACEHOLDER = "NNNN"
SUPERSEDED = re.compile(r"^Superseded by (\d{4})$")

# `# NNNN. Title`, the one heading above `##` level.
TITLE = re.compile(r"^# (\d{4})\. \S")

# A row of the index: a link at the start of a line, inside a table cell.
ROW = re.compile(r"^\| \[(\d{4})\]\(([^)]+)\) \|")

# Record 0000 hands this leg two rules about a correction beyond the shape of a
# record: the date form in the heading, and that a finished record gains none.
CORRECTION = re.compile(r"^### Correction, (\d{4}-\d{2}-\d{2}), \S")
CORRECTION_HEADING = "### Correction,"

# How many refusals of one kind are printed before the count stands in for the
# rest. A reader repairing a shape needs the first of them, not all of them.
SHOWN = 10


def outside_fences(text: str) -> Iterator[str]:
    """Every line of a document that is not inside a fenced block.

    A fence opens and closes on a line whose first three characters are
    backticks, which is the form every record in this tree uses. Indented code
    is not a fence and is not treated as one: record 0000 writes its own lists
    in backticked blocks, and this leg follows the record rather than Markdown
    in general.
    """
    inside = False
    for line in text.splitlines():
        if line.startswith("```"):
            inside = not inside
            continue
        if not inside:
            yield line


def block_after(text: str, heading: str) -> list[str]:
    """The lines of the first fenced block after a heading, stripped of blanks."""
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return []
    inside = False
    found: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("```"):
            if inside:
                break
            inside = True
            continue
        if inside and line.strip():
            found.append(line.strip())
    return found


def block_after_prose(text: str, opening: str) -> list[str]:
    """The same, where what introduces the block is a sentence rather than a heading."""
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith(opening))
    except StopIteration:
        return []
    return block_after("\n".join(lines[start:]), lines[start].strip())


def required(shape: str) -> list[str]:
    """The `##` headings every record carries, in the order record 0000 writes them.

    The title line of the block is not one of them: it carries the record's own
    number and title, so it is checked against the filename rather than compared
    as a string.
    """
    return [
        line for line in block_after(shape, SECTIONS_HEADING) if line.startswith("## ")
    ]


def allowed(shape: str) -> list[str]:
    """The status words a record may carry, as record 0000 writes them."""
    return block_after_prose(shape, STATUS_INTRODUCTION)


def headings(text: str) -> list[str]:
    """The `#` and `##` headings of a record, in order, fences excluded.

    Record 0000 leaves everything below `##` free, so a correction heading and
    whatever else a record wants under its answer are not sections and are not
    compared against anything here.
    """
    return [
        line.strip()
        for line in outside_fences(text)
        if line.startswith("# ") or line.startswith("## ")
    ]


def section(text: str, heading: str) -> list[str]:
    """The non-empty lines under a `##` heading, up to the next heading of any level."""
    found: list[str] = []
    collecting = False
    for line in outside_fences(text):
        if line.strip() == heading:
            collecting = True
            continue
        if collecting and line.startswith("#"):
            break
        if collecting and line.strip():
            found.append(line.strip())
    return found


def corrections(text: str) -> list[str]:
    """Every correction heading of a record, fences excluded."""
    return [
        line.strip()
        for line in outside_fences(text)
        if line.strip().startswith(CORRECTION_HEADING)
    ]


def rows(index: str) -> list[tuple[str, str]]:
    """Every row of the index, as its number and the file it points at."""
    found = []
    for line in index.splitlines():
        match = ROW.match(line)
        if match:
            found.append((match.group(1), match.group(2)))
    return found


def statuses(record: str, permitted: list[str]) -> tuple[str | None, str | None]:
    """What a record's status says, and the record it points at where it points.

    The allowed set is read out of record 0000, where the superseding form is
    written with a placeholder number. A status matching that form is accepted
    for its shape and its target is handed back for the caller to resolve.
    """
    lines = section(record, "## Status")
    if len(lines) != 1:
        return None, None
    said = lines[0]
    if said in permitted:
        return said, None
    for form in permitted:
        if PLACEHOLDER not in form:
            continue
        match = SUPERSEDED.match(said)
        if match and form.replace(PLACEHOLDER, match.group(1)) == said:
            return said, match.group(1)
    return None, None


def sections_of(text: str, number: str, wanted: list[str]) -> list[str]:
    """What a record's own headings say against the list record 0000 fixes.

    ``## Supersedes`` is dropped before the comparison: record 0000 allows it,
    requires it of nobody, and fixes no position for it.
    """
    faults = []
    found = headings(text)
    title = found[0] if found else ""
    named = TITLE.match(title)
    if not named or named.group(1) != number:
        faults.append(
            f"the first heading is {title!r} and record 0000 requires "
            f"'# {number}. Title'"
        )
    carried = [
        line for line in found[1:] if line.startswith("## ") and line != "## Supersedes"
    ]
    if carried == wanted:
        return faults
    missing = [line for line in wanted if line not in carried]
    if missing:
        faults.append(f"missing required section(s) {', '.join(missing)}")
    else:
        faults.append(
            "the required sections are present and out of the order record 0000 "
            f"fixes: {' '.join(carried)}"
        )
    return faults


def status_of(
    text: str, permitted: list[str], numbers: dict[str, Path], where: str
) -> list[str]:
    """What a record's status says, and what record 0000 requires of a correction.

    The two are one function because both depend on the same reading. A
    correction is refused on a record that was superseded, and whether it was
    superseded is what the status says.
    """
    faults = []
    said, points_at = statuses(text, permitted)
    if said is None:
        carried = section(text, "## Status") or ["nothing"]
        faults.append(
            f"## Status carries {' '.join(carried)!r}, and record 0000 allows "
            f"{', '.join(permitted)}"
        )
    elif points_at is not None and points_at not in numbers:
        faults.append(f"superseded by record {points_at}, which is not in {where}")
    for heading in corrections(text):
        if said is not None and points_at is not None:
            faults.append(
                f"{heading!r} on a record superseded by {points_at}, and record "
                "0000 gives a finished record no correction"
            )
        if not CORRECTION.match(heading):
            faults.append(f"{heading!r} carries no YYYY-MM-DD date after the comma")
    return faults


def index_of(directory: Path, numbers: dict[str, Path]) -> list[str]:
    """Both directions between the index and the files beside it."""
    index_file = directory / INDEX
    if not index_file.is_file():
        return [
            f"{directory.name}/{INDEX} is the index and it is not in the tree, "
            "so no record can be found from it"
        ]
    faults = []
    counted: dict[str, int] = {}
    for number, target in rows(index_file.read_text(encoding="utf-8")):
        counted[number] = counted.get(number, 0) + 1
        if not (directory / target).is_file():
            faults.append(
                f"{INDEX}: the row for {number} points at {target}, which is not "
                "in the tree"
            )
    for number, path in sorted(numbers.items()):
        if counted.get(number, 0) == 0:
            faults.append(f"{INDEX}: no row for {path.name}, which is in the tree")
        elif counted[number] > 1:
            faults.append(
                f"{INDEX}: {counted[number]} rows for {number}, and record 0000 "
                "puts every record in the index exactly once"
            )
    return faults


def judge(directory: Path) -> list[str]:
    """Every way the records under a directory depart from the shape 0000 fixes.

    One list rather than a verdict, so the caller reports all of them and a
    contributor repairing a record is not sent back around the loop for the
    next one.
    """
    shape_file = directory / SHAPE
    if not shape_file.is_file():
        return [
            f"{SHAPE} is the record that fixes the shape and it is not in "
            f"{directory.name}/, so what this leg requires cannot be read"
        ]
    shape = shape_file.read_text(encoding="utf-8")
    wanted = required(shape)
    if not wanted:
        return [
            f"no required section list could be read out of {SHAPE}: the block "
            f"under {SECTIONS_HEADING!r} is absent or names no section"
        ]
    permitted = allowed(shape)
    if not permitted:
        return [
            f"no status words could be read out of {SHAPE}: the block after "
            f"{STATUS_INTRODUCTION!r} is absent or is empty"
        ]

    files = sorted(path for path in directory.glob("*.md") if path.name != INDEX)
    numbers = {}
    for path in files:
        named = NAMED.match(path.name)
        if not named:
            continue
        numbers[named.group(1)] = path

    faults: list[str] = []
    where = f"{directory.name}/"
    for path in files:
        named = NAMED.match(path.name)
        if not named:
            faults.append(
                f"{path.name}: not named NNNN-short-title.md, so no number "
                "resolves it and no index row can point at it"
            )
            continue
        text = path.read_text(encoding="utf-8")
        found = sections_of(text, named.group(1), wanted)
        found += status_of(text, permitted, numbers, where)
        faults.extend(f"{path.name}: {fault}" for fault in found)
    return faults + index_of(directory, numbers)


def run(root: Path) -> gate.Verdict:
    directory = root / DECISIONS
    if not directory.is_dir():
        return gate.refused(
            f"{DECISIONS.as_posix()}/ is where the decision records live and it "
            "is not in this tree, so this leg fails closed rather than reading "
            "an absent directory as a set of well formed records"
        )
    faults = judge(directory)
    if faults:
        rest = len(faults) - SHOWN
        shown = faults[:SHOWN]
        if rest > 0:
            shown.append(f"and {rest} more, which a full run prints")
        return gate.refused(
            f"{len(faults)} departure(s) from the shape record 0000 fixes\n"
            + "\n".join(shown)
        )
    counted = len([path for path in directory.glob("*.md") if path.name != INDEX])
    return gate.passed(
        f"{counted} record(s) under {DECISIONS.as_posix()}/ carry the sections "
        "and the status words record 0000 fixes, and the index names each of "
        "them once and points at nothing absent"
    )
