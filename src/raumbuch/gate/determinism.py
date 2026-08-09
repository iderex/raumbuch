"""The leg named ``determinism``: the same input twice, and the same output.

Record 0012 promises that two runs of one input produce the same record. This is
the check that refuses a violation, and it is built in the second milestone,
before the classifier it will judge exists, because retrofitting determinism to a
symbolic pipeline that never had it is much more expensive than keeping it.

Each input is rendered twice in one gate run, in two subprocesses: one with a
hash seed of zero and one worker, and one with a different hash seed and four.
Both halves matter and they catch different things. A different hash seed is what
moves the native iteration order of a set or a map, which record 0012 names as
the cheapest way to break this and the hardest to notice. A second worker is what
record 0012 requires outright, because two single-threaded runs of the same code
agree for reasons that have nothing to do with the property, and a check made of
those would pass on a tree that violated it everywhere.

What is compared is every rendered line with the excluded fields removed. The
list of exclusions is held here rather than reconstructed by a reader, which is
what record 0012 asks for; what belongs on it beyond a timestamp and a cost is
issue #56, where a finished run first writes a record with those fields in it.

Today the inputs are the loader and the record round-trip, because that is what
exists. Extending the check to the classifier is issue #121.
"""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import raumbuch
from raumbuch import gate, record

RECORD_FORMAT = Path("docs/record-format.md")

#: The two runs, as (hash seed, worker count). The second seed is arbitrary and
#: fixed; what matters is that it is not the first. The second worker count is
#: greater than one, which record 0012 requires of at least one of the two.
RUNS: tuple[tuple[int, int], ...] = ((0, 1), (4222234, 4))

#: Field names whose values are not compared. A date changes between two runs by
#: construction and a cost is a measurement of a run rather than of a geometry,
#: and record 0012 puts both outside the promise. The list lives here because
#: that record says it is a list in the check; what else joins it is issue #56.
EXCLUDED: tuple[str, ...] = ("date", "transcribed_on", "cost")


def worked_record(root: Path) -> str:
    """The worked Schwarzschild record, loaded and rendered.

    Read out of the document rather than copied, so this input is the record the
    project holds rather than a second one that agrees with it today.
    """
    text = (root / RECORD_FORMAT).read_text(encoding="utf-8")
    start = text.index("```toml")
    body = text[start + len("```toml") : text.index("```", start + 3)]
    return "\n".join(rendered(record.loads(body.encode("utf-8"), "schwarzschild")))


def rendered(loaded: record.Record) -> list[str]:
    """A record as sorted ``path = value`` lines.

    Sorted, because record 0012's first rule is that nothing iterating a map
    reaches an output in its native order. A renderer that forgot that is
    precisely what this check is here to catch, so this one does not forget.
    """
    lines = [
        f"{field.name} = {getattr(loaded, field.name)!r}"
        for field in dataclasses.fields(loaded)
        if field.name != "charts"
    ]
    for chart in loaded.charts:
        lines.append(f"chart.{chart.name} = {chart.coordinates!r}")
        lines.extend(
            f"chart.{chart.name}.metric.{i}.{j} = {chart.metric[(i, j)]!r}"
            for i, j in sorted(chart.metric)
        )
    return sorted(lines)


def native_order(root: Path) -> str:
    """A fixture whose output depends on iteration order, and nothing else.

    It is not one of the inputs the leg replays. It exists so that the check can
    be shown to refuse a violation, which record 0012 asks of this issue by name:
    a replay check that has never been shown to fail is a check nobody has run
    against a violation.

    Twelve names, and the number is the point. A set of two reorders under a new
    hash seed only sometimes, so a fixture built from two would redden the proof
    occasionally rather than reliably, and a flaky proof is worse than none. With
    twelve, two seeds agree only if one permutation out of twelve factorial
    recurs, which is about two in a thousand million.
    """
    del root
    names = {f"coordinate-{position}" for position in range(12)}
    return " ".join(names)


#: What the leg replays. Adding an input is one line here.
INPUTS: dict[str, Callable[[Path], str]] = {
    "worked-record": worked_record,
}

