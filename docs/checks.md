# The checks

Every check this repository runs, what it refuses, and where it runs.

Most of them are legs of the gate verb. One command runs those:

    python3 -m raumbuch gate

Five are not. The section on the names a reader sees says which of them a reader
meets on a change, and the fuzz job is the one that appears on neither a push nor
a pull request.

The table is appended to by the issue that builds a check, one row per check, and
the surrounding text is issue #33's. That direction is chosen here so that the
alternative, one issue writing the list on behalf of the others, does not produce
two half-lists. A row is added when its check exists, never in advance of one.

| Check | Refuses | Where it runs |
| --- | --- | --- |
| `layout` | a tree missing a directory the layout block of record 0001 names | the `gate` workflow, and the pre-push hook |
| `hook` | a `.githooks/pre-push` carrying any instruction besides the gate invocation | the `gate` workflow, and the pre-push hook |
| `records` | a decision record departing from the shape record 0000 fixes, and an index that misses one or points at one that is not there | the `Decision records are well formed` job of the `records` workflow, and the pre-push hook |
| `pin` | an interpreter or a distribution whose version is not held in one file, a lockfile that disagrees with the manifest, and a version literal in a workflow | the `toolchain pin` job of the `pin` workflow, and the pre-push hook |
| `format` | a tree the formatter would change | the `format` job of the `style` workflow, and the pre-push hook |
| `lint` | a finding against the rule set in `pyproject.toml` | the `lint` job of the `style` workflow, and the pre-push hook |
| `headless` | an environment where a display can be opened or elevation is granted | the `Headless and unprivileged test contract` job of the `contract` workflow |
| `network` | a unit suite that reaches for the network, run where there is no route out | the `No network in the test suite` job of the `isolation` workflow |
| `determinism` | two runs of one input, under different hash seeds and worker counts, that disagree | the `Determinism replay` job of the `determinism` workflow, and the pre-push hook |
| `build` | a file in the tree that does not compile, or a module under `src/` that does not import | the `build` job of the `suite` workflow, and the pre-push hook |
| `tests` | a unit suite that does not pass on the tree being judged | the `unit tests` job of the `suite` workflow, and the pre-push hook |
| the fuzz harness | an input to the record loader or the expression parser that crashes, escapes the grammar, executes something, or builds a tree larger than its text | the `Fuzz the loader and the parser` job of the `fuzz` workflow, weekly and on request; a small campaign runs inside `tests` |

## The pin, and the three ways it stops being one

A catalogue that has to reproduce a classification in five years cannot be built
by whatever version of the toolchain the runner happened to have that week.
Record 0006 sharpens it: a stored derived value is anchored to a digest over the
source that produced it, and an anchor is worth something only where the thing
it anchors can be brought back.

Two files hold the versions. `.python-version` holds the interpreter, which is a
runtime rather than a distribution to install. `requirements.lock` holds every
distribution, pinned to one version and to the hash of every file that version
publishes, and the install route is `pip install --require-hashes -r
requirements.lock`, which record 0001 fixes.

Every file of every version is pinned rather than the ones a runner happens to
fetch, so a gate run on a machine this project has not been run on yet meets a
pin rather than a resolution.

The `pin` leg refuses three things. A version literal in a workflow, because the
pin means nothing where a second copy exists and a workflow is where the second
copy goes. A lockfile that disagrees with `pyproject.toml`, in either direction:
a name in the manifest and not the lock is a dependency arriving unpinned, and a
name in the lock and not the manifest is a pin for something nothing installs. A
locked entry with no hash or pinned by anything other than `==`, because a
version without a hash is still a name resolved at install time.

**The one version literal a workflow may carry is the `# vX.Y.Z` comment after
an action's forty character commit hash.** The hash is the pin and the comment
is what makes it readable, so a rule that deleted it would cost the reader the
supply-chain half of the same decision. The pattern is three parts for a
neighbouring reason: a two-part number reaches a standard's identifier in a
comment, which is not a version of anything this file pins.

The workflow auditor's version sits in the lockfile with everything else, and
the workflow that runs it reads it out of that file. Whether a tool used only by
a guard belongs beside the language toolchain was the open half of issue #27,
and this is the answer: a version is pinned in one file or it is pinned in
several. It is declared in its own group so that nothing installs it by
accident.

