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
import sys
from collections.abc import Callable, Collection, Iterable, Sequence
from pathlib import Path

from raumbuch.gate import (
    determinism,
    formatting,
    headless,
    hook,
    importing,
    index,
    layout,
    linting,
    network,
    records,
    suite,
    toolchain,
)

PASSED = "passed"
REFUSED = "refused"
NOT_RUN = "not run"


@dataclasses.dataclass(frozen=True)
class Verdict:
    """What a leg found, and why it says so.

    ``detail`` is the whole of what a reader gets, so it names the property the
    leg holds when it passes and what was refused when it does not. It may run
    to several lines where a leg has a tool's findings to hand on.
    """

    state: str
    detail: str


def passed(detail: str) -> Verdict:
    return Verdict(PASSED, detail)


def refused(detail: str) -> Verdict:
    return Verdict(REFUSED, detail)


def not_run(detail: str) -> Verdict:
    return Verdict(NOT_RUN, detail)


def skipped(detail: str) -> Verdict:
    """A leg that could not run, with why and what running it would cost."""
    return Verdict(NOT_RUN, detail)


@dataclasses.dataclass(frozen=True)
class Leg:
    name: str
    run: Callable[[Path], Verdict]


# In order, and the order is cheapest first among the legs that would refuse for
# the same reason. A tree that does not compile is refused by `build` before the
# formatter is asked what it thinks of the same file, and the suite runs last
# because it is the most expensive thing here and the least likely to be the
# first thing wrong.
LEGS: tuple[Leg, ...] = (
    Leg("layout", layout.run),
    Leg("hook", hook.run),
    Leg("records", records.run),
    Leg("index", index.run),
    Leg("pin", toolchain.run),
    Leg("build", importing.run),
    Leg("format", formatting.run),
    Leg("lint", linting.run),
    Leg("determinism", determinism.run),
    Leg("headless", headless.run),
    Leg("network", network.run),
    Leg("tests", suite.run),
)


def require(
    results: list[tuple[Leg, Verdict]], required: Collection[str]
) -> list[tuple[Leg, Verdict]]:
    """Turn a leg that did not run into a refusal, where the run required it.

    A leg that did not run leaves the gate green over a set it did not cover.
    Where a run exists to cover one leg, and that leg is the one that decides
    whether an environment is the environment it was built to judge, the run
    saying so is what stops a misconfigured job from reporting a contract met
    that nothing asked about.
    """
    judged = []
    for leg, verdict in results:
        if leg.name in required and verdict.state == NOT_RUN:
            judged.append(
                (
                    leg,
                    refused(
                        f"this run required {leg.name} to run and it did not: "
                        f"{verdict.detail}"
                    ),
                )
            )
            continue
        judged.append((leg, verdict))
    return judged


def run(
    root: Path,
    legs: Sequence[Leg] = LEGS,
    only: Collection[str] | None = None,
    required: Collection[str] | None = None,
) -> list[tuple[Leg, Verdict]]:
    """Run each leg in order, stopping at the first refusal.

    A leg after a refusal is not run, and a leg nobody asked for is not run.
    Neither is dropped: both are reported, with the reason and with what running
    them would cost, so the report always carries every declared leg.
    """
    results: list[tuple[Leg, Verdict]] = []
    stopped_at: str | None = None
    for leg in legs:
        if only is not None and leg.name not in only:
            results.append(
                (
                    leg,
                    not_run(
                        "not asked for: this run was limited to "
                        f"{', '.join(sorted(only))}. Asking for it costs running "
                        f"the gate with no --only, or with --only {leg.name}"
                    ),
                )
            )
            continue
        if stopped_at is not None:
            results.append(
                (
                    leg,
                    not_run(
                        f"the gate stopped at {stopped_at}; running this leg "
                        f"costs repairing what {stopped_at} refused and running "
                        "the gate again"
                    ),
                )
            )
            continue
        verdict = leg.run(root)
        results.append((leg, verdict))
        if verdict.state == REFUSED:
            stopped_at = leg.name
    return require(results, required) if required else results


def report(root: Path, results: Iterable[tuple[Leg, Verdict]]) -> list[str]:
    """The lines a run prints, in the order the legs were declared."""
    results = list(results)
    width = max((len(leg.name) for leg, _ in results), default=0)
    lines = [f"raumbuch gate, against {root}"]
    for leg, verdict in results:
        head, *rest = verdict.detail.splitlines() or [""]
        lines.append(f"  {leg.name.ljust(width)}  {verdict.state:<7}  {head}")
        indent = " " * (width + 13)
        lines.extend(f"{indent}{line}" for line in rest)
    counted = dict.fromkeys((PASSED, REFUSED, NOT_RUN), 0)
    for _, verdict in results:
        counted[verdict.state] = counted.get(verdict.state, 0) + 1
    lines.append(
        f"{len(results)} leg(s) declared: {counted[PASSED]} passed, "
        f"{counted[REFUSED]} refused, {counted[NOT_RUN]} not run."
    )
    return lines


def main(
    root: Path,
    legs: Sequence[Leg] = LEGS,
    out=None,
    only: Collection[str] | None = None,
    required: Collection[str] | None = None,
) -> int:
    """Run the gate and print the report. Non-zero exactly when a leg refused."""
    out = sys.stdout if out is None else out
    results = run(root, legs, only, required)
    for line in report(root, results):
        print(line, file=out)
    return 1 if any(verdict.state == REFUSED for _, verdict in results) else 0
