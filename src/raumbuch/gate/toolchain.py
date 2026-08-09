"""The leg named ``pin``: one version of anything, in one file, read by the rest.

A catalogue that has to reproduce a classification in five years cannot be built
by whatever version of the toolchain the runner happened to have that week.
Record 0006 sharpens that: a stored derived value is anchored to a digest over
the source that produced it, and an anchor is worth something only where the
thing it anchors can be brought back. So the pin is not only a supply-chain
control here, it is what makes a staleness anchor mean anything.

Two files hold the versions. ``.python-version`` holds the interpreter, which is
a runtime rather than a distribution to install. ``requirements.lock`` holds
every distribution, pinned to one version and to the hash of every file that
version publishes.

What this leg refuses, and each of the three is a different way the pin stops
being a pin.

A version literal in a workflow. The pin means nothing where a second copy of it
exists, and a workflow is where the second copy goes. The one shape allowed is
the ``# vX.Y.Z`` comment after an action's forty character commit hash, which is
the pinning convention's own readability and is not a version of anything this
file pins.

A lockfile that disagrees with the manifest. A name ``pyproject.toml`` declares
and the lock does not is a dependency that arrives unpinned; a name the lock
carries and the manifest does not is a pin for something nothing installs.

A locked distribution with no hash, or a lock pinned by anything other than
``==``. A version without a hash is a name resolved at install time, which is
the thing the file exists to stop.

What it does not judge is whether the pinned version is the right one, and
whether a workflow installs from the lock at all. The first is a judgement; the
second is readable and is written up in ``docs/checks.md`` as a gap rather than
folded into a sentence about the pin holding.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from raumbuch import gate

INTERPRETER = Path(".python-version")
LOCK = Path("requirements.lock")
MANIFEST = Path("pyproject.toml")
WORKFLOWS = Path(".github/workflows")

# Three parts, which is what a pinned version of anything here looks like. Two
# parts would reach a standard's identifier in a comment and the year in a
# licence line, neither of which is a version this file pins.
VERSION = re.compile(r"\b\d+\.\d+\.\d+\b")

# The one shape a version literal may take in a workflow: the readability
# comment after an action pinned to a full commit hash. The hash is the pin and
# the comment is what makes it legible, so removing it would cost the reader the
# thing the other half of this issue is about.
PIN_COMMENT = re.compile(r"@[0-9a-f]{40}\s*#\s*v?\d+\.\d+(\.\d+)?\s*$")

# `name==version`, which is the only form the lock admits. A range is a
# resolution deferred to install time.
LOCKED = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)")
HASH = re.compile(r"--hash=sha256:[0-9a-f]{64}")

# A requirement in the manifest is a name and possibly a marker or an extra.
# Only the name is compared, because which version arrives is the lock's answer.
NAMED = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)")


def normalised(name: str) -> str:
    """The name a package index resolves, so `Ruff` and `ruff_` are one name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def declared(manifest: str) -> set[str]:
    """Every distribution ``pyproject.toml`` says this project installs.

    The build requirement is in the set. It is installed to build the package
    and an unpinned build backend is as much a supply-chain surface as a runtime
    dependency, and a less visible one.
    """
    data = tomllib.loads(manifest)
    wanted: list[str] = list(data.get("build-system", {}).get("requires", []))
    project = data.get("project", {})
    wanted += list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        wanted += list(group)
    found = set()
    for requirement in wanted:
        name = NAMED.match(requirement.strip())
        if name:
            found.add(normalised(name.group(1)))
    return found


def locked(lock: str) -> dict[str, tuple[str, int]]:
    """Every distribution the lock pins, with its version and how many hashes.

    A lock entry runs over several lines, one hash to a line, so the count is
    accumulated onto the name the entry opened with.
    """
    found: dict[str, tuple[str, int]] = {}
    current: str | None = None
    for line in lock.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        opened = LOCKED.match(stripped)
        if opened:
            current = normalised(opened.group(1))
            found[current] = (opened.group(2).rstrip(" \\"), len(HASH.findall(line)))
            continue
        if current is not None:
            version, count = found[current]
            found[current] = (version, count + len(HASH.findall(line)))
    return found


