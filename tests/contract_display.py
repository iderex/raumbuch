"""A fixture that opens a display. It is proof, and it is not part of the suite.

The name does not begin with `test`, so neither `unittest discover` nor pytest
collects it. That exclusion is by construction rather than by a note in a
document, which is what keeps it out of a run somebody else configures.

What runs it is the `headless` leg, which reads a success here as a failure of
the contract: in an environment with no display attached, opening one has to be
impossible. The leg refuses when this fixture succeeds, so the fixture is the
thing that proves the check bites rather than a demonstration somebody ran once.

Run alone, it exits zero where a display exists and one where none does. Where
the toolkit it opens a window with is not installed at all it exits 3 and asks
nothing, because a missing toolkit and a missing display are different facts and
reading the first as the second would turn this proof into a formality.
"""

from __future__ import annotations

import importlib.util
import sys

CANNOT_ASK = 3


def open_a_window() -> None:
    """Open a real window, which is the thing the contract forbids."""
    import tkinter

    root = tkinter.Tk()
    root.update()
    root.destroy()


if __name__ == "__main__":
    if importlib.util.find_spec("tkinter") is None:
        print("not asked: there is no toolkit here to ask with", file=sys.stderr)
        sys.exit(CANNOT_ASK)
    open_a_window()
    print("a display was opened", file=sys.stderr)
    sys.exit(0)
