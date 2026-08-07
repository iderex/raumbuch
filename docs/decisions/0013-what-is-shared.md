# 0013. What is shared with findbuch, and where the boundary runs

## Status

Accepted

## Date

2026-08-07

## Question

`findbuch` is the catalogue of integrable cases in rigid body dynamics.
Structurally it is this project: a set of exactly known objects, each transcribed
from literature, each needing provenance, each verified by a computation rather
than by trust, each loaded by something that refuses a malformed record, each
held honest by a gate that reruns the verification.

What is common to both boards, what is not, and what is the interface between the
common part and the mathematics of this one? The cheapest moment to answer is
before either board has a verified-catalogue framework, which is now.

## Answer

Where the shared part lives is not decided here. Whether it becomes a third
repository, a dependency from one board to the other, or a duplicate held in step
by a compatibility test is entry 6 of the maintainer's question issue, #2, and it
is open. This record fixes the boundary and the interface, both written so they
survive all three answers, and the last section says what each answer changes.

### Shared, by named component

The record envelope. The identifier and its version, the schema version, the
provenance block, the verification entry shape and its closed vocabulary of
states, the staleness anchors, and the correction path. Records 0004, issue #9,
and 0006 are where these are specified for this board, and they are specified in
terms that name no spacetime.

The loader's refusal vocabulary. Not just the fact that a loader refuses, but the
names and the sentences. "This record was refused because a derived field was
asserted by hand" should be the same sentence on both boards, because a consumer
reading two catalogues should not have to learn two vocabularies for one failure.

The cost budget and the refusal report. Both boards run computations that can
exceed a machine, and both would otherwise be killed by the operating system with
nothing to show. Record 0011, issue #20, holds this board's half.

The catalogue gate procedure. Load every record, rerun each verification, compare
against what is stored, refuse a mismatch, apply the published markers to the
states that carry them. Issue #77 is this board's instance.

The release shape. What a published catalogue is as an artefact, how it is
versioned, and what a consumer receives.

### Not shared

Everything about the mathematics.

The tensor layer. The frame formalism and the conventions, record 0002, issue #7.
The curvature computation. The Petrov and Ricci classifications. The
Cartan-Karlhede algorithm and its bookkeeping. The notion of equivalence, record
0007, issue #13. `is_this_new` itself. The verification that a metric solves the
field equations it claims, issue #50. There is no shared tensor layer, no shared
verification and no shared notion of equivalence, and there is no plausible
version of this project in which there is.

The expression sub-language is on the boundary and lands on the unshared side
with one exception. Its grammar and its closed function list are this board's,
because a metric component and an integral of motion do not admit the same
functions. What is shared is the requirement placed on any payload: the values
are parsed into a syntax tree by a closed grammar and loading executes nothing.
That is a property the envelope demands of a payload validator, not a parser the
envelope supplies.

### The interface

The envelope treats the payload as opaque. It parses the file, validates the
envelope fields, and hands the payload to a board-supplied validator identified
by the record's `domain` field. The envelope never parses a metric and never
learns what a Petrov type is.

Three things a board supplies.

A payload validator, which takes the parsed payload and returns refusals
expressed in the shared vocabulary.

A subject list, which takes a record and names what is derivable from it. On this
board that list is the derived fields in record 0003.

A recompute function, which takes a record and one subject and returns a value
and a cost, and which is given a budget handle it must respect.

Two things a board never does. It does not implement provenance, verification
states, staleness or the gate loop, because a second implementation of those is a
second set of rules for what an unverified record means. And it does not write
into the envelope's blocks except through the recompute path, which is what keeps
the derived block machine-written.

The interface is small on purpose. Every function on it that grows a spacetime
shaped argument is the boundary leaking, and the test is that nothing in the
envelope's own suite mentions a metric.

### What each answer to the maintainer's question changes here

A third repository both boards depend on. This board takes a versioned dependency
on it, and the interface above becomes that package's public API with the three
hooks as its extension points. The envelope's schema version turns into an
external compatibility surface, so widening the provenance field set stops being
a commit here and becomes a release there followed by a bump here. This board's
gate runs the shared gate loop and supplies only the recompute hook. The cost is
a third repository to maintain, release and secure, and a release here that waits
on a release there whenever the envelope moves.

One board depends on the other. The envelope lives in one of the two trees and
the other imports it. The interface is unchanged, and the coupling widens from a
small shared surface to the whole of the other board's tree, since a dependency
on a repository is a dependency on its toolchain, its suite and its release
cadence. A refactor in rigid body dynamics then reds the gate on a spacetime
catalogue for a reason that has nothing to do with either, which is the outage
the maintainer's question is weighing. Nothing about this board's mathematics
changes; what changes is what can break it.

Duplicated, held in step by a compatibility test. The envelope is implemented
twice and the interface above becomes a written specification plus a shared
fixture corpus, which is issue #83 on this board. Nothing couples at build time
and neither board can break the other. Drift is then caught by fixtures rather
than by a compiler, which means it is caught later and only where a fixture
exists, so the fixture corpus has to cover every refusal in the shared vocabulary
rather than the common ones. Under this answer, records 0003, 0004 and 0006 plus
this one are the specification, and they have to be written so a second
implementation could be built from them alone.

One thing narrows two of those three answers, and it is not decided either.
Record 0001, issue #5, chooses the language and toolchain for this board.
`findbuch` chooses its own. If the two differ, a shared package is not available
in the form the first two answers describe, and what can actually cross the
boundary is the file format, the vocabulary and the fixture corpus rather than
code. That reduces the first two answers to the third in practice, and it is
worth knowing before the third repository is created rather than after.

## Rejected alternatives

Share the mathematics too, behind a general "verified scientific object"
abstraction. Rejected because there is nothing to share. A metric and an
integrable case have no common structure below the level of the envelope, and an
abstraction over two unrelated things is an abstraction that has to be widened
for the third.

Share nothing, and let each board build its own envelope. Rejected because both
boards then invent a verification vocabulary, and two vocabularies for the same
four epistemic positions is the defect record 0006 exists to prevent, arriving
one repository over.

Make the envelope generic by giving it a plugin system with hooks for everything.
Rejected because the interface's smallness is its whole value. Three functions
that a reader can hold in their head is a boundary; a plugin surface is a second
program with its own failure modes.

Put the payload in a separate file from the envelope. Rejected because a record
split across two files can be half copied, and because the provenance of a metric
belongs beside the metric.

Decide entry 6 here, in the direction of a third repository, on the grounds that
it is the cleanest boundary. Rejected because creating a repository is not
something this plan does, and because the language question above can make that
answer unavailable. The boundary is what this record owed, and it is decided.

## What depends on this

Record 0003, record 0004 issue #9, and record 0006, which together are the
envelope this record calls shared, and which under the third answer become the
specification a second implementation is built from.

Issue #81, extracting the shared record envelope and the refusal vocabulary,
which is this record turned into code and is where the boundary is first tested.

Issue #82, the interface another project may depend on and what is promised about
it, which is the three hooks above given a stability promise.

Issue #83, the compatibility test against the sibling catalogue's records, which
is load-bearing under the third answer and a nicety under the first two.

Record 0011, issue #20, the cost budget and the refusal report, which is listed
as shared and therefore has to be written without a spacetime in it.

The maintainer's entry 6 in issue #2. This record does not decide it and does not
depend on the answer; what depends on the answer is only where the code lives and
what a break in it costs, which is the last section above.
