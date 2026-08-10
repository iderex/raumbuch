"""The release artefacts: a distribution that rebuilds byte for byte, and its
bill of materials.

A catalogue whose results cannot be reproduced is a catalogue of claims, and the
same applies to the artefact that produced them. Record 0006 anchors a stored
derived value to a digest over the source that produced it, and record 0012
promises that two runs of one input agree. Neither is worth anything if the
program those runs were made with cannot be brought back: a classification
record carrying a toolchain version and a commit is decoration where those two
do not determine an artefact.

## What makes a build vary, and what is done about each

Measured on this tree rather than assumed. Two builds of one commit, with
nothing set, disagree in both artefacts. With ``SOURCE_DATE_EPOCH`` in the
environment the wheel is byte-identical and the sdist is not, because setuptools
applies the variable to the wheel and stamps the sdist's tar members and its
gzip header with the wall clock instead. The member list, its order, the sizes,
the modes and the ownership already agree; only the times move.

So the epoch is set from the commit, which ties the artefact to the thing a
record names rather than to the hour the build ran, and the sdist is rewritten
afterwards with every time set to that same epoch.

## The bill of materials

Produced here rather than assembled by hand afterwards, and produced out of
``requirements.lock``, which is already the one file saying which version of
every distribution arrives and the hash of every file it publishes. A second
place holding the same list is a second place to be wrong.

That is what ``verify`` is for. A document disagreeing with the lock it claims
to describe is refused, naming the component and what disagreed, so a bill of
materials that was edited, carried over from an older build, or written by hand
cannot be shipped beside a distribution built from a different lock.

What this module does not do. It builds and it describes; it publishes nothing
and it tags nothing. What a release contains and how one is made is issue #100,
and no step here is a release procedure.
"""

from __future__ import annotations

import dataclasses
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tomllib
from pathlib import Path

from raumbuch.gate.toolchain import (
    HASH,
    LOCK,
    LOCKED,
    MANIFEST,
    declared,
    locked,
    normalised,
)

INTERPRETER = Path(".python-version")

# CycloneDX, at the version whose field names are used below. The format is
# named in the document rather than left to be inferred from its shape, because
# a consumer has to know which specification the keys come from before it can
# read one of them.
FORMAT = "CycloneDX"
SPECIFICATION = "1.6"

# One subprocess per artefact, and the separation is not tidiness. The backend's
# two entry points share the distutils distribution object inside one
# interpreter, and a wheel built first leaves the sdist's output directory
# pointing at `bdist_wheel/` under the checkout: the call returns the name it
# was asked for and the file is written somewhere else. Measured on this tree.
#
# The subprocess also keeps the environment variable the build reads out of the
# process that judges what the build produced, and keeps whatever the backend
# does at import time out of it.
#
# The name comes back behind a marker because the backend writes its own log to
# the same stream, so a reader of the last line would get whichever file
# setuptools happened to mention last.
MARKER = "raumbuch-built:"
BUILD = (
    "import setuptools.build_meta as backend, sys;"
    f"print({MARKER!r} + getattr(backend, 'build_' + sys.argv[1])(sys.argv[2]))"
)
ARTEFACTS = ("wheel", "sdist")


class Refused(Exception):
    """A release artefact that may not be produced, and the reason.

    Everything refused here is a way the artefact would be shipped saying
    something about itself that is not true, and a distribution whose bill of
    materials is wrong is worse than one carrying none: it is the same object
    with an assurance attached.
    """


@dataclasses.dataclass(frozen=True)
class Component:
    """One distribution the build installs, as the lock pins it."""

    name: str
    version: str
    hashes: tuple[str, ...]


