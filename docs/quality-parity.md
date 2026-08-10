# Quality parity: the target gate, the adaptation, and the deviations

The gate this board aims at is the one on the `Flowfin/jellyfin-plugin-sso`
repository. It is a real gate on a real repository rather than an aspiration, and
what stands behind a merge there is readable:

    gh api repos/Flowfin/jellyfin-plugin-sso/rulesets/18802863 \
      --jq '[.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context]'
    ["build","ABI floor build","Package (JPRM) / Build package","Package (JPRM) / Generate SBOM","CodeQL","Analyze (csharp)","DCO sign-off","Deterministic PR-hygiene checks","Enforce greppable invariants","Reject Trojan Source Unicode","Audit workflows (zizmor)","prettier","dependency-review"]

Thirteen checks required of every merge there. What is required of a merge here:

    gh api repos/iderex/raumbuch/rulesets/20527860 \
      --jq '[.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context]'
    []

None. Both commands are in this document so the comparison can be re-run rather
than trusted, and both were run at the commit this document landed at.

Parity does not mean the same thirteen strings. That repository is a plugin for a
media server in a compiled managed language. This one is a symbolic-computation
library with a data catalogue attached, in Python, per record 0001. Some checks
transfer unchanged, some have a counterpart under a different name, and some have
none. Below is which is which, and for every deviation one line of reasoning that
a reader can disagree with.

## Where a name is quoted, it is quoted from the machine

Three kinds of statement appear below and they are not the same claim.

A check that runs here today, named from the tree. Those names were taken from
the workflow files and confirmed against what GitHub reported on a pull request.

A check this board plans, named from the issue that builds it. Those are
reservations. None of them runs, because there is no gate verb and no suite yet.

A gap, where this board has neither.

## The target's thirteen, one at a time

`build`. Planned, same name, issue #25. It is not the same operation: record 0001
chose a language with no compiler, so there is nothing here that fails on a
compiler warning. What `build` can refuse here is an import failure across the
tree together with whatever the linter in issue #26 treats as an error, and that
wording difference is written into #25 rather than settled here.

`ABI floor build`. No counterpart, and no issue holds one. Nothing loads this
project into a host application across a version range, so there is no binary
interface to hold a floor under. The risk that check manages does exist here in a
different shape: a consumer pinned to a record format or to a published interface
and finding it moved. What answers it is the schema version in
`schema/record-1.schema.json`, the identifier and version pair of record 0004, and
the interface promise in issue #82. That is a design answer rather than a check,
and no check refuses a breaking change to any of the three today.

`Package (JPRM) / Build package`. Counterpart planned, issue #96, packaging and
the command-line entry point. The target's packaging is a plugin archive for a
host; here it is a Python distribution and a console script.

`Package (JPRM) / Generate SBOM`. Present today, under the name `Reproducible
build and bill of materials`. Issues #98 and #93 were two asks and both are met
by one job: the `release` verb produces the document out of `requirements.lock`
during the build and refuses one that disagrees with that lock, and the workflow
step uploads what the build wrote rather than assembling a second copy. So the
bill is produced by the build and attached to the run, which is the property the
target's name carries, and nothing generates one by hand at release time.

`CodeQL` and `Analyze (csharp)`. These two are one instrument, a workflow and the
job inside it, and the job names the language. The question issue #93 asked was
whether an equivalent analysis exists for the language record 0001 chose. It
does: CodeQL analyses Python, and `.github/workflows/codeql.yml` carries
`Analyze (python)` over this tree. So the first of the two answers that
done-condition admits is the one this document now states, and the second, that
no tool exists, does not apply.

It is not a leg of the gate. Building the database takes minutes and the gate
runs in front of every push, which is the same argument the reproducible build
is held out by. It is also not required of a merge, and neither is anything
else here.

Two bounds. It runs with `build-mode: none`, so it parses the source rather than
observing a build, which for an interpreted package is the whole of what there
is to observe and is written down rather than left to be assumed. And what it
found on the run that landed it is in that pull request body; a green code
scanning job is a tool finding nothing it knows to look for, which is not the
same statement as source with nothing wrong in it.

`DCO sign-off`. Present today, same name, and it is the same instrument rather
than an equivalent one. `.github/workflows/dco.yml` carries the job named
`DCO sign-off`, it runs on every pull request, and it verifies a `Signed-off-by`
trailer matching the author on every non-merge commit in the range.

