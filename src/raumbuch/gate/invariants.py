"""The leg named ``invariants``: patterns that must never appear, and never do.

The cheapest check on this board, and it does work nothing else does. Three
decision records each say a thing that must not appear in the source, and until
this leg each of them was a sentence in a document. A sentence in a document is
an explanation of a rule; this is where three of them become rules.

Every pattern names the record it comes from. That is the whole design: a
pattern nobody can trace to a decision is a rule somebody added, and a decision
whose rule is not here is prose. What the leg refuses is written beside each
:class:`Pattern` below rather than in a list a reader has to keep in step.

**One file is outside what this leg reads, and it is this one.** The boundary
pattern refuses a name in the source, and the name has to be written here for
the pattern to exist, so the module declaring the patterns matches its own. It
is excluded by construction along with its fixtures, which is an exclusion a
reader can see rather than a list somebody could quietly lengthen. Nothing here
does arithmetic, reaches the network or touches the algebra layer, so what the
exclusion costs is a file whose whole content is these patterns.

**What a text pattern cannot decide, it does not claim.** A record 0003 rule,
that a derived field is never written without its command, commit and date, is
named in issue #93 and is not here: nothing in this tree writes a record, so
there is no site for a pattern to be about, and issue #130 holds whether a
writer is ever built. A pattern with no possible subject would pass on every
tree and read as coverage.
"""

from __future__ import annotations

import dataclasses
import io
import re
import tokenize
from collections.abc import Callable, Iterable
from pathlib import Path

from raumbuch import gate

SOURCE = (Path("src"), Path("tests"))

#: This module and the fixtures that exercise it. The boundary pattern below
#: matches a name that has to be written here for the pattern to exist.
ITSELF = (
    "src/raumbuch/gate/invariants.py",
    "tests/test_gate_invariants.py",
)

SHOWN = 20


@dataclasses.dataclass(frozen=True)
class Pattern:
    """One rule from one record, and where in the tree it is about.

    ``record`` is the decision the rule comes from and is printed with every
    refusal, so a reader meeting one is sent to the argument rather than to
    this file. ``within`` and ``except_in`` are the subject: a rule about the
    loader is not a rule about the harness that proves the loader.
    """

    name: str
    record: str
    refuses: str
    within: tuple[str, ...]
    except_in: tuple[str, ...]
    found: Callable[[str], list[tuple[int, str]]]

    def about(self, path: str) -> bool:
        if any(path == excluded or path.startswith(excluded) for excluded in ITSELF):
            return False
        if any(path == one or path.startswith(one) for one in self.except_in):
            return False
        return any(path == one or path.startswith(one) for one in self.within)


SYMBOLIC = re.compile(r"sympy", re.IGNORECASE)

OUTBOUND = re.compile(
    r"^\s*(?:import|from)\s+"
    r"(socket|ssl|urllib|http|ftplib|smtplib|poplib|imaplib|telnetlib|xmlrpc|"
    r"webbrowser|requests|httpx|urllib3)\b",
    re.MULTILINE,
)


def matching(expression: re.Pattern[str]) -> Callable[[str], list[tuple[int, str]]]:
    """Every line the expression reaches, with its number."""

    def found(text: str) -> list[tuple[int, str]]:
        return [
            (number, line.strip())
            for number, line in enumerate(text.splitlines(), start=1)
            if expression.search(line)
        ]

    return found


def floating(text: str) -> list[tuple[int, str]]:
    """Every floating point number and every route to one, in code.

    Read off the token stream rather than off the text, because a decimal point
    inside a message is prose about arithmetic and not arithmetic. The parser's
    own refusal names ``0.5`` in the sentence that refuses it, and a pattern
    that could not tell those apart would refuse the check that enforces the
    same record.
    """
    found: list[tuple[int, str]] = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # A file that does not tokenise is the `build` leg's refusal, and that
        # leg runs before this one. Reporting it twice, in a vocabulary about
        # floating point, would send a reader to the wrong record.
        return found
    for token in tokens:
        if token.type == tokenize.NUMBER and re.search(
            r"[.]|[eE][-+]?\d", token.string
        ):
            found.append((token.start[0], f"the number {token.string}"))
        if token.type == tokenize.NAME and token.string in ("float", "complex"):
            found.append((token.start[0], f"the name {token.string}"))
    return found


