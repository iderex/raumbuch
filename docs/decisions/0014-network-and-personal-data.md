# 0014. The network, and the personal data this project holds

## Status

Accepted

## Date

2026-08-08

## Question

Classifying a metric is arithmetic and a catalogue is a directory of files. So the
simplest possible network posture is available here, which is none at all, and the
reason to write that down is not that it is difficult. It is that every one of the
things that would break it gets added later by somebody who thinks it is obviously
helpful, and each of them arrives as a small convenience rather than as a change
of posture.

What does the software do with the network? What personal data does this project
actually hold, named rather than described as a category? Under what conditions
could federation ever exist? And what does the documentation an operator reads
have to say about all of it?

## Answer

### No network, and what that covers

The library and the command-line entry point make no network connection.

Specifically, and each item is here because it is a thing that gets added: no
telemetry, no usage counting, no crash report upload, no version check, no update
notification, no licence or entitlement check, no remote catalogue fetch, no
resolution of a citation or a DOI at run time, and no connection at import time.

Import time is called out because it is the one that surprises people. Loading the
library must not open a socket, resolve a name, or read a configuration file whose
purpose is to tell it where to connect. A first run does not differ from a second
run in this respect, because there is no first-run step.

A catalogue is a directory of files that is already on the host. Getting it there
is the operator's business and is done by whatever they already use to move files.
This project does not fetch it, and a path in a configuration file is a path on a
filesystem.

The test suite makes no network connection either, and that is the half a check
can refuse. Issue #29 is that check.

### What the default does not cover, said plainly

Two things reach the network in this project's life and neither is the software
running.

The build and the gate. Resolving a dependency, fetching a pinned action, and
querying an advisory database are network operations performed by a developer's
toolchain or by a workflow on a hosted runner. They are not performed by the
library, they do not happen on an operator's machine when they classify a metric,
and issue #27 is where the pinning and locking that bound them lives. An operator
who installs from a package index has made one network connection, to that index,
before anything in this project runs.

The documentation. A link in a document is a link a reader may follow, and a
citation with a DOI is a reference rather than a fetch. Nothing resolves either
on the reader's behalf.

Writing the boundary this way is deliberate. A statement that a project makes no
network connection, made in a tree whose own gate downloads an advisory database,
is the kind of overclaim a reader is right to stop trusting the rest of the
document over.

### The personal data, as a list

The personal data this project holds is small, real, and specific. Naming it is
the point; a category would not be a disclosure.

The names of the authors credited in a `citation` on a record, per record 0006.
That is what a citation is, and it is personal data about the people named
whether or not it is also a bibliographic reference.

Whatever a `locator`, a `note` or a `coverage_argument` field happens to carry.
These are prose fields. A note recording a disagreement with a source can name the
person disagreed with, and nothing refuses it, so the fields are on this list.

The names and email addresses in this repository's git history, from commits and
from the sign-off line the developer certificate of origin gate requires. That is
personal data the repository holds about contributors, and it is published because
a public repository is public.

The identity of whoever ran a verification is not held, and the negative statement
is the accurate one rather than the reassuring one. Record 0006's `recomputed`
entry names the command, the commit and the date, and record 0003's derived block
names the same three. Neither carries a person. The nearest thing to an identity a
derived entry exposes is the authorship of the commit it names, which lives in the
git history above and not in the record. If a future record adds a person to a
verification entry, that record extends this list, and this paragraph is what it
has to come back and change.

Whatever an operator's own files reveal about them: a filesystem path containing a
name, a machine name, a user account, the title of an unpublished metric they are
classifying. This project does not collect any of it and it appears wherever an
error message or a log line quotes a path, which is on the operator's own disk.
The reason it is on this list at all is that an operator who copies a log into a
public issue has published it, so the software keeps a path out of a message
wherever the message is as useful without it.

### Federation, if it is ever built

No federation exists today. Nothing in this tree connects to a peer, publishes a
record to anywhere, or knows the address of another catalogue.

If it is ever built, every one of these conditions holds, and a version that drops
one of them is not the thing this record permits.

It is opt-in and off by default. Off means there is no endpoint, not that the
endpoint is unreachable.

The endpoint is configured by the operator. No default address exists anywhere in
the tree, so a misconfiguration cannot silently reach a service this project
chose.

The fields that cross are named, individually, in the documentation and in the
code that sends them. A document saying that some data may be transmitted is not a
disclosure, and a field list that says "the record" is not a field list.

A dry run exists that prints exactly what would be sent, and it is what the
documentation tells an operator to run first.

It arrives with its own decision record, which supersedes or extends this one, and
with the paragraph below rewritten rather than quietly left in place. The
paragraph is what a reader trusts; leaving it standing beside a federation feature
would be the negative disclosure turned into a false one.