def epoch(root: Path) -> int:
    """The commit date, which is what every time in the artefact is set to.

    The commit rather than the clock. A build of one commit made twice, on two
    machines, two years apart, has one answer here, and it is the same thing a
    record's stamp names.
    """
    finished = subprocess.run(
        ["git", "log", "-1", "--format=%ct"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    stamp = finished.stdout.strip()
    if finished.returncode != 0 or not stamp.isdigit():
        raise Refused(
            "every time in the artefact is set to the commit date, and git did "
            f"not answer with one in {root}: "
            f"{finished.stderr.strip() or stamp!r}"
        )
    return int(stamp)


def hashes_by_distribution(lock: str) -> dict[str, set[str]]:
    """Which sha256 hashes each entry of the lock carries, by distribution.

    The lock's own parser answers how many an entry has; this answers which they
    are, over the same line shapes. An entry opens on the line naming the
    distribution and runs until the next one does.
    """
    found: dict[str, set[str]] = {}
    current: str | None = None
    for line in lock.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        opened = LOCKED.match(stripped)
        if opened:
            current = normalised(opened.group(1))
            found.setdefault(current, set())
        if current is not None:
            found[current].update(HASH.findall(line))
    return found


def components(root: Path) -> list[Component]:
    """Every distribution the lock pins, with its version and its hashes.

    The manifest is read too, in one direction. A name it declares and the lock
    does not is a dependency arriving unpinned, and a document assembled from
    the lock alone would not carry it and so would not say it was missing. The
    other direction is the ``pin`` leg's, which refuses a lock entry nothing
    installs.
    """
    lock_text = (root / LOCK).read_text(encoding="utf-8")
    pinned = locked(lock_text)
    missing = sorted(
        declared((root / MANIFEST).read_text(encoding="utf-8")) - set(pinned)
    )
    if missing:
        raise Refused(
            "a bill of materials cannot carry a hash for a distribution nothing "
            f"pins, and pyproject.toml declares {', '.join(missing)} with no "
            f"entry in {LOCK}"
        )

    carried = hashes_by_distribution(lock_text)
    found = []
    for name in sorted(pinned):
        version, count = pinned[name]
        if count == 0:
            raise Refused(
                f"{name}=={version} is pinned to a version and to no hash, so a "
                "bill of materials would list a name resolved at install time "
                "as though it were a fixed set of files"
            )
        found.append(Component(name, version, tuple(sorted(carried[name]))))
    return found


def bom(root: Path) -> dict:
    """The bill of materials for this tree, produced from the lock.

    The interpreter is a component too. It is a runtime rather than a
    distribution, so it is not in the lock and carries no hash, and it is
    recorded as a property rather than pretended into the component list where a
    consumer would look for one.
    """
    project = tomllib.loads((root / MANIFEST).read_text(encoding="utf-8"))["project"]
    return {
        "bomFormat": FORMAT,
        "specVersion": SPECIFICATION,
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": project["name"],
                "version": project["version"],
                "licenses": [{"expression": project["license"]}],
            },
            "properties": [
                {"name": "raumbuch:source-date-epoch", "value": str(epoch(root))},
                {
                    "name": "raumbuch:interpreter",
                    "value": (root / INTERPRETER).read_text(encoding="utf-8").strip(),
                },
            ],
        },
        "components": [
            {
                "type": "library",
                "name": component.name,
                "version": component.version,
                "hashes": [
                    {"alg": "SHA-256", "content": digest.removeprefix("--hash=sha256:")}
                    for digest in component.hashes
                ],
            }
            for component in components(root)
        ],
    }


def verify(root: Path, document: dict) -> None:
    """Refuse a bill of materials that disagrees with the lock it describes.

    This is what makes "produced by the build" mean something. A document
    assembled by hand, edited afterwards, or carried over from a build against a
    different lock disagrees here on the component set, on a version or on a
    hash, and each of the three is named rather than reported as a mismatch.
    """
    expected = {
        component.name: (
            component.version,
            frozenset(
                digest.removeprefix("--hash=sha256:") for digest in component.hashes
            ),
        )
        for component in components(root)
    }
    carried = {
        normalised(component["name"]): (
            component["version"],
            frozenset(entry["content"] for entry in component.get("hashes", [])),
        )
        for component in document.get("components", [])
    }

    absent = sorted(set(expected) - set(carried))
    if absent:
        raise Refused(
            f"{LOCK} pins {', '.join(absent)} and the bill of materials does not "
            "name them, so the document describes a different install"
        )
    extra = sorted(set(carried) - set(expected))
    if extra:
        raise Refused(
            f"the bill of materials names {', '.join(extra)} and {LOCK} pins "
            "nothing by that name"
        )
    for name in sorted(expected):
        version, digests = expected[name]
        their_version, their_digests = carried[name]
        if their_version != version:
            raise Refused(
                f"{name} is pinned at {version} in {LOCK} and the bill of "
                f"materials says {their_version}"
            )
        if their_digests != digests:
            raise Refused(
                f"{name}=={version} is pinned to {len(digests)} file hash(es) in "
                f"{LOCK} and the bill of materials carries "
                f"{len(their_digests) - len(their_digests & digests)} that are "
                "not among them; a document whose hashes are not the lock's "
                "describes a different set of files"
            )