`Deterministic PR-hygiene checks`. No counterpart today and no issue holds one.
Issue #93 named it as one of four things missing and its done-conditions did not
ask for it, so #93 closed without it and this paragraph is where that is
recorded rather than left as a planned counterpart nobody is holding.

`Enforce greppable invariants`. Present today, under that exact name. It carries
three patterns and each names the record it comes from: record 0001 for the
symbolic layer named outside `src/raumbuch/algebra/`, record 0009 for floating
point in code under `src/`, and record 0014 for a module that reaches the
network imported outside the two files that prove there is no route. Each has a
fixture that reddens it and reddens no other pattern.

The fourth pattern this paragraph used to promise is not there. Record 0003
requires a derived field to carry its command, its commit and its date, and
nothing in this tree writes a record, so there is no site for a pattern to be
about. Whether a writer is ever built is issue #130, and a pattern with no
possible subject passes on every tree and reads as coverage.

`Reject Trojan Source Unicode`. Present today, same name, same instrument.
`.github/workflows/unicode-guard.yml` refuses bidirectional and invisible Unicode
control characters in tracked text, on every branch and every pull request, and it
fails closed on a scanner error rather than reading a broken scanner as a clean
tree.

`Audit workflows (zizmor)`. Present today, same name.
`.github/workflows/zizmor.yml` carries it.

`prettier`. No counterpart under that name and none wanted. There is no web asset
here to format. The job it does, a formatter that refuses rather than advises, is
issue #26 for the language record 0001 chose.

`dependency-review`. Present today, same name.
`.github/workflows/dependency-review.yml` carries it, running on every pull
request.

## What this board needs that the target does not

Parity is not a ceiling. Nine checks below are reserved by issues here and have no
counterpart in the thirteen above, because they answer risks a media-server plugin
does not have.

`toolchain pin`, issue #27. A classification that has to reproduce in five years
cannot be built by whatever toolchain the runner happened to have that week.

The headless and unprivileged test contract, issue #28. A suite that quietly needs
a display or an elevation is a suite that passes on one machine.

`No network in the test suite`, issue #29. Record 0014 says the library makes no
network connection, and a decision with nothing refusing its violation is an
explanation rather than a rule.

`Decision records are well formed`, issue #31. Fourteen records are already landed
and the shape they follow is only real if something refuses a file that does not
follow it.

The determinism replay check, issue #32. Record 0012 requires a classification
record to be byte-identical between runs at different worker counts, which is a
property a compiled plugin has no equivalent of.

The schema validation check, issue #43, over `schema/record-1.schema.json`. The
target has no data catalogue, so it has nothing whose shape a schema would refuse.

The catalogue gate, issue #77. Every entry loads, classifies, and reproduces what
is stored. This is the check the whole board exists for, and it has no analogue
anywhere in the thirteen.

The coverage bar, issue #86, mutation testing, issue #88, fuzzing of the loader
and the expression parser, issue #90, and the property suite, issue #91. Issue #85
records that the target runs scheduled fuzzing, mutation testing and a
supply-chain scorecard beside its gate rather than inside it, and this board runs
a supply-chain scorecard the same way today, in
`.github/workflows/scorecard.yml`, on a schedule and not on a pull request.
Whether any of the four belongs inside the gate here rather than beside it is
decided in their own issues.

Every guard proved to bite, issue #95. Not a check over the tree but a check over
the checks, and it is the one that decides whether any of the names above is worth
anything.

## What none of this makes required

Requiring a check is a repository setting. This plan does not change repository
settings, and the empty list at the top of this document is the state today: five
guards run on a pull request here and not one of them stands behind a merge. A
reader who sees green ticks and concludes the merge was gated is wrong.

Which of these names becomes required, and whether signature verification joins
them, is entry 7 of the maintainer's question issue, #2, and it is open. Nothing
in this document decides it and nothing in this document should be read as
progress towards it: a board can reach thirteen green advisory checks and still
have a gate that refuses nothing.

## What is not covered by anything

Two of the thirteen have no holder here. `ABI floor build` has no counterpart and
no issue, for the reason given above, and the risk it stands in for is answered by
design rather than by a check. The static-analysis pair is held by #93 but nothing
has been evaluated on this route, so whether a counterpart exists at all is
unknown rather than decided.

This document is prose. Nothing reads it, nothing compares its list against either
ruleset, and a check name that changes on either board leaves it silently wrong.
The two commands at the top are the repair a reader can run in ten seconds, and
they are here for that reason rather than as decoration.
