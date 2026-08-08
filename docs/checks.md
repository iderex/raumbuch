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