PATTERNS: tuple[Pattern, ...] = (
    # Record 0001: everything record 0009 makes load-bearing sits behind one
    # interface in src/raumbuch/algebra/, and nothing outside that directory
    # constructs a symbolic object or names a symbolic type. The boundary is
    # what makes the means decision revisitable, and a single import somewhere
    # convenient is how a boundary stops being one.
    Pattern(
        name="symbolic-layer-outside-its-boundary",
        record="0001",
        refuses=(
            "the symbolic algebra layer named outside the one directory "
            "that may name it"
        ),
        within=("src/raumbuch",),
        except_in=("src/raumbuch/algebra",),
        found=matching(SYMBOLIC),
    ),
    # Record 0009: floating point does not appear in the classification path at
    # all, not as a filter, not as a pre-test, not as a heuristic ordering. The
    # one place a float is admitted is a cost measurement on a verification
    # entry, which is a measurement of a run and is never branched on, and no
    # such measurement exists in this tree yet.
    Pattern(
        name="floating-point-in-a-decision-path",
        record="0009",
        refuses="a floating point number, or a route to one, in code under src/",
        within=("src/raumbuch",),
        except_in=(),
        found=floating,
    ),
    # Record 0014: the library and the command-line entry point make no network
    # connection, and the test suite makes none either. Two files reach for a
    # socket on purpose and both exist to prove the absence of a route: the
    # `network` leg's probe and the fixture it runs.
    Pattern(
        name="network-outside-the-harness-allowed-one",
        record="0014",
        refuses=(
            "a module that reaches the network, imported outside the harness "
            "that proves there is no route"
        ),
        within=("src/raumbuch", "tests"),
        except_in=("src/raumbuch/gate/network.py", "tests/contract_network.py"),
        found=matching(OUTBOUND),
    ),
)


def sources(root: Path) -> list[str]:
    """Every Python file this leg reads, as a path relative to the root."""
    found: list[str] = []
    for directory in SOURCE:
        for path in sorted((root / directory).rglob("*.py")):
            found.append(path.relative_to(root).as_posix())
    return found


def faults(root: Path, patterns: Iterable[Pattern] = PATTERNS) -> list[str]:
    """Every appearance of every pattern, named with the record it comes from."""
    found: list[str] = []
    paths = sources(root)
    for pattern in patterns:
        for path in paths:
            if not pattern.about(path):
                continue
            text = (root / path).read_text(encoding="utf-8")
            for number, what in pattern.found(text):
                found.append(
                    f"{pattern.name}: {path}:{number}: {what}, and record "
                    f"{pattern.record} refuses {pattern.refuses}"
                )
    return found


def run(root: Path) -> gate.Verdict:
    for directory in SOURCE:
        if not (root / directory).is_dir():
            return gate.refused(
                f"{directory.as_posix()}/ is not in this tree, so this leg fails "
                "closed rather than reading an absent directory as one carrying "
                "no forbidden pattern"
            )
    found = faults(root)
    counted = len(sources(root))
    if found:
        rest = len(found) - SHOWN
        shown = found[:SHOWN]
        if rest > 0:
            shown.append(f"and {rest} more")
        return gate.refused(
            f"{len(found)} appearance(s) of {len(PATTERNS)} forbidden pattern(s) "
            f"across {counted} file(s)\n" + "\n".join(shown)
        )
    return gate.passed(
        f"{len(PATTERNS)} pattern(s) from record(s) "
        f"{', '.join(sorted({pattern.record for pattern in PATTERNS}))} appear "
        f"nowhere in {counted} file(s) under "
        f"{', '.join(directory.as_posix() + '/' for directory in SOURCE)}, "
        f"outside the {len(ITSELF)} file(s) that declare and exercise them"
    )
