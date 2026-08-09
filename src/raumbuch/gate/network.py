"""The leg named ``network``: the suite runs with nothing to reach, and passes.

Record 0014 says the library and the command-line entry point make no network
connection, and it says which half of that a check can refuse: the test suite.
A code path the suite never reaches can contain a connection the suite never
sees, so a green run here is not evidence that the library makes no connection,
and this module says so rather than leaving the reader to work it out.

The denial is the environment's and never this code's. A flag the suite sets on
itself is read after the interpreter has started, and the call this check exists
to catch is the one inside a dependency at import time, which runs first. So the
leg does not deny anything: it establishes that there is no route out of the
environment it is in, watches a fixture fail to find one, and then runs the
suite there.

Where a route exists, this is not the environment the contract is about and the
leg does not run, with what running it costs. That is the common case on a
workstation, and a local run that quietly omitted the check and reported green
is the failure the reporting exists against. It also means this leg opens no
connection from a machine somebody is sitting at: the route probe below sends
no packet, and the fixture is only ever run once the probe has said there is
nowhere for a packet to go.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
from pathlib import Path

from raumbuch import gate
from raumbuch.gate import suite

FIXTURE = Path("tests/contract_network.py")

# A documentation address, used as a route probe and never as a destination. A
# datagram socket connected to it sends nothing: the call asks the kernel which
# interface would carry a packet there and fails where the answer is none. So
# the probe is silent on a machine with a route and instant on one without.
ELSEWHERE = ("192.0.2.1", 9)


def on_posix() -> bool:
    """True where a network namespace with no interface in it is a thing."""
    return os.name == "posix"


def routable() -> bool:
    """True where this environment has a route out of it, without using one."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(ELSEWHERE)
    except OSError:
        return False
    return True


def ask(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / FIXTURE)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def elsewhere() -> gate.Verdict | None:
    """The verdict for an environment this contract is not about, or nothing."""
    if os.environ.get(suite.INSIDE):
        return gate.not_run(
            "not run: this gate run is already inside a suite a leg started, and "
            "this leg runs the suite, so it would run one from inside another "
            "without terminating. Running it costs a gate run outside one, which "
            f"is any run where {suite.INSIDE} is unset"
        )
    if not on_posix():
        return gate.skipped(
            "not run: the denial this contract is about is a network namespace "
            f"with no interface in it, and {os.name} is not where one is made. "
            "Running it costs the job that denies the network, which is where "
            "this leg is asked for"
        )
    if routable():
        return gate.skipped(
            "not run: a route out of this environment exists, so a suite that "
            "passed here would have passed with the network available and "
            "proved nothing about a contract that is about having none. Running "
            "it costs an environment with outbound access denied, which the "
            "job asking for this leg provides"
        )
    return None


def run(root: Path) -> gate.Verdict:
    verdict = elsewhere()
    if verdict is not None:
        return verdict
    if not (root / FIXTURE).is_file():
        return gate.refused(
            f"the fixture that proves this denial is real is not in the tree at "
            f"{FIXTURE.as_posix()}, so nothing here would notice a denial that "
            "had stopped denying anything"
        )
    attempt = ask(root)
    if attempt.returncode == 0:
        return gate.refused(
            f"{FIXTURE.as_posix()} opened a connection in an environment "
            "declared to have no route out, so the denial is not in force and a "
            "suite passing here would prove nothing\n" + attempt.stderr.strip()
        )
    # No separate check that the suite directory is there. The fixture above
    # lives in it, so a tree carrying the fixture carries the directory, and a
    # branch nothing can reach is a branch no fixture can prove.
    verdict = suite.judge(suite.invoke(root))
    if verdict.state != gate.PASSED:
        return gate.refused(
            "the suite did not pass with outbound access denied, and every "
            "route out of this environment was already refused before it "
            f"started\n{verdict.detail}"
        )
    return gate.passed(
        f"nothing got out of this environment and {verdict.detail}, so no test "
        "in the suite reached for the network. This covers the suite and not "
        "the library, per record 0014"
    )
