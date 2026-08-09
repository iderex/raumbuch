# Contributing

## From a clone to a green gate

Four commands, and the fourth is the gate. They were run in this order on a
fresh clone, and what came back is in the pull request body of issue #33 rather
than asserted here.

    python3 -m venv ../raumbuch-env
    ../raumbuch-env/bin/pip install --require-hashes -r requirements.lock
    ../raumbuch-env/bin/pip install --no-deps --no-build-isolation -e .
    ../raumbuch-env/bin/python -m raumbuch gate

On Windows the environment's programs are under `Scripts` rather than `bin` and
everything else is the same.

**The environment goes beside the clone rather than inside it.** The `build` leg
compiles every Python file under the root it is given, and a `.venv` in the
checkout is several hundred files this repository did not write. It does not
redden the gate today, and it is a set the run reports as though it were the
tree. Issue #128 is where the leg learns to leave an environment alone; until
then, the path above is the one that judges this project and only this project.

The interpreter version is in `.python-version` and nothing chooses it for you:
a `python3` that is not that version runs the gate anyway, and the `pin` leg
judges the file rather than the interpreter running it. Every dependency comes
from `requirements.lock`, hash by hash, which is why the install carries
`--require-hashes`.

## The gate

One command runs the whole gate:

    python3 -m raumbuch gate

Its legs run in order and stop at the first refusal. The run prints every leg
that is declared and what became of it, so a run that stopped early cannot be
read as a run that covered everything and found nothing. A leg that could not
run where you are says so and says what running it would cost.

What the legs are is not listed here. The run prints them, and a list in a
document drifts against the thing it describes. `docs/checks.md` carries one row
per check with what it refuses and where it runs.

One leg at a time:

    python3 -m raumbuch gate --only lint

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

## Every change starts as an issue

An issue says what is wrong, what the evidence is, and what done means. Where the
evidence is a number, it carries the command that produced it, run against the
reference the reader will have rather than against your working tree.

A change lands as a pull request. Its body says what changed and what failure
that prevents, and it carries the evidence for every claim it makes: the command
and what came back, not a summary of what came back. A guard is proved by
deleting it and watching the suite go red, and that run belongs in the body too.

One topic per commit and per pull request. A commit carrying two unrelated
changes has a message describing one of them.

Before an artefact is built, whether the means fits is argued in the issue or in
the pull request body: the language, the format, the tool, the runtime. One
sentence naming the means and the reason it fits. A means that was right for the
last artefact is an assumption about this one.

Every commit is signed off, which is what the `DCO sign-off` check reads:

    git commit -s

A negative disclosure stays negative. Where a passage admits something was not
done, not measured or not covered, the admission survives every edit.

## What stands behind a merge

The ruleset on `main`:

    gh api repos/iderex/raumbuch/rulesets/20527860 --jq '{name, enforcement, rules: [.rules[].type], bypass: .bypass_actors}'
    {"bypass":[],"enforcement":"active","name":"gate","rules":["deletion","non_fast_forward","pull_request"]}

A pull request is required, the branch cannot be deleted or force-pushed, and
there are no bypass actors. **No check is required of a merge**:

    gh api repos/iderex/raumbuch/rulesets/20527860 --jq '[.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context]'
    []

So every check in `docs/checks.md` runs on every push and every pull request,
and every one of them can be red while the merge is still available. A reader
who sees green ticks and concludes the merge was gated on them is wrong, and
this paragraph is where that is corrected. Which of the names becomes a
precondition is entry 7 of issue #2, and it is open.
