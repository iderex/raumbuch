# 0006. Provenance and verification

## Status

Accepted

## Date

2026-08-07

## Question

The complaint this board answers is that the reference is a book. A catalogue
that copies the book and does not say that it copied the book has not improved
anything; it has made the same claims faster. So a record has to carry where the
metric came from and what has actually been done to it.

What provenance fields does a record carry, what words describe what verification
has happened, which of those states may be published, and what does a record do
when a verification goes stale because the code changed under it?

## Answer

### Provenance

Provenance is a block on the record, and its fields are these and no others.

`source_kind`, one of `primary`, `secondary` or `derived_here`. A primary source
is the publication the solution first appeared in. A secondary source is a
compilation, a review or a textbook. `derived_here` means the metric was
obtained by a computation in this repository rather than transcribed, which is
rare and needs the computation named.

`citation`, the full bibliographic reference of the source.

`locator`, where inside the source the metric is: page, equation or section. A
citation with no locator sends the next reader to a book rather than to a line,
and the next reader is usually somebody checking a transcription.

`doi` and `url`, optional, and present where they exist.

`transcribed_on`, one date.

`note`, prose, for anything the fields above cannot carry, including a difference
between what the source printed and what the record holds.

What may be transcribed from what is a policy question and it is open. It is
entry 3 in the maintainer's question issue, #2, and this record does not decide
it. What this record fixes is that the answer is recorded per entry in
`source_kind` and `citation`, so that whichever policy is chosen can be checked
against the catalogue afterwards instead of being asserted about it.

### The verification states

Four words for four different epistemic positions. Collapsing any two of them is
the defect.

`transcribed` means the value was written down from a source and nothing here has
checked it.

`checked_against_publication` means the value was compared against a published
result, and the entry names the publication and where in it.

`recomputed` means a command in this repository produced the value, and the entry
names the command, the commit it ran at and the date.

`cross_checked` means an independent implementation agreed, and the entry names
that implementation and its version.

The vocabulary is closed. A fifth word is added by amending this record, not by
writing one into a file.

An unverified record is legitimate. Most entries will start at `transcribed` and
stay there for a while, and forcing a state onto them that the work does not
support is how a catalogue becomes untrustworthy in a way nobody can audit later.
What is not legitimate is an unverified record that a consumer cannot tell apart
from a verified one, and the marker below is what separates them.

### Verification is per claim, not per record

A record does not have a verification state. Each value does.

A record carries a list of verification entries. Each names its subject, which is
one derived field together with the stratum and chart it holds on, its state, and
the evidence that state requires. The evidence is not optional and the loader
refuses an entry whose state and evidence do not match: a `recomputed` entry with
no command, a `checked_against_publication` entry with no publication, a
`cross_checked` entry with no implementation named.

A record whose Petrov type is recomputed and whose Killing vector count is still
transcribed is a normal record and a common one. One state for the whole record
would have to be the weakest of them, which throws away the work that was done,
or the strongest, which is a lie.

The field equations are a subject like any other. Whether the metric actually
solves what the record claims is the derived field `field_equations_hold`,
issue #50, and it carries its own verification entry.

### Cost belongs to the verification entry

A `recomputed` entry carries the cost of the run that produced it: peak memory,
wall clock and the differentiation order reached. Cost sits here rather than on
the record because it is a property of a run, not of a solution, and because two
recomputations at different commits will differ. Record 0011, issue #20, fixes
what a cost report contains, and this record only fixes where it is stored.

### Staleness is computed, not stored

A `recomputed` entry carries two anchors beyond its command and date. A digest
over the asserted part of the record as it stood when the command ran, and a
digest over the source that produced the value.

The loader marks an entry stale when either digest fails to match the tree the
record is loaded in. The record stores no stale flag.

The reason is that a flag would have to be set by hand, by the person whose
change made it stale, at the moment they are least likely to notice. Anchors
cannot be forgotten because they are written by the command that made the entry,
and the comparison happens on every load.

The manifest that says which source paths produce which derived field is what the
second digest is taken over. It does not exist yet and it is owed before the
first `recomputed` entry lands; issue #77 is where it belongs, since the
catalogue gate needs the same mapping to know what to rerun. Until it exists no
`recomputed` entry can be written, because there is nothing for the anchor to
digest.

Stale is not a fifth state. It is a property of an entry in a tree, and the same
entry is fresh in the tree it was written in and stale in a later one. Writing it
as a state would make the vocabulary depend on when it was read.

### What the catalogue gate publishes

The gate in issue #77 refuses no verification state. All four publish.

It refuses three things, none of which is a state. A derived value carrying no
verification entry, because that is a value from nowhere. A `recomputed` entry
that does not reproduce when the command is rerun at the commit under test,
because that is the mismatch the gate exists to find. And a verification entry
whose evidence does not match its state, which the loader already refuses and the
gate refuses again because a catalogue can be published from a tree the loader
was not run over.

Two states publish with a visible marker, and the marker says the same thing in
both cases: no computation in this repository has confirmed this value.
`transcribed` and `checked_against_publication` carry it. A stale `recomputed`
entry carries a marker of its own saying the value was computed and the thing it
was computed from has since changed.

The marker is part of the published artefact, not a footnote in the
documentation. A consumer reading a Petrov type gets the state with it or does
not get the value.

## Rejected alternatives

One verification state per record. Rejected above: the weakest-of-all rule
discards real work and the strongest-of-all rule is false. Records will routinely
be part recomputed and part transcribed for a long time.

A boolean `verified` field. Rejected because it collapses all four positions into
one and the collapse is not recoverable afterwards. A record that says `verified
= true` cannot be asked whether that meant a book was consulted or a command was
run.

Free text for the source and the verification. Rejected because a closed
vocabulary is what makes a query over the catalogue possible at all, and because
free text is where "checked" and "checked (roughly)" both appear and neither can
be counted.

Refusing to publish anything below `recomputed`. Rejected because it would empty
the catalogue for as long as the classifier is unfinished, and because it creates
the incentive this whole record is built against: a person with a book, a
deadline and a field that refuses to publish the truth will write something else
in it.

A stored `stale` flag, cleared by whoever reruns the verification. Rejected in
the paragraph above. The person who invalidates a verification is changing the
code, not reading the record, and asking them to walk the catalogue clearing
flags is asking for the flag to be wrong.

Storing the cost on the record rather than on the verification entry. Rejected
because cost is a property of a run and a record can carry several runs at
different commits.

## What depends on this

Record 0003, whose provenance block and derived block are specified here, and
whose claimed block exists because `transcribed` is a legitimate state.

Issue #35 and issue #36, the schema and the loader, which carry the refusals:
evidence not matching state, a derived value with no verification entry, a
`source_kind` outside the closed vocabulary.

Issue #38, the fixture corpus, which needs one refused record per reason above.

Issue #50, the field equation check, whose result is a subject here.

Issue #67 and record 0011, issue #20, which fix what a cost report holds.

Issue #77, the catalogue gate, which owes the source path manifest the second
digest is taken over, and which implements the three refusals and the two
markers.

Issue #79, the coverage report, which is a count over these states and is
meaningless if the vocabulary is not closed.

The maintainer's entry 3 in issue #2, on what entries may be transcribed from.
That answer changes which `source_kind` values the project's own policy admits.
It does not change the field set here, which is why this record could be written
before it.