What this leg does not judge. Whether the pinned version is the right one, which
is a judgement. Whether a workflow installs from the lock at all, which is
readable and is not refused: `.github/workflows/` is scanned for version
literals rather than for install routes. And the container images two jobs run
in, `python:3` in the `contract` and `isolation` workflows, which name no
version and therefore pass. The `isolation` job's image is a `docker run`
argument and could read the pin file; the `contract` job's is a job-level field
where no file can be read, so pinning those two is a change to how those jobs are
started rather than to this check.

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

## The decision records, and what reads their shape

Record 0000 says what shape a decision record takes: the sections it carries, in
order, the words its status may hold, and what a supersession and a correction
look like. The `records` leg refuses a departure from that, and it reads the
required section list and the allowed status words out of record 0000's own
fenced blocks rather than carrying a copy. Changing a heading there changes what
the check requires, which is the coupling the record asks for.

The index is read in both directions. Every record appears in
`docs/decisions/README.md` exactly once, and every row of it points at a file
that exists, because an index that silently misses a record is worse than no
index: a reader who trusts it concludes the decision was never made. A row is a
table row anchored at the start of a line and never an occurrence of a filename,
since the prose above the table links to record 0000 as well and that link is the
index working rather than a second row.

**A heading is a heading outside a fence.** Record 0000 writes its required
section list inside one, and record 0003 carries a worked example whose comments
begin with a hash. A checker scanning line by line reads twelve sections in the
record that defines what a section is and refuses its own specification on the
first run, which reads as a broken document rather than as a broken checker. The
same in the other direction: the correction heading form is written out in record
0000 inside a fence, and a scan that ignored fences would read the specification
as an instance of the thing it specifies.

The fixtures are a directory of their own rather than files under
`docs/decisions/`. A malformed record inside the directory the check scans would
redden the check on `main` for as long as it stayed there, so the checker takes
the directory it judges and the fixtures live in a temporary one. That is an
exclusion by construction rather than a list somebody could shorten without
seeing what it held.

What this leg does not judge. Whether a row's status matches the record's, and
whether a `## Date` is a date, are both readable and neither is refused here:
record 0000 hands this check its required sections, its status words, its two
index directions and its two correction rules, and those are what it holds.
Whether a `## Question` is more than a restatement of the title, and whether a
rejected alternative carries a reason, are judgements about meaning that no
reading of the tree makes.

## The build, in a language with no compiler

Record 0001 chose Python and said what follows: where this project wants a
refusal at the earliest moment, it has to be a check rather than a build failure.
The `build` leg is that check, and it asks two questions because one does not
answer the other.

Every Python file in the tree is compiled. That reaches a file nothing imports,
which is where a syntax error survives longest. Every module under `src/` is then
imported, which compiling proves nothing about: a name that moved, a module
deleted from under an import and a cycle between two modules all compile and none
of them imports.

The import runs in a subprocess. Importing into the process running the gate
would leave whatever a module does at import time inside the interpreter that
goes on to judge the rest of the tree, and a leg that changes the thing it judges
is not a check. The same subprocess is told to write no bytecode, so judging a
tree adds no files to it.

Nothing is run. A module that imports and then fails when it is called is the
suite's question.

## The fuzz targets, and what each one is looking for

Two components read input that did not come from here: the record loader and the
expression parser. A catalogue is a thing people download and a record is a thing
people write by hand. `tests/fuzz.py` generates input for both from a seed and
judges four properties over every input it produced.

`nothing-crashes` admits two outcomes from a component and no third: a value, or
a refusal naming a reason from the closed vocabulary. Anything else is a crasher.

`grammar-containment` walks what the parser built and asks that it is made of the
declared node kinds, that every function applied is one of the declared ones, and
that every exponent is a whole number. A parser accepting something outside its
own grammar is how a construct nobody expects gets into a record.

`nothing-executes` runs the loader under an audit hook and fails on any event
that would mean the process ran, opened or fetched something. The loader's own
documentation asserts that loading executes nothing; this is the difference
between asserting it and watching it. The hook cannot be uninstalled once it is
on, so this target runs in the harness and never inside the unit suite.

