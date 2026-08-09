"""A fixture that opens a connection. It is proof, and it is not part of the suite.

The name does not begin with `test`, so neither `unittest discover` nor pytest
collects it. That exclusion is by construction rather than by a note in a
document, which is what keeps it out of a run somebody else configures. It also
keeps it out of `unit tests`: this fixture succeeds wherever a route exists, and
a suite carrying it would be red on every developer machine.

What runs it is the `network` leg, which reads a success here as a failure of the
contract: in an environment with outbound access denied, opening a connection has
to be impossible. So the leg is not trusting the denial, it is watching the
denial refuse something.

It is the inverse of the fixture a guard usually carries and that is the point.
A test that opens a socket and passes proves the network is there. This one is
run where the answer must be no, and the leg refuses when the answer is yes.

The target is the package index. Record 0014 already names it as the one
connection this project's life involves, so the fixture reaches for the thing
that is genuinely reachable rather than for a documentation address that would
hang and be read as a denial. Both halves of reaching it are tried, because they
fail at different layers and a denial that stopped only one of them would be a
denial with a hole in it: a name is resolved, and then a connection is opened to
a literal address so that a resolver answering from a cache proves nothing.

Run alone, it exits zero where anything got out and one where nothing did.
"""

from __future__ import annotations

import socket
import sys

# The package index, which record 0014 names as the connection an install makes.
NAME = "pypi.org"
PORT = 443

# A literal address, so that the second attempt needs no resolver at all. This
# is one of the public resolvers, reached on the port a resolver answers on.
ADDRESS = "1.1.1.1"
RESOLVER_PORT = 53

# Short, because this fixture is run where the answer is expected immediately.
# A denial at the routing layer fails before this matters; the timeout is here
# so that a filtered route ends the fixture rather than the job's own clock.
TIMEOUT = 5


def resolved() -> str | None:
    """The address a name resolves to, or nothing where it did not resolve."""
    try:
        return socket.getaddrinfo(NAME, PORT, type=socket.SOCK_STREAM)[0][4][0]
    except OSError:
        return None


def connected(host: str, port: int) -> bool:
    """True where a connection to an address was opened."""
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return True
    except OSError:
        return False


if __name__ == "__main__":
    address = resolved()
    if address is not None:
        print(f"{NAME} resolved to {address}", file=sys.stderr)
    if address is not None and connected(address, PORT):
        print(f"a connection to {NAME} was opened", file=sys.stderr)
        sys.exit(0)
    if connected(ADDRESS, RESOLVER_PORT):
        print(f"a connection to {ADDRESS} was opened", file=sys.stderr)
        sys.exit(0)
    print("nothing got out of this environment", file=sys.stderr)
    sys.exit(1)
