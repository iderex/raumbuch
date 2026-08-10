"""The index: which ids a catalogue spends, and what a pinned consumer is told.

Record 0004 makes the identifier a pair. ``id`` is the primary key and never
moves; ``version`` is what a citation adds when the citer wants to be told that
what they cited has changed. Both halves are worth nothing without something
that reads every record at once, which is what this module is.

Three things read a record and they read different amounts of it. The parser
reads one string. The loader reads one document and the shape around it. This
reads the set: which ids exist, which of them are spent twice, and whether the
supersession links between them are written from both ends. A refusal here is
therefore one no schema and no loader could have made, and the split is record
0004's own.

The other half of the identifier is the report. A consumer that pinned
``(id, version)`` and gets no report when the entry has been corrected has been
served a different record than the one it cited, silently, and record 0004 is
explicit that this is the failure the version exists against. :func:`pinned` is
that report and it is one call.

**Withdrawal is not implemented and nothing here returns it.** Record 0004's
index carries three states and this module produces two: an entry is current or
it is superseded by a named id. The third, ``withdrawn``, is a row for an id
whose file may no longer be in the tree, so it cannot be derived from a walk of
the tree, and the register it would be read out of has no home yet. Whether a
withdrawn entry keeps its file at all is entry 10 of issue #2 and is open. What
that costs today is nothing, because no id has been published and none has been
withdrawn; what it will cost is named here rather than discovered by the first
consumer who withdraws one.

The two refusals record 0004 puts on the catalogue gate, issue #77, are not
here either, for the reason that record gives: they compare a record against
what it was when its version landed, so they read history and this reads a
directory. A run of this module over a downloaded catalogue covers the first
list and not the second.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from raumbuch import record as record_module
from raumbuch import refusal

#: Where the records live, per the layout block of record 0001.
DIRECTORY = Path("catalogue")

SUFFIX = ".toml"

#: The two states this module produces. Record 0004's third, ``withdrawn``, is
#: the one the module docstring says is not derivable from a tree.
CURRENT = "current"
SUPERSEDED = "superseded"


@dataclasses.dataclass(frozen=True)
class Entry:
    """One record, and the name of the thing it was read out of.

    ``source`` is carried so that a refusal naming two records can say which
    two files they were. An id equals a filename stem, so the pair is normally
    the same fact twice, and the one case where it is not is the one this
    module exists to refuse.
    """

    record: record_module.Record
    source: str

    @property
    def state(self) -> str:
        return CURRENT if self.record.superseded_by is None else SUPERSEDED


@dataclasses.dataclass(frozen=True)
class Report:
    """What a consumer pinned to ``(id, version)`` is told, and nothing more.

    The quiet case has to stay quiet. Record 0004 says so in as many words: a
    consumer that gets a report every time stops reading them, so a pin that
    matches the catalogue produces a report whose :attr:`quiet` is true and
    whose lines are empty.

    A record can be both corrected and superseded, and record 0004 describes
    the two as separate events rather than ranking them. So both are carried
    and neither hides the other; picking one to report would be a precedence no
    record fixes.
    """

    id: str
    pinned: int
    current: int
    corrections: tuple[dict[str, Any], ...]
    superseded_by: str | None

    @property
    def quiet(self) -> bool:
        return self.pinned == self.current and self.superseded_by is None

    def lines(self) -> list[str]:
        """The report as sentences, empty where there is nothing to say."""
        said: list[str] = []
        if self.current > self.pinned:
            said.append(
                f"{self.id} was corrected: version {self.pinned} was pinned and "
                f"this catalogue holds version {self.current}. The record "
                "returned is the current one."
            )
            said.extend(
                f"  version {entry.get('version')}, {entry.get('date')}: "
                f"{entry.get('reason')}"
                for entry in self.corrections
            )
        elif self.current < self.pinned:
            # Record 0004 names the case where the catalogue is ahead of the
            # pin and does not name this one, so the report states the two
            # numbers and draws no conclusion from them. A consumer pinned
            # above what a release holds is reading an older release than the
            # one it was built against, and what to do about that is not
            # settled anywhere this module could read.
            said.append(
                f"{self.id} is pinned at version {self.pinned} and this "
                f"catalogue holds version {self.current}, which is lower. "
                "Record 0004 does not fix what this means."
            )
        if self.superseded_by is not None:
            said.append(
                f"{self.id} is superseded by {self.superseded_by}. The record "
                "returned is the superseded one, because a supersession says "
                "the identity was wrong and following it would answer a "
                "question about one entry with a different entry."
            )
        return said


@dataclasses.dataclass(frozen=True)
class Index:
    """Every record of one catalogue, by id, judged as a set."""

    entries: dict[str, Entry]

    def __len__(self) -> int:
        return len(self.entries)

    def __contains__(self, identifier: object) -> bool:
        return identifier in self.entries

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.entries))

    @property
    def superseded(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                identifier
                for identifier, entry in self.entries.items()
                if entry.state == SUPERSEDED
            )
        )

    def pinned(self, identifier: str, version: int) -> Report:
        return pinned(self, identifier, version)


def build(documents: Iterable[tuple[str, bytes]]) -> Index:
    """An index over ``(source, bytes)`` pairs, or a refusal naming what is wrong.

    The source is the name the record was read out of, and its stem is what the
    loader compares the id against. Taking pairs rather than a directory is what
    lets a fixture be a set of records rather than a set of files, and it is the
    same code path a directory takes.
    """
    entries: dict[str, Entry] = {}
    for source, data in documents:
        loaded = record_module.loads(data, Path(source).stem)
        seen = entries.get(loaded.id)
        if seen is not None:
            refusal.refuse(
                refusal.ID_CARRIED_BY_TWO_RECORDS,
                f"the id {loaded.id!r} is carried by {seen.source} and by "
                f"{source}, and record 0004 makes it the one thing a citation "
                "names",
            )
        entries[loaded.id] = Entry(record=loaded, source=source)
    index = Index(entries=entries)
    for entry in entries.values():
        _corrections(entry)
    for entry in entries.values():
        _supersession(index, entry)
    return index


def read(directory: Path) -> Index:
    """The index of the catalogue at ``directory``.

    The walk descends. A flat directory cannot produce two records under one id,
    because the filesystem refuses two files with one name and the loader
    refuses an id that is not its filename stem, so a walk that stopped at the
    top would carry a refusal nothing could ever reach. It descends because a
    catalogue somebody assembled or downloaded is not obliged to be flat, and
    the id is the primary key of the whole of it rather than of one directory.
    """
    documents = []
    for path in sorted(directory.rglob(f"*{SUFFIX}")):
        documents.append((path.relative_to(directory).as_posix(), path.read_bytes()))
    return build(documents)


def pinned(index: Index, identifier: str, version: int) -> Report:
    """What a consumer holding ``(identifier, version)`` is told. One call.

    An id this catalogue does not hold is refused rather than returned empty.
    Record 0004: an id a release never had and an id it took away look identical
    to a caller that gets nothing back, and they are opposite statements.
    """
    entry = index.entries.get(identifier)
    if entry is None:
        refusal.refuse(
            refusal.UNKNOWN_IDENTIFIER,
            f"{identifier!r} is unknown to this catalogue, which is not the "
            "same statement as withdrawn: this release never held it",
        )
    return Report(
        id=identifier,
        pinned=version,
        current=entry.record.version,
        corrections=tuple(
            correction
            for correction in entry.record.corrections
            if _at(correction) is not None
            and version < _at(correction) <= entry.record.version
        ),
        superseded_by=entry.record.superseded_by,
    )


def _at(correction: dict[str, Any]) -> int | None:
    """The version a correction entry produced, where it is a whole number."""
    version = correction.get("version")
    if isinstance(version, bool) or not isinstance(version, int):
        return None
    return version


def _corrections(entry: Entry) -> None:
    """The correction list is exactly the versions from 2 up to the record's own.

    Record 0004 makes the list append-only and the history a consumer reads
    instead of the old copy it cannot have. Three ways that stops being true and
    one refusal covers them, because what a reader needs is the list it found
    beside the list it needed: a gap is a correction nobody is told about, a
    repeat is one told twice, and a list running past the version claims a
    version that is not on disk.
    """
    found = [_at(correction) for correction in entry.record.corrections]
    needed = list(range(2, entry.record.version + 1))
    if found != needed:
        refusal.refuse(
            refusal.CORRECTION_LIST_DOES_NOT_RUN_TO_THE_VERSION,
            f"{entry.source} is at version {entry.record.version} and its "
            f"correction list runs {found}, where record 0004 requires exactly "
            f"{needed}",
        )


def _supersession(index: Index, entry: Entry) -> None:
    """Both ends of every supersession link exist and name each other."""
    identifier = entry.record.id
    successor = entry.record.superseded_by
    if successor is not None:
        replacement = index.entries.get(successor)
        if replacement is None:
            refusal.refuse(
                refusal.SUPERSESSION_NAMES_NO_RECORD,
                f"{entry.source} says it is superseded by {successor!r}, which "
                "this catalogue does not hold, so a reader following it arrives "
                "nowhere",
            )
        if identifier not in replacement.record.supersedes:
            refusal.refuse(
                refusal.HALF_WRITTEN_SUPERSESSION,
                f"{entry.source} names {successor!r} as its successor and "
                f"{replacement.source} does not carry {identifier!r} in its "
                "supersedes, and record 0004 writes the link from both ends",
            )
    for displaced in entry.record.supersedes:
        replaced = index.entries.get(displaced)
        if replaced is None:
            refusal.refuse(
                refusal.SUPERSESSION_NAMES_NO_RECORD,
                f"{entry.source} says it supersedes {displaced!r}, which this "
                "catalogue does not hold, so nothing says what it displaced",
            )
        if replaced.record.superseded_by != identifier:
            refusal.refuse(
                refusal.HALF_WRITTEN_SUPERSESSION,
                f"{entry.source} supersedes {displaced!r} and "
                f"{replaced.source} does not name {identifier!r} as its "
                "successor, so a reader arriving at the old id is not sent "
                "forward",
            )