def unpinned(lock: str) -> list[str]:
    """Every line of the lock that names a requirement in some other form."""
    loose = []
    for line in lock.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped or stripped.startswith("--hash="):
            continue
        if not LOCKED.match(stripped):
            loose.append(stripped)
    return loose


def literals(directory: Path) -> list[str]:
    """Every version literal in a workflow that is not an action's pin comment."""
    found = []
    for path in sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml")):
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if PIN_COMMENT.search(line):
                continue
            for version in VERSION.findall(line):
                found.append(f"{path.name}:{number}: {version} in {line.strip()}")
    return found


def judge(root: Path) -> list[str]:
    """Every way the pin is not a pin, as a list rather than a first find."""
    faults = []
    interpreter = root / INTERPRETER
    if not interpreter.is_file():
        faults.append(
            f"{INTERPRETER.as_posix()} is where the interpreter version is held "
            "and it is not in this tree"
        )
    else:
        said = interpreter.read_text(encoding="utf-8").strip()
        if not VERSION.fullmatch(said):
            faults.append(
                f"{INTERPRETER.as_posix()} holds {said!r}, and an interpreter "
                "pinned to anything but one X.Y.Z version is a version chosen "
                "by whatever is installed"
            )

    lock_file = root / LOCK
    manifest_file = root / MANIFEST
    if not lock_file.is_file() or not manifest_file.is_file():
        for path in (LOCK, MANIFEST):
            if not (root / path).is_file():
                faults.append(f"{path.as_posix()} is not in this tree")
        return faults + literals(root / WORKFLOWS)

    lock = lock_file.read_text(encoding="utf-8")
    pinned = locked(lock)
    for line in unpinned(lock):
        faults.append(
            f"{LOCK.as_posix()}: {line!r} pins nothing: a lock admits name==version "
            "and a range is a resolution deferred to install time"
        )
    for name, (version, hashes) in sorted(pinned.items()):
        if hashes == 0:
            faults.append(
                f"{LOCK.as_posix()}: {name}=={version} carries no hash, so what "
                "arrives is whatever the index serves under that name"
            )

    wanted = declared(manifest_file.read_text(encoding="utf-8"))
    for name in sorted(wanted - set(pinned)):
        faults.append(
            f"{name} is declared in {MANIFEST.as_posix()} and not pinned in "
            f"{LOCK.as_posix()}, so it arrives unpinned"
        )
    for name in sorted(set(pinned) - wanted):
        faults.append(
            f"{name} is pinned in {LOCK.as_posix()} and declared nowhere in "
            f"{MANIFEST.as_posix()}, so it is a pin for something nothing installs"
        )

    return faults + [
        f"{WORKFLOWS.as_posix()}/{found}, and a version literal in a workflow is "
        "the second copy this pin exists to prevent"
        for found in literals(root / WORKFLOWS)
    ]


def run(root: Path) -> gate.Verdict:
    if not (root / WORKFLOWS).is_dir():
        return gate.refused(
            f"{WORKFLOWS.as_posix()}/ is not in this tree, so this leg fails "
            "closed rather than reading an absent set of workflows as a set "
            "naming no version"
        )
    faults = judge(root)
    if faults:
        return gate.refused(
            f"{len(faults)} way(s) the pin is not a pin\n" + "\n".join(faults)
        )
    pinned = locked((root / LOCK).read_text(encoding="utf-8"))
    said = (root / INTERPRETER).read_text(encoding="utf-8").strip()
    total = sum(count for _, count in pinned.values())
    return gate.passed(
        f"CPython {said} in {INTERPRETER.as_posix()}, {len(pinned)} "
        f"distribution(s) pinned to {total} file hash(es) in {LOCK.as_posix()} "
        f"and matching {MANIFEST.as_posix()}, and no version literal in "
        f"{WORKFLOWS.as_posix()}/"
    )