def normalise_sdist(path: Path, when: int) -> None:
    """Rewrite a source distribution with every time set to ``when``.

    Two builds of one tree produce tarballs that already agree on which members
    they hold, in what order, at what size, with what mode and what ownership.
    They disagree on the times, in two places: each member's mtime, which
    setuptools takes from the staged copy on disk, and the gzip stream's own
    header.

    Nothing but the times is touched. The members are read and written back in
    the order they arrived, so this cannot make two tarballs of differing
    content agree, which is what would make it a normalisation that hides a
    difference rather than one that removes a clock.
    """
    with tarfile.open(path, "r:gz") as archive:
        members = []
        for member in archive.getmembers():
            payload = archive.extractfile(member)
            members.append((member, payload.read() if payload is not None else None))

    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode="w", format=tarfile.GNU_FORMAT) as archive:
        for member, payload in members:
            member.mtime = when
            archive.addfile(
                member, io.BytesIO(payload) if payload is not None else None
            )

    # Two fields of the gzip header, and neither is content.
    #
    # ``mtime=0`` rather than ``when``: the field is the time the stream was
    # compressed and zero is what the format reserves for "not recorded". The
    # build's own time is in the member headers, where a reader of the archive
    # will find it.
    #
    # ``filename=""`` because gzip otherwise records the name of the file it was
    # given, which it takes off the open file object. Two archives of identical
    # content written to two paths would differ in their headers alone, which is
    # the shape this whole module exists to remove and which a build into two
    # comparison directories would not have shown.
    with (
        open(path, "wb") as out,
        gzip.GzipFile(filename="", fileobj=out, mode="wb", mtime=0) as stream,
    ):
        stream.write(inner.getvalue())


def one(root: Path, into: Path, kind: str, when: int) -> Path:
    """Build one artefact, in an interpreter that builds nothing else."""
    finished = subprocess.run(
        [sys.executable, "-c", BUILD, kind, str(into.resolve())],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env={
            **os.environ,
            "SOURCE_DATE_EPOCH": str(when),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )
    named = [
        line.removeprefix(MARKER).strip()
        for line in finished.stdout.splitlines()
        if line.startswith(MARKER)
    ]
    if finished.returncode != 0 or len(named) != 1:
        tail = finished.stderr.strip().splitlines()
        raise Refused(
            f"the backend did not build a {kind} from {root}: "
            f"{tail[-1] if tail else 'it named ' + str(len(named)) + ' artefact(s)'}"
        )
    built = into / named[0]
    if not built.is_file():
        raise Refused(
            f"the backend named {named[0]} as the {kind} and wrote no such file "
            f"into {into}"
        )
    return built


def build(root: Path, into: Path) -> list[Path]:
    """Build the wheel, the sdist and the bill of materials into ``into``.

    The backend is called through its PEP 517 interface rather than through a
    build frontend. A frontend's job is to make an isolated environment and
    install the build requirement into it, which is a resolution at build time
    in the one tree that has been careful to have none: setuptools is pinned in
    ``requirements.lock`` and installed from there, and a frontend would fetch
    its own copy instead.
    """
    into.mkdir(parents=True, exist_ok=True)
    when = epoch(root)
    built = [one(root, into, kind, when) for kind in ARTEFACTS]
    wheel, sdist = built
    normalise_sdist(sdist, when)

    document = bom(root)
    verify(root, document)
    materials = into / f"{document['metadata']['component']['name']}.cdx.json"
    materials.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return [wheel, sdist, materials]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reproducible(root: Path, into: Path) -> list[str]:
    """Build twice into two directories and report whether the bytes agree.

    Two builds rather than one build compared against a stored hash. A stored
    hash goes stale on the next commit and is then either updated by hand every
    time, which is a ritual nobody reads, or it is wrong. Two builds in one run
    ask the property directly and have nothing to keep up to date.
    """
    first = build(root, into / "first")
    second = build(root, into / "second")
    lines = []
    for left, right in zip(first, second, strict=True):
        agree = digest(left) == digest(right)
        lines.append(
            f"{'same  ' if agree else 'DIFFER'}  {left.name}  {digest(left)}"
            + ("" if agree else f"  and  {digest(right)}")
        )
    return lines


def main(root: Path, into: Path, out=None) -> int:
    """Build twice, print what came back, and refuse a byte that moved."""
    out = sys.stdout if out is None else out
    try:
        lines = reproducible(root, into)
    except Refused as refusal:
        print(f"raumbuch release, against {root}", file=out)
        print(f"  refused  {refusal}", file=out)
        return 1
    print(f"raumbuch release, against {root}", file=out)
    for line in lines:
        print(f"  {line}", file=out)
    moved = [line for line in lines if line.startswith("DIFFER")]
    print(
        f"{len(lines)} artefact(s) built twice: {len(lines) - len(moved)} "
        f"byte-identical, {len(moved)} not.",
        file=out,
    )
    return 1 if moved else 0
