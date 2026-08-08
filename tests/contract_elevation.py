"""A fixture that asks for elevation. It is proof, and it is not part of the suite.

The name does not begin with `test`, so nothing collects it, and the `headless`
leg is what runs it. The leg reads a success here as a failure of the contract:
an unprivileged process must not be able to become a privileged one.

This fixture is not symmetric with the display one and the difference is the
reason it is written the way it is. A test that opens a display fails on a
machine with no display, which is the check working. A request for elevation on
a developer's machine is not a failure at all, it is a consent dialog taking the
screen from whoever is sitting in front of it, and a proof that interrupts the
person reading it is a proof nobody keeps running.

So it refuses to ask anywhere except where the answer is no by construction. On
anything other than POSIX it exits 2 without asking for anything, and the leg
reports that it did not run and why. The elevation half of the contract is
therefore proven on a runner and never locally, which is a bound on this check
rather than a gap in it.
"""

from __future__ import annotations

import os
import sys

NOT_ASKED = 2


def ask_for_elevation() -> None:
    """Become the superuser, which is the thing the contract forbids.

    This is the request that fails with a refusal rather than with a prompt: an
    unprivileged process calling it gets `PermissionError` from the kernel, and
    nothing is shown to anybody. Nothing here runs a helper that could raise a
    consent dialog.
    """
    os.setuid(0)


if __name__ == "__main__":
    if os.name != "posix":
        print(
            "not asked: elevation is only requested where the answer is a "
            "refusal rather than a prompt",
            file=sys.stderr,
        )
        sys.exit(NOT_ASKED)
    ask_for_elevation()
    print("elevation was granted", file=sys.stderr)
    sys.exit(0)
