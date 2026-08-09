"""The fuzz harness over the two components that read input from outside.

A catalogue is a thing people download and a record is a thing people write by
hand and get wrong in creative ways, so the record loader and the expression
parser are the two surfaces where the input is not this project's. This module
generates input for both and judges four properties over every one of them.

The name does not begin with `test`, so neither `unittest discover` nor pytest
collects it, the same exclusion the contract fixtures rely on. `test_fuzz.py`
runs it, and so does the scheduled workflow, with a much larger budget.

Why a generator written here rather than a coverage-guided engine. Every
distribution this repository installs is pinned to the hash of every file it
publishes and the suite reaches no network, so a fuzzing engine is a dependency
argued for and locked rather than one that arrives with a harness. What that
would buy is coverage feedback; what it costs here is a distribution, a build
for the pinned interpreter and a second thing that decides which inputs run.
This generator instead mutates a seed corpus that already exists and that is
already the good one: the refusal fixtures and the near misses beside them, in
`corpus.py`, are inputs written to sit one character from a boundary. Every run
is seeded and its inputs are reproducible from the seed alone, which is what
turns a crasher into a fixture rather than into an anecdote.

The four properties, and what each one is looking for.

`nothing-crashes` runs each input through a component and admits two outcomes: a
value, or a `refusal.Refused` naming a reason from the closed vocabulary. Any
other exception is a crasher. This is the property that found every entry in
`CRASHERS` below.

`grammar-containment` walks what the parser built and checks that it is made of
the declared node kinds, that every applied function is one of the declared
ones, and that every exponent is a whole number. The parser accepting something
outside its own grammar is how a record smuggles in a construct no reader of
`docs/expression-language.md` would expect to be there.

`nothing-executes` loads records under an audit hook and fails on any event that
would mean the process ran, opened or fetched something. It is the property the
loader's own docstring asserts, and asserting it is not the same as watching it.
The hook stays installed once it is added, so this target runs in this program
rather than inside a suite that has other things to judge afterwards.

`memory-is-bounded` counts the nodes the parser built and requires no more of
them than the input had characters. Every node consumes at least one token and
every token at least one character, so the bound is exact rather than a
threshold somebody tuned, and an input that made the tree grow faster than the
text is the shape that turns a download into an out-of-memory kill.
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import random
import sys

import corpus

from raumbuch import expression, record, refusal

#: Audit events that would mean something ran, was opened, or was fetched. The
#: list is the events a loader could plausibly reach; an event outside it is not
#: watched here, which is the bound on what this target proves.
FORBIDDEN_EVENTS: frozenset[str] = frozenset(
    {
        "builtins.input",
        "compile",
        "exec",
        "import",
        "open",
        "os.system",
        "socket.connect",
        "socket.getaddrinfo",
        "subprocess.Popen",
    }
)

#: Expression seeds. Every one is a shape the language admits, taken from the
#: worked record and from the boundaries of the grammar, because a mutation of
#: something valid lands near the boundary far more often than a random string.
EXPRESSION_SEEDS: tuple[str, ...] = (
    "-(1 - 2*M/r)",
    "1/(1 - 2*M/r)",
    "r^2",
    "r^2*sin(theta)^2",
    "exp(2*a)*cosh(t)",
    "log(r/M) + tan(theta)",
    "-1",
    "pi",
    "cot(theta)/coth(u) + tanh(v)",
    "x^(-3)",
    "sin(cos(exp(log(r))))",
)

#: Condition seeds, for the fields of the sub-language that carry a relation.
CONDITION_SEEDS: tuple[str, ...] = (
    "M > 0",
    "r > 2*M",
    "theta > 0 and theta < pi",
    "phi >= 0",
    "a^2 <= M^2",
    "1 = 1",
    "M != 0",
)

#: The alphabet mutations insert from. It holds the characters of the language
#: and the ones just outside it, because a mutation that can only produce legal
#: text never reaches a refusal and one that can only produce illegal text never
#: reaches the parser's interior.
ALPHABET = "0123456789+-*/^()<>=! andMrtxpiseoglc.,;'\"\\\n\t{}[]:#_"


@dataclasses.dataclass(frozen=True)
class Crasher:
    """An input that once escaped as something other than a refusal.

    ``encoded`` is base64 for the reason `corpus.py` gives: the bytes of a
    fixture are the fixture, and a raw literal in a tracked text file is
    whatever normalisation the clone applied to it.
    """

    encoded: str
    kind: str
    reason: str
    note: str

    def text(self) -> str:
        return base64.b64decode(self.encoded).decode("utf-8")

    def data(self) -> bytes:
        return base64.b64decode(self.encoded)


def _record_around(body: bytes) -> str:
    head = (
        b'schema_version = "1"\nid = "a"\nversion = 1\nname = "n"\n'
        b'dimension = 4\nsignature = "s"\ncoverage_argument = "c"\n'
    )
    tail = (
        b'[[stratum]]\nname = "generic"\ngeneric = true\ncondition = "1 = 1"\n'
        b'[matter]\n[provenance]\nsource_kind = "primary"\n'
    )
    return base64.b64encode(head + body + tail).decode("ascii")


#: Every crasher this harness has found, kept as the input that produced it.
#: Each one is now a refusal naming a reason, and the test beside this module
#: asks for that reason rather than only for the absence of a traceback: a
#: crasher repaired into a different crash would otherwise read as fixed.
CRASHERS: dict[str, Crasher] = {
    "brackets-nested-past-the-stack": Crasher(
        encoded=base64.b64encode(
            b"(" * 400 + b"1" + b")" * 400,
        ).decode("ascii"),
        kind="expression",
        reason=refusal.EXPRESSION_TOO_DEEP,
        note=(
            "The descent is recursive and nothing bounded it, so the "
            "interpreter's stack decided. Four hundred is not the boundary: "
            "the first depth that reached it was under two hundred, because "
            "one level of brackets costs several frames."
        ),
    ),
    "calls-nested-past-the-stack": Crasher(
        encoded=base64.b64encode(
            b"sin(" * 300 + b"x" + b")" * 300,
        ).decode("ascii"),
        kind="expression",
        reason=refusal.EXPRESSION_TOO_DEEP,
        note=(
            "The near miss of the entry above and a different route into the "
            "same descent: a call re-enters the expression production without "
            "a bracket token of its own."
        ),
    ),
    "an-exponent-nested-past-the-stack": Crasher(
        encoded=base64.b64encode(
            b"x^" + b"(" * 400 + b"2" + b")" * 400,
        ).decode("ascii"),
        kind="expression",
        reason=refusal.EXPRESSION_TOO_DEEP,
        note=(
            "The third route, and the one a bound on the expression production "
            "alone would have missed: a bracketed exponent recurses inside the "
            "exponent production and reaches no expression at all."
        ),
    ),
    "an-integer-longer-than-the-interpreter-converts": Crasher(
        encoded=base64.b64encode(b"1" * 5000).decode("ascii"),
        kind="expression",
        reason=refusal.NUMBER_TOO_LONG,
        note=(
            "The interpreter refuses its own string-to-integer conversion "
            "above a digit limit, and it arrives as a ValueError about digit "
            "limits rather than about a record."
        ),
    ),
    "an-exponent-longer-than-the-interpreter-converts": Crasher(
        encoded=base64.b64encode(b"x^" + b"9" * 5000).decode("ascii"),
        kind="expression",
        reason=refusal.NUMBER_TOO_LONG,
        note=(
            "The same conversion, reached through the exponent production, "
            "which reads its digits itself rather than through the atom."
        ),
    ),
    "a-sum-longer-than-the-walker-recurses": Crasher(
        encoded=base64.b64encode(b"1" + b"+1" * 20000).decode("ascii"),
        kind="condition-scope",
        reason="",
        note=(
            "Accepted by the parser and fatal afterwards. The sum is one level "
            "deep to the descent and as deep as it is long to anything walking "
            "the tree the descent built, so the nesting bound does not reach "
            "it and the walker had to stop recursing. This entry carries no "
            "reason: the input is legal and the repair is that reading it "
            "returns rather than that it is refused."
        ),
    ),
    "a-claimed-entry-that-is-not-a-table": Crasher(
        encoded=_record_around(b'claimed = ["x"]\n'),
        kind="record",
        reason=refusal.FIELD_OF_THE_WRONG_KIND,
        note=(
            "The claimed, derived and verification blocks are carried rather "
            "than read, so the first thing to touch an entry asks it for a "
            "key, and a string has none."
        ),
    ),
    "a-derived-entry-that-is-not-a-table": Crasher(
        encoded=_record_around(b"derived = [1]\n"),
        kind="record",
        reason=refusal.FIELD_OF_THE_WRONG_KIND,
        note="The same shape in the second of the three blocks.",
    ),
    "a-verification-entry-that-is-not-a-table": Crasher(
        encoded=_record_around(b"verification = [[]]\n"),
        kind="record",
        reason=refusal.FIELD_OF_THE_WRONG_KIND,
        note="The third block, and a list rather than a string.",
    ),
}


def seeds() -> list[tuple[str, bytes]]:
    """Every starting input, as a kind and the bytes of it.

    The record seeds are the fixture corpus, which is the cheapest good corpus
    available and is already in the tree: one refused record per reason, and
    beside each one the near miss it is one character from.
    """
    found: list[tuple[str, bytes]] = [("record", base64.b64decode(corpus.BASELINE))]
    for fixture in corpus.FIXTURES.values():
        found.append(("record", fixture.refused_bytes()))
        found.append(("record", fixture.accepted_bytes()))
    found.extend(("expression", text.encode("utf-8")) for text in EXPRESSION_SEEDS)
    found.extend(("condition", text.encode("utf-8")) for text in CONDITION_SEEDS)
    return found


def _inserted(source: random.Random, text: str, at: int) -> str:
    return text[:at] + source.choice(ALPHABET) + text[at:]


def _deleted(source: random.Random, text: str, at: int) -> str:
    return text[:at] + text[at + 1 :]


def _replaced(source: random.Random, text: str, at: int) -> str:
    return text[:at] + source.choice(ALPHABET) + text[at + 1 :]


def _repeated(source: random.Random, text: str, at: int) -> str:
    """A slice, written again a number of times.

    This is the mutation that matters and it is why the generator is not a byte
    flipper alone. Every crasher the harness found by itself is a legal
    fragment repeated until something ran out, and no single-character edit of
    a seed reaches one.
    """
    end = source.randrange(at, len(text)) + 1
    return text[:at] + text[at:end] * source.randrange(2, 200) + text[end:]


def _cut(source: random.Random, text: str, at: int) -> str:
    return text[:at] + text[source.randrange(at, len(text)) + 1 :]


def _rotated(source: random.Random, text: str, at: int) -> str:
    return text[at:] + text[:at]


MUTATIONS = (_inserted, _deleted, _replaced, _repeated, _cut, _rotated)


def mutate(source: random.Random, data: bytes) -> bytes:
    """One mutation of ``data``, chosen by ``source``."""
    if not data:
        return ALPHABET.encode("utf-8")
    text = data.decode("utf-8", errors="replace")
    at = source.randrange(len(text))
    return MUTATIONS[source.randrange(len(MUTATIONS))](source, text, at).encode("utf-8")


#: A mutant longer than this is used and not kept. Without a ceiling the pool
#: drifts towards its longest member and a run spends its whole budget on one
#: enormous input; without a pool at all nothing compounds. Both were measured.
KEPT = 20000


def inputs(seed: int, rounds: int) -> list[tuple[str, bytes]]:
    """The inputs of one run, derived from the seed and from nothing else.

    Same seed, same list, on any machine: a crasher is then a seed and an index
    rather than a thing somebody saw once.

    A mutant goes back into the pool the next one is drawn from. That is what
    makes a repetition compound, and compounding is how the generator reaches a
    nesting depth or a digit count no single edit of a seed produces.
    """
    source = random.Random(seed)
    pool = seeds()
    produced = list(pool)
    for _ in range(rounds):
        kind, data = pool[source.randrange(len(pool))]
        mutant = (kind, mutate(source, data))
        produced.append(mutant)
        if len(mutant[1]) <= KEPT:
            pool.append(mutant)
    return produced


def read(kind: str, data: bytes) -> object:
    """Run one input through the component its kind names."""
    if kind == "record":
        return record.loads(data, "a")
    text = data.decode("utf-8", errors="replace")
    if kind == "condition":
        return expression.parse_condition(text)
    if kind == "condition-scope":
        # The parse and the walk over what it produced. The loader always does
        # both, and the second is where a tree the first accepted goes wrong.
        node = expression.parse(text)
        expression.names(node)
        expression.functions(node)
        return node
    return expression.parse(text)


@dataclasses.dataclass
class Report:
    """What one target found, and over how many inputs."""

    target: str
    examined: int
    failures: list[str] = dataclasses.field(default_factory=list)

    def line(self) -> str:
        state = "clean" if not self.failures else f"{len(self.failures)} failure(s)"
        return f"{self.target}: {self.examined} input(s), {state}"


def _describe(kind: str, data: bytes) -> str:
    return f"{kind} {base64.b64encode(data).decode('ascii')[:120]}"


def nothing_crashes(cases: list[tuple[str, bytes]]) -> Report:
    report = Report("nothing-crashes", len(cases))
    for kind, data in cases:
        try:
            read(kind, data)
        except refusal.Refused as refused:
            if refused.reason not in refusal.REASONS:
                report.failures.append(
                    f"a reason outside the vocabulary, {refused.reason!r}, on "
                    + _describe(kind, data)
                )
        except BaseException as error:
            report.failures.append(
                f"{type(error).__name__} on " + _describe(kind, data)
            )
    return report


def grammar_containment(cases: list[tuple[str, bytes]]) -> Report:
    """What the parser accepted is made of the declared parts and nothing else."""
    kinds = (
        expression.Number,
        expression.Name,
        expression.Apply,
        expression.Negate,
        expression.Operation,
        expression.Power,
        expression.Comparison,
        expression.Conjunction,
    )
    report = Report("grammar-containment", 0)
    for kind, data in cases:
        if kind == "record":
            continue
        try:
            tree = read(kind, data)
        except refusal.Refused:
            continue
        except BaseException:
            continue
        report.examined += 1
        for node in expression.walk(tree):
            where = _describe(kind, data)
            if not isinstance(node, kinds):
                report.failures.append(f"{type(node).__name__} in a tree from {where}")
            if isinstance(node, expression.Apply) and node.function not in (
                expression.FUNCTIONS
            ):
                report.failures.append(f"{node.function!r} applied in {where}")
            if isinstance(node, expression.Power) and not isinstance(
                node.exponent, int
            ):
                report.failures.append(f"a non-integer exponent in {where}")
            if isinstance(node, expression.Operation) and node.operator not in "+-*/":
                report.failures.append(f"{node.operator!r} as an operator in {where}")
            if isinstance(node, expression.Comparison) and (
                node.relation not in expression.COMPARISONS
            ):
                report.failures.append(f"{node.relation!r} as a relation in {where}")
    return report


def memory_is_bounded(cases: list[tuple[str, bytes]]) -> Report:
    """No tree holds more nodes than its text held characters."""
    report = Report("memory-is-bounded", 0)
    for kind, data in cases:
        if kind == "record":
            continue
        try:
            tree = read(kind, data)
        except refusal.Refused:
            continue
        except BaseException:
            continue
        report.examined += 1
        text = data.decode("utf-8", errors="replace")
        built = len(expression.walk(tree))
        if built > len(text):
            report.failures.append(
                f"{built} node(s) out of {len(text)} character(s) in "
                + _describe(kind, data)
            )
    return report


def nothing_executes(cases: list[tuple[str, bytes]]) -> Report:
    """No input makes a component run, open or fetch anything.

    The hook is installed here and cannot be taken off again, which is why this
    program is what runs this target and a unit suite is not.
    """
    seen: list[str] = []
    watching = [False]

    def hook(event: str, arguments: object) -> None:
        if watching[0] and event in FORBIDDEN_EVENTS:
            seen.append(event)

    sys.addaudithook(hook)
    report = Report("nothing-executes", len(cases))
    for kind, data in cases:
        seen.clear()
        watching[0] = True
        try:
            read(kind, data)
        except refusal.Refused:
            pass
        except BaseException:
            pass
        finally:
            watching[0] = False
        if seen:
            report.failures.append(
                f"{', '.join(sorted(set(seen)))} during " + _describe(kind, data)
            )
    return report


TARGETS = {
    "nothing-crashes": nothing_crashes,
    "grammar-containment": grammar_containment,
    "memory-is-bounded": memory_is_bounded,
    "nothing-executes": nothing_executes,
}


def campaign(seed: int, rounds: int, only: str | None = None) -> list[Report]:
    cases = inputs(seed, rounds)
    chosen = TARGETS if only is None else {only: TARGETS[only]}
    return [target(cases) for target in chosen.values()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--rounds", type=int, default=2000)
    parser.add_argument("--only", choices=sorted(TARGETS), default=None)
    arguments = parser.parse_args(argv)
    reports = campaign(arguments.seed, arguments.rounds, arguments.only)
    print(f"seed {arguments.seed}, {arguments.rounds} mutation(s) beyond the corpus")
    for report in reports:
        print(report.line())
        for failure in report.failures:
            print(f"  {failure}")
    return 1 if any(report.failures for report in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