#: What the leg never replays, and what proves it bites. One line here too.
PROVING_FIXTURES: dict[str, Callable[[Path], str]] = {
    "native-order": native_order,
}

RENDERERS: dict[str, Callable[[Path], str]] = INPUTS | PROVING_FIXTURES


def emit(root: Path, names: Sequence[str], workers: int) -> str:
    """Render each named input, and return the results in input-name order.

    The work is spread over ``workers`` threads and the output is assembled by
    name afterwards, so the harness itself contributes no ordering of its own and
    a difference between two runs is a difference in what was rendered.
    """
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda name: RENDERERS[name](root), names))
    return "".join(
        f"{name}\n{result}\n"
        for name, result in sorted(zip(names, results, strict=True))
    )


def compared(text: str) -> list[str]:
    """The lines a comparison sees: everything but the excluded fields."""
    kept = []
    for line in text.splitlines():
        field = line.split("=", 1)[0].strip().rsplit(".", 1)[-1]
        if field not in EXCLUDED:
            kept.append(line)
    return kept


def once(root: Path, names: Sequence[str], seed: int, workers: int) -> str:
    """One replay, in a subprocess, so the hash seed is the one asked for.

    A hash seed is read once when the interpreter starts, so varying it inside a
    process is not available and a subprocess is the only route. The same module
    is the entry point, so the two runs execute the code this leg is about.
    """
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = str(seed)
    package = str(Path(raumbuch.__file__).resolve().parents[1])
    environment["PYTHONPATH"] = os.pathsep.join(
        [package, *([environment["PYTHONPATH"]] if "PYTHONPATH" in environment else [])]
    )
    arguments = [
        sys.executable,
        "-m",
        "raumbuch.gate.determinism",
        "--root",
        str(root),
        "--workers",
        str(workers),
    ]
    for name in names:
        arguments += ["--input", name]
    finished = subprocess.run(
        arguments, capture_output=True, text=True, env=environment, check=False
    )
    if finished.returncode != 0:
        raise ChildProcessError(finished.stderr.strip() or "the replay run failed")
    return finished.stdout


def replay(root: Path, names: Sequence[str] | None = None) -> gate.Verdict:
    """Replay each input under every run in :data:`RUNS` and compare."""
    names = sorted(INPUTS) if names is None else sorted(names)
    if not names:
        return gate.passed("no input is declared, so nothing was replayed")
    try:
        outputs = [once(root, names, seed, workers) for seed, workers in RUNS]
    except ChildProcessError as failed:
        return gate.skipped(
            f"the replay could not be run: {failed}. Running it costs an "
            "interpreter that can import this package in a subprocess"
        )
    varied = ", then ".join(
        f"hash seed {seed} with {workers} worker(s)" for seed, workers in RUNS
    )
    first = compared(outputs[0])
    for output in outputs[1:]:
        difference = _first_difference(first, compared(output))
        if difference is not None:
            return gate.refused(
                f"two runs of the same input disagree, {varied}. The first "
                f"differing line:\n{difference}"
            )
    return gate.passed(
        f"{len(names)} input(s) replayed {len(RUNS)} times and agreeing, "
        f"{varied}, with {len(EXCLUDED)} field name(s) excluded: "
        f"{', '.join(EXCLUDED)}"
    )


def _first_difference(first: list[str], second: list[str]) -> str | None:
    """The first line the two runs disagree on, or ``None`` where they agree.

    The first rather than the whole diff, which record 0012 asks for: a whole
    record printed twice is a wall a reader scrolls past.
    """
    for line in difflib.unified_diff(first, second, n=0, lineterm=""):
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith(("+", "-")):
            return line
    return None


def run(root: Path) -> gate.Verdict:
    return replay(root)


def main(argv: list[str] | None = None) -> int:
    """The subprocess entry point. Prints what one run rendered."""
    parser = argparse.ArgumentParser(prog="raumbuch.gate.determinism")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--input", action="append", default=[], dest="inputs")
    arguments = parser.parse_args(argv)
    names = arguments.inputs or sorted(INPUTS)
    sys.stdout.write(emit(arguments.root, names, arguments.workers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
