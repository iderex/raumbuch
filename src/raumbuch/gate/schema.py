"""The leg named ``schema``: every record in the tree is the shape ``schema/`` says.

The published schema is what a consumer downloads and validates against, so a
schema nothing in this repository applies is a promise about records this
repository never checked. This leg applies it, to every record under
``catalogue/`` rather than to a sample, and prints the count it loaded.

**The version selects the schema, and never the other way round.** Record 0003
makes a second format a second file, so this reads ``schema_version`` out of the
record and looks for ``schema/record-<version>.schema.json``. Validating every
record against whichever schema is newest is invisible until the second version
exists and then invalidates the whole catalogue at once. A record naming a
version this tree carries no schema for is refused, with the version it found
and the versions there are.

**What this leg passes is a shape, and it is narrower than a valid record.** A
schema sees one document and sees no other file, so the id matching the filename
stem, two records sharing an id, an undeclared identifier inside an expression, a
duplicate or transposed metric component, and a stratum or chart named by a value
and not declared are all outside what it can decide. Those are the loader and the
``index`` leg, and this leg's report says which of the three ran rather than
reporting one and meaning three.

The schema is also knowingly weaker than records 0005 and 0006 in the four places
`docs/record-format.md` lists, which issue #107 settled in the documents and not
in the file. So a green run here does not mean a record is complete.

The validator comes from the lockfile, and a leg whose tool is absent reports
that it did not run and what running it costs, which is the accounting every
other leg gives. It does not pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tomllib
from pathlib import Path

from raumbuch import catalogue, gate

TOOL = "jsonschema"
INSTALL = 'python3 -m pip install -e ".[schema]"'

DIRECTORY = Path("schema")

#: ``schema/record-<version>.schema.json``. The version in the name and the
#: ``const`` inside the file are the same fact, and this leg reads the name.
PREFIX = "record-"
SUFFIX = ".schema.json"

#: A record naming no ``schema_version`` at all cannot select a schema, so it is
#: refused here as well as by the loader. This is the one field this leg has to
#: read before it can decide which rules to read it under.
VERSION = "schema_version"

SHOWN = 20


def installed() -> bool:
    return importlib.util.find_spec(TOOL) is not None


def available(directory: Path) -> dict[str, Path]:
    """Every schema version this tree carries, by the version in its filename."""
    found = {}
    for path in sorted(directory.glob(f"{PREFIX}*{SUFFIX}")):
        found[path.name[len(PREFIX) : -len(SUFFIX)]] = path
    return found


def declared(data: bytes) -> str | None:
    """The ``schema_version`` of a record, or nothing where it has none."""
    try:
        document = tomllib.loads(data.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None
    version = document.get(VERSION)
    return version if isinstance(version, str) else None


def faults(root: Path, schemas: dict[str, Path]) -> tuple[list[str], int]:
    """Every record that is not the shape its declared version fixes, and the count.

    The whole set is judged rather than the first failure, because a run that
    stopped at the first record would report one fault where a change broke
    forty, and the count is the whole point of the leg reporting what it read.
    """
    from jsonschema import Draft202012Validator

    validators = {
        version: Draft202012Validator(json.loads(path.read_text(encoding="utf-8")))
        for version, path in schemas.items()
    }
    found: list[str] = []
    directory = root / catalogue.DIRECTORY
    paths = sorted(directory.rglob(f"*{catalogue.SUFFIX}"))
    for path in paths:
        name = path.relative_to(directory).as_posix()
        data = path.read_bytes()
        version = declared(data)
        if version is None:
            found.append(
                f"{name} declares no {VERSION}, so nothing says which of "
                f"{', '.join(sorted(validators))} to read it under"
            )
            continue
        if version not in validators:
            found.append(
                f"{name} declares {VERSION} {version!r} and this tree carries "
                f"{DIRECTORY.as_posix()}/ for "
                f"{', '.join(repr(known) for known in sorted(validators))}"
            )
            continue
        document = tomllib.loads(data.decode("utf-8"))
        for error in sorted(
            validators[version].iter_errors(document), key=lambda one: one.json_path
        ):
            found.append(f"{name}: {error.json_path}: {error.message}")
    return found, len(paths)


def run(root: Path) -> gate.Verdict:
    if not installed():
        return gate.skipped(
            f"not run: {TOOL} is not installed for {sys.executable}, so nothing "
            "applies the published schema to this tree. Running it costs "
            f"installing the schema extra, {INSTALL}"
        )
    directory = root / DIRECTORY
    schemas = available(directory) if directory.is_dir() else {}
    if not schemas:
        return gate.refused(
            f"{DIRECTORY.as_posix()}/ carries no {PREFIX}<version>{SUFFIX}, so "
            "this leg fails closed rather than reading an absent schema as a "
            "tree of records nothing is wrong with"
        )
    found, counted = faults(root, schemas)
    if found:
        rest = len(found) - SHOWN
        shown = found[:SHOWN]
        if rest > 0:
            shown.append(f"and {rest} more")
        return gate.refused(
            f"{len(found)} fault(s) against {DIRECTORY.as_posix()}/ across "
            f"{counted} record(s) under {catalogue.DIRECTORY.as_posix()}/\n"
            + "\n".join(shown)
        )
    return gate.passed(
        f"{counted} record(s) under {catalogue.DIRECTORY.as_posix()}/ are the "
        f"shape {DIRECTORY.as_posix()}/ fixes for the version each declares, "
        f"out of {len(schemas)} version(s) this tree carries: "
        f"{', '.join(sorted(schemas))}. A shape is not a whole record: what a "
        "schema cannot see is the loader's and the index leg's"
    )