`memory-is-bounded` counts the nodes the parser built and requires no more of
them than the input had characters. Every node consumes at least one token and
every token at least one character, so the bound is exact rather than tuned.

Two things this does not do. It gates no merge: a red campaign is an issue to
open. And it does not look for a round trip through a writer, because there is no
writer in this tree; whether there is ever one is issue #130.

Every crasher a campaign has found is kept in `tests/fuzz.py` as the input that
produced it, with the reason it is now refused by, and `tests/test_fuzz.py` asks
for that reason rather than only for the absence of a traceback. A crasher
repaired into a different crash would otherwise read as fixed.

## The suite, and the name it runs under

The `tests` leg runs the unit suite over `tests/`, in a subprocess, out of the
checkout the gate was given and with that checkout's `src/` ahead of anything
installed. What is judged is the tree at that root rather than a copy of the
project in the environment.

The leg is `tests` and the check a reader sees is `unit tests`. Those are two
different names for the same thing and the second is the contract: it is what a
pull request shows and what entry 7 of issue #2 would make a precondition of a
merge. The gate's own names are what `--only` takes, and the table above carries
both.

**Inside a suite this leg started, the leg does not run and the report says so.**
The suite contains a test that runs the whole gate against this tree, so a leg
that ran the suite unconditionally would run it from inside itself until the
machine stopped. The subprocess carries a variable saying a gate-started suite is
in progress, and a leg that sees it reports that it did not run, with what
running it costs. Two consequences, and both are bounds rather than gaps. A gate
report produced inside a suite run says the suite was not judged. And running the
suite by hand runs it twice, once directly and once from the whole-gate test
inside it, which is where this leg is exercised. Two is where it stops.

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

## No network in the test suite

Record 0014 says the library and the command-line entry point make no network
connection, and it names which half of that a check can refuse: the test suite.
The `network` leg is that check.

The denial belongs to the environment and never to the code being judged. A flag
the suite sets on itself is read after the interpreter has started, and the call
this check exists to catch is the one inside a dependency at import time, which
runs first. So the suite is run inside a container started with `--network none`,
which gives it a namespace holding a loopback interface and nothing else. There
is no route out and no interface for one to be added to.

The leg does not trust that denial either. It establishes that no route exists,
then runs `tests/contract_network.py`, which tries to resolve a name and open a
connection, and refuses if anything got out. Only then does it run the suite.
The fixture is the inverse of the one a guard usually carries: it succeeds
wherever a route exists, so it is run only where the answer has to be no. It is
named so that no default pattern collects it, which is what keeps it out of
`unit tests` rather than a note somebody has to read.

**Where a route exists, this leg does not run and says so.** That is the common
case on a workstation, and it is also why running the gate locally opens no
connection: the route probe is a datagram socket connected to a documentation
address, which asks the kernel which interface would carry a packet and sends
none, and the fixture is reached only once that probe has said there is nowhere
for a packet to go.

**A green run here covers the suite and not the library.** Record 0014 states
the bound in its own text rather than leaving a reader to work it out: a code
path the suite never reaches can contain a connection the suite never sees. Two
further gaps are named in that record and neither is this check. Nothing refuses
a hard-coded address in a source file, which is issue #93, and nothing refuses a
dependency that opens a socket of its own, which no issue holds.

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

## The names a reader sees, read off a run

The table above is the gate's own names, which is what `--only` takes. What
appears beside a commit is a job name, and the mapping is not one to one. These
were read off runs rather than off the workflow files, because the names a
reader sees are what a run produced:

    gh api repos/iderex/raumbuch/commits/8521f91/check-runs --jq '.check_runs[].name'

On a pull request, fifteen distinct names, one of which is produced twice: `build`, `unit tests`, `format`, `lint`,
`gate`, `Decision records are well formed`, `toolchain pin`, `Determinism
replay`, `Headless and unprivileged test contract`, `No network in the test
suite`, `Reject Trojan Source Unicode`, `DCO sign-off`,
`dependency-review`, `Audit workflows (zizmor)`, and `zizmor`.

Four things in that list are worth knowing before it is read as a list of jobs.

`Reject Trojan Source Unicode` appears twice, once for the push and once for the
pull request, because its workflow triggers on both and a pull request from a
branch of this repository is both events.

