"""The gate: one verb, whose legs run in order and stop at the first refusal.

There is one procedure here and not three. The pre-push hook execs this verb and
the workflow runs this verb, so neither carries a second copy of a leg that can
drift from this one.

A run says what it examined. Every declared leg appears in the report with what
became of it: it ran and passed, it ran and refused, or it did not run and the
reason is printed beside it. A run that covered less than the whole set therefore
cannot be read as a run that covered it and found nothing.

A leg is a name and a function taking the root of a checkout and returning a
verdict. Adding one is a module beside this one and a line in ``LEGS``.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path

from raumbuch.gate import hook, layout

PASSED = "passed"
REFUSED = "refused"
NOT_RUN = "not run"


@dataclasses.dataclass(frozen=True)
class Verdict:
    """What a leg found, and why it says so.

    ``detail`` is the whole of what a reader gets, so it names the property the
    leg holds when it passes and what was refused when it does not.
    """

    state: str
    detail: str


def passed(detail: str) -> Verdict:
    return Verdict(PASSED, detail)


def refused(detail: str) -> Verdict:
    return Verdict(REFUSED, detail)


def not_run(detail: str) -> Verdict:
    return Verdict(NOT_RUN, detail)


@dataclasses.dataclass(frozen=True)
class Leg:
    name: str
    run: Callable[[Path], Verdict]


LEGS: tuple[Leg, ...] = (
    Leg("layout", layout.run),
    Leg("hook", hook.run),
)


def run(root: Path, legs: Sequence[Leg] = LEGS) -> list[tuple[Leg, Verdict]]:
    """Run each leg in order, stopping at the first refusal.

    A leg after a refusal is not run, and it is reported rather than dropped,
    with the refusal that stopped the run and what running it would cost.
    """
    results: list[tuple[Leg, Verdict]] = []
    stopped_at: str | None = None
    for leg in legs:
        if stopped_at is not None:
            results.append(
                (
                    leg,
                    not_run(
                        f"the gate stopped at {stopped_at}; running this leg costs "
                        f"repairing what {stopped_at} refused and running the gate again"
                    ),
                )
            )
            continue
        verdict = leg.run(root)
        results.append((leg, verdict))
        if verdict.state == REFUSED:
            stopped_at = leg.name
    return results


def report(root: Path, results: Iterable[tuple[Leg, Verdict]]) -> list[str]:
    """The lines a run prints, in the order the legs were declared."""
    results = list(results)
    width = max((len(leg.name) for leg, _ in results), default=0)
    lines = [f"raumbuch gate, against {root}"]
    for leg, verdict in results:
        lines.append(f"  {leg.name.ljust(width)}  {verdict.state:<7}  {verdict.detail}")
    counted = {state: 0 for state in (PASSED, REFUSED, NOT_RUN)}
    for _, verdict in results:
        counted[verdict.state] = counted.get(verdict.state, 0) + 1
    lines.append(
        f"{len(results)} leg(s) declared: {counted[PASSED]} passed, "
        f"{counted[REFUSED]} refused, {counted[NOT_RUN]} not run."
    )
    return lines


def main(root: Path, legs: Sequence[Leg] = LEGS, out=None) -> int:
    """Run the gate and print the report. Non-zero exactly when a leg refused."""
    import sys

    out = sys.stdout if out is None else out
    results = run(root, legs)
    for line in report(root, results):
        print(line, file=out)
    return 1 if any(verdict.state == REFUSED for _, verdict in results) else 0
