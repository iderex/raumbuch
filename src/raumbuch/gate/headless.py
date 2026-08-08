"""The leg named ``headless``: this environment has no display and no privilege.

A suite that needs a desktop session is a suite that runs on the machine of
whoever wrote it. Nothing in this project obviously needs a display, which is
exactly why the rule is enforced now: the first helper that quietly opens a
plotting window will do it where nobody reads, and by then the suite will not
run in a container any more.

The leg judges the environment it is in, and it does that by asking rather than
by assuming. Two fixtures in ``tests/`` do the asking: one opens a display, one
asks to become the superuser. Where either succeeds, the environment is not the
one the contract describes and the leg refuses. Where both are refused, the leg
has run the failure it is guarding against and watched it fail.

Where the environment is not the one the contract is about, the leg does not run
and says so. Locally that is the common case, and a local run that silently
omitted the check and reported green is the failure this reporting exists
against.

Hardware-bound work is a separate matter and not this leg's. The classification
runs that need very large memory belong to the seventh milestone, they do not
run in the main suite, and a green run here is never a report that they ran.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from raumbuch import gate

DISPLAY_VARIABLES = ("DISPLAY", "WAYLAND_DISPLAY")
DISPLAY_FIXTURE = Path("tests/contract_display.py")
ELEVATION_FIXTURE = Path("tests/contract_elevation.py")
NOT_ASKED = 2
CANNOT_ASK = 3


def display_variables_set() -> list[str]:
    return [name for name in DISPLAY_VARIABLES if os.environ.get(name)]


def privileged() -> bool:
    """True where this process is already the superuser.

    Only POSIX answers this. On anything else the leg does not run at all, so
    there is no second answer to give here.
    """
    return hasattr(os, "geteuid") and os.geteuid() == 0


def ask(root: Path, fixture: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / fixture)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def elsewhere() -> gate.Verdict | None:
    """The verdict for an environment this contract is not about, or nothing.

    Asking here is what has to be avoided rather than what has to be reported: a
    window or a consent dialog belongs to whoever is sitting at the machine, and
    a proof that interrupts them is a proof nobody keeps running.
    """
    if os.name != "posix":
        return gate.skipped(
            "not run: this contract is about an environment with no display and "
            "no privilege, and asking for either here would raise a window or a "
            f"consent dialog on {os.name}. Running it costs the container the "
            "check runs in, where both requests are refused rather than granted"
        )
    attached = display_variables_set()
    if attached:
        return gate.skipped(
            "not run: a display is attached to this environment "
            f"({', '.join(attached)} is set), so opening one proves nothing "
            "about a contract that is about an environment with none. Running "
            "it costs the container the check runs in"
        )
    return None


def unready(root: Path) -> gate.Verdict | None:
    """The verdict for an environment that cannot carry the proof, or nothing."""
    if privileged():
        return gate.refused(
            "this process is the superuser, so the suite is not running "
            "unprivileged and nothing here could refuse a request for elevation"
        )
    missing = [
        f for f in (DISPLAY_FIXTURE, ELEVATION_FIXTURE) if not (root / f).is_file()
    ]
    if missing:
        return gate.refused(
            "the fixtures that prove this contract are not in the tree: "
            + ", ".join(f.as_posix() for f in missing)
        )
    return None


def run(root: Path) -> gate.Verdict:
    verdict = elsewhere() or unready(root)
    if verdict is not None:
        return verdict

    display = ask(root, DISPLAY_FIXTURE)
    if display.returncode == 0:
        return gate.refused(
            f"{DISPLAY_FIXTURE.as_posix()} opened a display in an environment "
            "declared to have none, so nothing here would refuse a test that "
            "opens one"
        )
    if display.returncode == CANNOT_ASK:
        return gate.skipped(
            f"not run: {DISPLAY_FIXTURE.as_posix()} had no toolkit to ask with, "
            "so nothing was refused and the proof was not made. A missing "
            "toolkit read as a missing display is a check that passes "
            "everywhere. Running it costs an environment carrying the toolkit, "
            "which is the image the check runs in, and the job that has to "
            "cover this leg requires it rather than accepting this line"
        )

    elevation = ask(root, ELEVATION_FIXTURE)
    if elevation.returncode == 0:
        return gate.refused(
            f"{ELEVATION_FIXTURE.as_posix()} was granted elevation, so this "
            "process is not unprivileged and nothing here would refuse a test "
            "that asks for it"
        )
    if elevation.returncode == NOT_ASKED:
        return gate.refused(
            "the elevation fixture declined to ask, which it does only off "
            "POSIX, and this leg has already established that it is on POSIX. "
            "The two disagree, so this leg fails closed"
        )

    return gate.passed(
        "no display variable is set, this process is not the superuser, and "
        "both fixtures were refused: a display could not be opened and "
        "elevation was not granted"
    )
