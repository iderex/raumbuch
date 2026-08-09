# The checks

Every check this repository runs, what it refuses, and where it runs.

A check is a leg of the gate verb. One command runs them all:

    python3 -m raumbuch gate

The table is appended to by the issue that builds a check, one row per check, and
the surrounding text is issue #33's. That direction is chosen here so that the
alternative, one issue writing the list on behalf of the others, does not produce
two half-lists. A row is added when its check exists, never in advance of one.

| Check | Refuses | Where it runs |
| --- | --- | --- |
| `layout` | a tree missing a directory the layout block of record 0001 names | the `gate` workflow, and the pre-push hook |
| `hook` | a `.githooks/pre-push` carrying any instruction besides the gate invocation | the `gate` workflow, and the pre-push hook |
| `format` | a tree the formatter would change | the `format` job of the `style` workflow, and the pre-push hook |
| `lint` | a finding against the rule set in `pyproject.toml` | the `lint` job of the `style` workflow, and the pre-push hook |
| `headless` | an environment where a display can be opened or elevation is granted | the `Headless and unprivileged test contract` job of the `contract` workflow |
| `determinism` | two runs of one input, under different hash seeds and worker counts, that disagree | the `Determinism replay` job of the `determinism` workflow, and the pre-push hook |

## The formatter and the linter

Both are ruff, one tool doing two jobs, which is one version to pin and one
dependency to lock. Both refuse and neither advises: a tree the formatter would
change is refused rather than reformatted, and the repair is one command the
contributor runs.

The rule set is chosen in `pyproject.toml` rather than accumulated. Every rule
switched off is switched off there beside the reason it is off, and ruff's own
`RUF100` refuses a suppression that has stopped being needed, so a rule that was
turned off once does not stay off by inertia.

Markdown is outside what either judges. Ruff formats and lints the code inside a
Markdown block, and the Markdown here is `docs/decisions/`, where a landed record
is an argument somebody made and the code in it is part of what was argued.
Reformatting one would be editing a record, which record 0000 refuses.

Neither leg reformats or fixes anything. A leg that repaired the tree would be a
check that passes on a tree nobody wrote.

## The test contract

Every test in the main suite runs with no display attached, with no elevated
privileges, and with no device the runner does not have. A suite that needs a
desktop session is a suite that runs on the machine of whoever wrote it.

Hardware-bound work is a separate and honestly named harness. The classification
runs that need very large memory belong to the seventh milestone, they do not run
in the main suite, and a green main suite is never reported as though they had
run. Record 0011, issue #20, is where those runs and their budget are fixed.

The `headless` leg proves the contract by asking rather than by assuming. Two
fixtures in `tests/` do the asking, one opening a display and one asking to
become the superuser, and the leg refuses where either succeeds. Neither is
collected by the suite: both are named so that no default pattern picks them up,
which is an exclusion by construction rather than a note somebody has to read.

The two are not symmetric, and the difference is worth knowing before somebody
tries to make them so. A test that opens a display fails on a machine with no
display, which is the check working. A request for elevation on a developer's
machine is not a failure at all; it is a consent dialog taking the screen from
whoever is sitting there, and a proof that interrupts the person reading it is a
proof nobody keeps running. So the elevation fixture asks only where the answer
is a refusal by construction, which is the container. **The elevation half of
this contract is proven on a runner and never locally.** That is a bound on the
check rather than a gap in it, and it is written here rather than discovered.

The leg does not run at all on a machine with a display attached, off POSIX, or
where there is no toolkit to open a window with, and it says so with what running
it would cost. A missing toolkit is not a missing display: reading the first as
the second is a check that passes on any image, so nothing was asked and nothing
is claimed. Because a leg that did not run
leaves a job green over a set it did not cover, the job asks for the leg and
requires it: `--require headless` turns a leg that did not run into a refusal, so
a container that lost its unprivileged user or gained a display reddens rather
than passes.

## The determinism replay

Record 0012 promises that two runs of the same input produce the same record.
The `determinism` leg replays every declared input twice inside one gate run and
compares what came back.

The two runs differ in two ways and each catches something the other does not. A
different hash seed moves the native iteration order of a set or a map, which is
the cheapest way to break the property and the hardest to notice. A different
worker count, greater than one in at least one of the two runs, is what record
0012 requires outright: two single-threaded runs of the same code agree for
reasons that have nothing to do with the property, and a check made of those
would pass on a tree that violated it everywhere.

A hash seed is read once when an interpreter starts, so each run is a
subprocess. Both run the same module, so what is replayed is the code the leg is
about.

The comparison drops the excluded fields, which are a list in the leg rather
than a rule a reader reconstructs. A date changes between two runs by
construction and a cost is a measurement of a run rather than of a geometry, and
record 0012 puts both outside the promise. What else joins the list is issue
#56, where a finished run first writes a record carrying those fields.

The inputs today are the loader and the record round-trip, which is what exists.
Adding one is one line. Extending the check to the classifier is issue #121.

A fixture whose output depends on iteration order is declared beside the inputs
and is never replayed by the leg, because a fixture that violates the property
cannot be an input the gate replays without the gate being red for ever. It is
reached by name from `tests/test_gate_determinism.py`, where the leg is run
against it and refuses. It carries twelve names rather than two, because a set
of two reorders under a new seed only sometimes and a proof that fails
occasionally is worse than none.

## What a run says, and what it does not

Every declared leg appears in a report, whatever became of it. A leg that ran and
passed, a leg that refused, a leg that did not run because an earlier one refused,
and a leg nobody asked for are four different lines, so a run covering part of the
set cannot be read as a run that covered all of it.

A leg whose tool is not installed reports that it did not run and what running it
would cost. It does not pass. The `format` and `lint` legs are the two that can
say this today, because ruff comes with the development extra:

    python3 -m pip install -e ".[dev]"

## What is not here

Nothing refuses a merge. The ruleset on `main` requires a pull request and no
status check:

    gh api repos/iderex/raumbuch/rulesets/20527860 --jq '[.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context]'
    []

So every check in the table above runs and none of them stands behind a merge.
Which of these names becomes a precondition is entry 7 of issue #2, and it is
open.
