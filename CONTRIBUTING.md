# Contributing

## The gate

One command runs the whole gate:

    python3 -m raumbuch gate

Its legs run in order and stop at the first refusal. The run prints every leg
that is declared and what became of it, so a run that stopped early cannot be
read as a run that covered everything and found nothing.

Two legs are declared today, `layout` and `hook`. The rest of the gate is built
by the issues of the second milestone and lands as a module beside them and a
line in the leg list, not as logic in a hook or a workflow file.

The verb runs out of a checkout with `PYTHONPATH=src`, which is where record 0001
puts the package. Installing the project instead gives you the same verb as
`raumbuch gate` and as `python3 -m raumbuch gate` without the variable.

## The pre-push hook

Install it once per clone:

    git config core.hooksPath .githooks

The hook execs the gate verb and nothing else. It runs the same command you would
run by hand, so there is one procedure rather than two that drift.

**Installing it is optional and it is not the enforcement.** It is a courtesy that
shortens the feedback loop: it is skippable with `--no-verify`, it is absent from
a fresh clone until the line above is run, and whether a clone ran it is a fact of
that clone's local git configuration, which no tree holds and nothing here can
read.

What stands behind a merge is the ruleset on `main`:

    gh api repos/iderex/raumbuch/rulesets/20527860 --jq '{name, enforcement, rules: [.rules[].type]}'
    {"enforcement":"active","name":"gate","rules":["deletion","non_fast_forward","pull_request"]}

A pull request is required and the branch cannot be deleted or force-pushed. No
check is required of a merge:

    gh api repos/iderex/raumbuch/rulesets/20527860 --jq '[.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context]'
    []

So the gate runs on every push and on every pull request, and its verdict refuses
nothing on its own. Whether any check name becomes a precondition of a merge is
entry 7 of issue #2, and it is open.

## The rest

This file carries the gate and the hook, which is what issue #24 owed it. How a
change is proposed, what a merge has to pass, and what a contributor signs are
issue #33, and they belong here rather than anywhere else.