`zizmor` and `Audit workflows (zizmor)` are two different things with one tool
behind them. The second is the job. The first is a code-scanning check run
created by GitHub Advanced Security when that job uploads its findings, so it
reports on the same audit from the security tab rather than from the workflow.

`Scorecard analysis` never appears on a pull request. Its workflow's trigger
block says why in its own text: a schedule, a push to the default branch and a
branch protection rule change, and no pull request trigger, because that path is
experimental upstream and cannot publish results. So it is a check that exists
and that a contributor cannot see on their own change.

`update-pip-graph` appears on `main` and is declared in no workflow in this
tree. It is GitHub's own dependency submission, which started running when
`requirements.lock` landed:

    gh api repos/iderex/raumbuch/actions/runs/31309584586 --jq '{name, path, event}'
    {"event":"dynamic","name":"Graph Update: pip in /. #1514778074","path":"dynamic/dependabot/update-graph"}

A reader counting green ticks and matching them against `.github/workflows/`
would be one over and would not find the file.

## The five that are not gate legs

`DCO sign-off` reads every non-merge commit of a pull request and refuses one
whose message carries no `Signed-off-by` matching its author. It fails closed:
a commit range it cannot walk reddens rather than passing with nothing verified.

`dependency-review` refuses a pull request that introduces a dependency with a
known vulnerability. It runs on pull requests only, because it compares a head
against a base and there is nothing to compare a push to.

`Audit workflows (zizmor)` audits the workflow files themselves at
`--min-severity=low`: template injection, cache poisoning, dangerous triggers,
excessive permissions, an action pinned to a tag rather than a hash. Its version
comes from `requirements.lock` like everything else.

`Scorecard analysis` scores this repository against the OpenSSF supply-chain
checks and publishes the score. It is a self-audit and a checklist rather than a
guarantee, and it builds and tests nothing.

`Fuzz the loader and the parser` runs the campaign the section above describes,
weekly and on request. It is a leg of nothing, on purpose: a campaign worth
running takes minutes and its value is a different seed each time, so in front of
every push it would cost every push and still only ever run one seed. The unit
suite runs a small campaign at seed zero instead, which keeps the harness itself
from rotting.

Those last two are the checks a contributor cannot see on their own change. One
publishes from the default branch only and the other is not triggered by a change
at all.

Two comments in those workflow files describe a project that is not this one.
The scorecard workflow's header refers twice to a release pipeline for a plugin,
and the workflow auditor's header refers to a `publish-beta.yml` that is not in
this tree and to an issue number from another tracker. Neither describes anything
this repository builds. They are named here rather than repaired, because this
file's scope is the documents and not the workflows, and issue #33 carries the
pointer.

## What a run says, and what it does not

Every declared leg appears in a report, whatever became of it. A leg that ran and
passed, a leg that refused, a leg that did not run because an earlier one refused,
and a leg nobody asked for are four different lines, so a run covering part of the
set cannot be read as a run that covered all of it.

A leg whose tool is not installed reports that it did not run and what running it
would cost. It does not pass. The `format` and `lint` legs are the two that can
say this today, because ruff comes from the lockfile:

    python3 -m pip install --require-hashes -r requirements.lock

`headless` and `network` are the two that do not run on a workstation, each for a
reason in its own section above, and a job that has to cover either asks for it
with `--require`, which turns a leg that did not run into a refusal.

## What is not here

Nothing refuses a merge. The ruleset on `main` requires a pull request and no
status check:

    gh api repos/iderex/raumbuch/rulesets/20527860 --jq '[.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context]'
    []

So every check named in this document runs and none of them stands behind a
merge. A reader who sees green ticks on a pull request and concludes the merge
was gated on them is wrong. The ruleset requires a pull request, refuses a
deletion and a force push, and carries no bypass actors, and that is the whole of
what a merge has to pass:

    gh api repos/iderex/raumbuch/rulesets/20527860 --jq '{name, enforcement, rules: [.rules[].type], bypass: .bypass_actors}'
    {"bypass":[],"enforcement":"active","name":"gate","rules":["deletion","non_fast_forward","pull_request"]}

Which of these names becomes a precondition is entry 7 of issue #2, and it is
open.