### The paragraph the documentation quotes

This paragraph is the text the `README`, the operator documentation in issue #99
and the data protection statement in it all carry. It is quoted from here and not
paraphrased, so that three documents cannot describe one posture three ways.

```
This software makes no network connection. It sends no telemetry, checks for no
updates, fetches no catalogue and contacts nothing at import time or on a first
run. A catalogue is a directory of files already on your machine, and
classifying a metric is arithmetic performed on it. The personal data this
project holds is what a record's citation and prose fields say about the people
credited in them, and what your own file paths and machine names reveal about
you if you copy a log somewhere public. None of it leaves your machine, because
nothing here transmits anything. Fetching dependencies when you install or
build the software is your package manager's connection and not this
software's.
```

The last sentence of that block is there because an operator who watches network
traffic during an install will see connections, and a paragraph that did not
mention them would be read as wrong about everything else.

### What is enforced and what is not

Issue #29 is the check that refuses a network call from the test suite. It runs the
suite with outbound access denied, or with the network interface the suite could
reach removed, so that an attempted connection fails the run rather than passing
quietly on a machine that happens to be offline. It owes the near miss the target
gate in issue #95 requires: a fixture that deliberately opens a connection and is
refused for that reason.

What that check covers is the test suite. What it does not cover is the library
itself in the hands of an operator, and the difference is real. A code path that
never executes under test can contain a connection the suite never reaches. So the
enforced statement is narrower than the paragraph above, and the gap is named here
rather than folded into a sentence about the project making no connections.

Nothing refuses a hard-coded address in the tree, nothing refuses a new dependency
that opens a socket, and no open issue holds either. The list of things reached at
build time is bounded by the pinning and locking in issue #27, which is a
different property from a network refusal and is not a substitute for one.

## Rejected alternatives

An opt-out telemetry signal, on by default, carrying nothing but a version and a
count. Rejected because a default-on transmission from a tool used inside
institutional networks makes the tool the operator's problem to justify, and
because the information it would return is not worth one conversation with a data
protection officer, let alone the number of them this would cause.

A version check on start-up, so that an operator learns their classifier is out of
date. Rejected because it is a network connection on every run for information a
package manager already provides, and because an out-of-date classifier producing
a stored derived value is exactly what record 0006's staleness anchors detect
without anyone being told anything.

Resolving a DOI or a citation at run time to validate a provenance field. Rejected
because it turns loading a catalogue into a set of outbound requests whose failure
mode is a record that cannot be loaded on a machine with no route out, and because
what it would check is that a DOI resolves rather than that a metric came from
where the record says.

Fetching a catalogue from a remote location when it is missing locally. Rejected
because a catalogue arriving over the network is a catalogue whose provenance is
the connection rather than the file, and because the operator already has a way to
move files that they trust more than this one.

Uploading a crash report. Rejected because a crash report from this software would
carry the metric being classified, which may be unpublished work, along with paths
and machine names. The alternative is a report written to a local file the operator
may choose to attach to an issue, and that is what the software does.

Federation on by default with an opt-out. Rejected because a federation nobody
chose is a publication nobody chose. The condition list above is what opt-in
means here.

Describing the personal data as a category, for instance as bibliographic metadata
and diagnostic information. Rejected because a category cannot be checked against
the fields that exist, and because the two entries a reader would not have guessed
are a prose field naming a person and the git history, neither of which is
bibliographic or diagnostic.

Saying that this project makes no network connection at all, with no mention of
the build. Rejected as an overclaim. It is also the more impressive sentence,
which is the reason to be suspicious of it.

Writing the disclosure once in the operator documentation and letting the `README`
link to it. Rejected for the same reason record 0007 rejects it: a reader who does
not follow a link has not been told, and the cost of the alternative is one
paragraph quoted twice with this record as the source.

## What depends on this

Record 0003 and record 0006, whose `citation`, `locator`, `note` and provenance
fields are what carries the personal data named above, and whose derived and
verification entries are named here as carrying no person.

Record 0005, whose `coverage_argument` is a prose field on the same list.

Issue #29, the check that refuses a network call from the test suite, which owes
the fixture that proves it bites.

Issue #27, the pinned toolchain and locked dependencies, which bounds what the
build reaches and is not a network refusal.

Issue #96, the packaging and the command-line entry point, which is where the
no-connection-at-import property is first testable against a real installed
artefact.

Issue #99, the operator documentation and the data protection statement, which
carries the quoted paragraph verbatim and is where the `README` copy is made.

Issue #95, every guard proved to bite, which covers the near miss issue #29 owes.

Any future federation, which needs its own decision record, the conditions listed
above, and a rewrite of the quoted paragraph rather than a quiet exception to it.
