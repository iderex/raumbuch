"""The leg named ``tests``: the unit suite passes, on the tree being judged.

The suite runs in a subprocess out of the checkout the gate was given, with that
checkout's ``src/`` ahead of whatever is installed, so what is judged is the tree
at that root and never a copy of the project that happens to be in the
environment.

It does not run inside itself, and the reason is worth reading before somebody
removes the guard. The suite contains a test that runs the whole gate against
this tree, so a leg that ran the suite unconditionally would run the suite from
inside the suite, and again from inside that one, until the machine stopped. The
subprocess therefore carries a variable saying a gate-run suite is already in
progress, and a leg that sees it reports that it did not run, with what running
it costs, which is the accounting every other leg gives.

That is a bound rather than a trick, and it has a consequence a reader should
have: inside a suite run, the gate's own report says the suite was not judged.
The other consequence is a cost. Running the suite by hand runs it twice, once
directly and once from the whole-gate test inside it, and the second run is where
this leg is exercised. Two is where it stops.

What this leg does not do is choose which tests run. Discovery is the standard
one over ``tests/``, so a file named to be collected is collected and a fixture
named not to be is not, which is the same rule the contract fixtures rely on.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from raumbuch import gate

SUITE = Path("tests")
PACKAGE = Path("src")

# Set on the subprocess this leg starts, and read by the leg. Nothing else reads
# it and nothing else should set it: setting it by hand turns the suite leg off
# for that run, and the report says the leg did not run rather than hiding it.
INSIDE = "RAUMBUCH_GATE_SUITE"

ARGUMENTS = ["-m", "unittest", "discover", "-s"]

# The lines of a unittest run that name something that went wrong. A run with
# five failures prints five of these and then one traceback each, and the names
# are what a reader needs before the tracebacks.
NAMED = re.compile(r"^(FAIL|ERROR): ")
COUNTED = re.compile(r"^Ran (\d+) tests? in ")
SHOWN = 20


def counted(lines: list[str]) -> int | None:
    """How many tests the run reported, or nothing where it never got there."""
    for line in lines:
        found = COUNTED.match(line)
        if found:
            return int(found.group(1))
    return None


def environment(root: Path) -> dict[str, str]:
    variables = dict(os.environ)
    existing = variables.get("PYTHONPATH")
    source_root = str(root / PACKAGE)
    variables["PYTHONPATH"] = (
        f"{source_root}{os.pathsep}{existing}" if existing else source_root
    )
    variables[INSIDE] = "1"
    return variables


def invoke(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *ARGUMENTS, SUITE.as_posix()],
        cwd=root,
        env=environment(root),
        capture_output=True,
        text=True,
        check=False,
    )


def judge(result: subprocess.CompletedProcess[str]) -> gate.Verdict:
    """What a unittest run said, as a verdict.

    This is a function rather than the tail of ``run`` because the suite is run
    by two legs. The ``network`` leg runs the same suite in an environment with
    no route out of it, and a second reading of a runner's output is a second
    thing to keep in step with unittest.
    """
    # unittest writes its report to standard error, and a test that printed
    # something wrote to standard output. Both belong to a reader of a failure.
    lines = [
        line
        for line in f"{result.stderr}\n{result.stdout}".splitlines()
        if line.strip()
    ]
    total = counted(lines)
    if result.returncode == 0:
        if total is None:
            return gate.refused(
                "the suite exited zero without saying how many tests it ran, so "
                "this leg fails closed rather than reading a run that never "
                "started as a suite that passed\n" + "\n".join(lines[-5:])
            )
        return gate.passed(f"{total} test(s) in {SUITE.as_posix()}/ passed")
    named = [line for line in lines if NAMED.match(line)]
    if not named:
        return gate.refused(
            "the suite could not judge this tree, so this leg fails closed "
            f"rather than reading a broken run as a passing one (exit "
            f"{result.returncode})\n" + "\n".join(lines[-5:])
        )
    rest = len(named) - SHOWN
    shown = named[:SHOWN]
    if rest > 0:
        shown.append(f"and {rest} more, which the run prints in full")
    ran = "of an unreported number" if total is None else f"of {total}"
    return gate.refused(f"{len(named)} test(s) {ran} did not pass\n" + "\n".join(shown))


def run(root: Path) -> gate.Verdict:
    if os.environ.get(INSIDE):
        return gate.not_run(
            "not run: this gate run is already inside a suite this leg started, "
            "and a suite that runs itself does not terminate. Running it costs a "
            f"gate run outside one, which is any run where {INSIDE} is unset"
        )
    if not (root / SUITE).is_dir():
        return gate.refused(
            f"{SUITE.as_posix()}/ is not in this tree, so there is no unit suite "
            "here to pass"
        )
    return judge(invoke(root))
