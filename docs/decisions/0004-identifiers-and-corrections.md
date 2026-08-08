# 0004. Identifiers and corrections

## Status

Accepted

## Date

2026-08-08

## Question

A catalogue is useful when somebody can cite a row and get the same row back
later, and it is honest when a row that turns out to be wrong can be corrected.
Those two pull against each other. A citation wants an identifier that never
moves; a correction wants the corrected value to reach whoever is relying on the
old one.

What identifies an entry? What happens when two branches add an entry
independently, in terms concrete enough that a check can refuse the collision
rather than a reader noticing it? What does a consumer see when a record it
depends on has been corrected, and what does it see when the record has been
superseded by a different one?

Record 0003 already put `id` and `version` in the asserted block and left their
meaning here. Record 0005 noted that superseding a record which holds a family is
coarser than superseding one geometry, and left that here too. Entry 10 of the
maintainer's question issue, #2, is whether an entry may ever be removed rather
than only superseded, and it is open, so this record is written to survive either
answer.

## Answer

### The identifier is a pair

An entry is identified by `id` together with `version`.

`id` is a slug: one or more groups of lowercase letters and digits, separated by
single hyphens, matching `^[a-z0-9]+(-[a-z0-9]+)*$`. It is assigned once, it is
never reused for a different entry, and it is never renumbered or renamed. It is
the primary key of the catalogue and the thing a citation names.

`version` is an integer, starting at 1, which increases by one every time the
content it covers changes. It is what a citation adds when the citer wants to be
told that the thing they cited has moved.

The slug is chosen to be readable, and readability is a convenience rather than a
guarantee. Record 0003 already carries `name` and `aliases` for the human names,
which is where the fact that several metrics are reasonably called Kerr-like is
absorbed. The slug is unique because a check refuses a second record carrying it,
not because the world provides unique names.

### One record, one file, and the filename is the id

A record lives at `catalogue/<id>.toml` and its `id` field equals the filename
stem. That is one rule and it buys three things.

Two branches adding two different solutions never collide, because they write two
different paths and no allocator is consulted. This is the whole reason a
sequential number was not taken.

Two branches adding the same solution collide loudly, as an add/add conflict on
one path in git, before anything is merged. That is the direction a collision
should fail in: two people transcribing Kerr in parallel should find out, and the
tool that tells them is the one they are already using.

A duplicate is decidable from the tree alone. A checker walking `catalogue/` and
finding two records with one `id`, or a record whose `id` and filename disagree,
refuses without needing history, a network call or a previous release.

### What a version covers, and what it does not

A version covers the asserted block and the claimed block of record 0003, and
nothing else.

It does not cover the derived block or the verification entries. Those are
machine-written, they carry their own command, commit and date under record 0006,
and a recomputation that reproduces the same value is not a correction of
anything. If a version moved on every gate run, a pinned citation would go stale
for reasons that have nothing to do with the entry, and the signal this record
exists to send would be lost inside the noise.

This is deliberately a different subset from record 0006's staleness anchor,
which digests the asserted part only. The two are different questions. Staleness
asks whether a computed value still follows from what it was computed from, so it
looks at the input to the computation. A version asks whether what a person
asserted or claimed about this entry has changed, and a claimed Petrov type read
from a book is exactly the kind of thing that gets corrected without any
computation being invalidated.

Record 0005's case lands here. A record holds a family, so a correction to one
stratum is a correction to the record and bumps the whole record's version.
Nothing finer is available, because the citable object is the entry and the strata
are structure inside it. The cost is that a consumer pinned to version 3 and
looking at version 4 has to read the correction entry to find out whether the
change touched the stratum they care about, which is why the correction entry
below names what it affects.

### The correction list

Every version above 1 adds one entry to a list named `correction` on the record.
An entry carries the version it produced, the date, one sentence saying what was
wrong, and the strata and fields it affects. The list is append-only: an entry is
never edited and never removed, and the list read from top to bottom is the
history of the entry as far as anyone has found it.

The list is on the record rather than in the git history because a consumer holds
a catalogue and not a checkout. A history that is only reachable by cloning the
repository is not available to the thing that has to tell a caller their pinned
version has moved.

Only the current version of a record is on disk. Older versions are recoverable
from git history and the catalogue does not carry them, because a catalogue
holding every version of every entry answers the question "what is known about
this spacetime" with a pile of things that were once believed. The correction
list is what stands in for the old copy: it says what changed and why, which is
what a consumer needs, and it does not pretend the superseded value is still a
value anyone should use.

### Superseding is the id-level path, and it is a different event

A correction keeps the id and moves the version. Superseding replaces the id.

Superseding is for the case where the identity was wrong rather than the content.
Two entries turn out to be one geometry, one entry turns out to be two, or a slug
names something the entry is not. The new record carries `supersedes`, a list of
the ids it replaces, and each replaced record carries `superseded_by` naming the
new id. The link is written from both ends, for the reason record 0000 gives
about superseded decision records: a reader arriving at the old id has to be sent
forward, and a reader arriving at the new one has to know what it displaced.

A superseded record keeps its file, its id and its content. Its version does not
move, because nothing about what it asserts has changed; what changed is that it
is no longer the entry to use.

### The release index, and why the identifier survives entry 10

A published catalogue carries an index listing every id it holds, with the
current version of each and one of three states: `current`, `superseded_by <id>`
or `withdrawn`.

The index is what makes the scheme survive either answer to entry 10 of the
maintainer's question issue.

If entries are never removed, a withdrawn entry keeps its file and its row, its
state is `withdrawn`, and the reason sits in the correction list as the entry
that produced its last version.

If entries may be removed, the row stays in the index with the state `withdrawn`,
the date and the reason, and only the file goes. The id is still spent and is
still never reused.

Either way an id that was ever published stays in the index forever, and a
consumer pinned to an id that is no longer loadable is told which of the two
happened rather than receiving a missing entry. A missing entry and a withdrawn
one look identical to a caller that gets nothing back, and they are opposite
statements: one is a catalogue that never had it and one is a catalogue that took
it away.

### What a consumer sees

A consumer pins whatever it is willing to be told about. Pinning nothing is
allowed and gets no report.

Pinned to `(id, version)`, and the catalogue holds that id at that version. The
load is silent. This is the case that has to stay quiet, because a consumer that
gets a report every time will stop reading them.

Pinned to `(id, version)`, and the catalogue holds a higher version. The load
succeeds against the current record and reports that the entry was corrected,
naming the pinned version, the current version, and every correction entry
between them. The consumer receives the current record and not the pinned one.
Silently serving an old version would mean a catalogue that answers differently
depending on what the caller once wrote down, and that is a catalogue with no
single state.

Pinned to an id whose record carries `superseded_by`. The load succeeds, the
record loaded is the superseded one, and the report names the successor id.
Nothing is redirected automatically, because a supersession says the identity was
wrong and following it silently would answer a question about one entry with a
different entry.

Pinned to an id whose index row says `withdrawn`. The load refuses, naming the id,
the date and the reason. This is a refusal rather than an empty result for the
reason in the section above.

Pinned to an id absent from the index entirely. The load refuses, naming the id,
and says the identifier is unknown to this release rather than saying it was
removed. Those are different sentences and the index is what tells them apart.

How this reaches the caller of `is_this_new` is record 0008, issue #15. What this
record fixes is what a consumer is told and when; where in the returned value it
appears is not settled here.

### The refusals this record creates

Written out so issue #41 and issue #43 have a list rather than a paraphrase, and
split by what each one needs in order to be decided.

Decidable from the tree alone, so they belong to the loader and to the schema
check:

Two records under `catalogue/` carrying the same `id`.

A record whose `id` does not equal its filename stem.

An `id` that does not match the grammar above.

A `supersedes` or `superseded_by` naming an id that is not in the index.

A `superseded_by` on a record where the named successor does not carry the
matching `supersedes`, or the reverse. The link is written from both ends and a
half-written link is refused rather than repaired.

A `version` below 1, or a `correction` list whose entries do not run from 2 up to
the record's current version with no gaps and no repeats.

Decidable only against a previous state, so they belong to the catalogue gate in
issue #77 rather than to the loader:

A landed `(id, version)` whose asserted or claimed content differs from what it
was when that version landed. This is the rule that makes a version a citation
anchor rather than a label, and it is refusable by comparing the record against
the merge base. The cost is that this check reads history and therefore cannot
run against a bare directory of records.

A `version` that decreased against the merge base.

An id present in the previous release's index and absent from this one's.

Nothing refuses any of these today, because there is no code and no catalogue in
this repository yet. The list is what those issues owe, not a description of
something that runs.

## Rejected alternatives

A sequential number. Short and citable, and it needs an allocator, so two
branches adding an entry on the same day both take the next number and the
collision is silent until a merge. The usual repairs are a central allocator,
which is a coordination point on the one action the catalogue most wants to be
parallel, or renumbering on merge, which breaks the citation the number existed
to provide. Rejected for the collision behaviour, which is the property the issue
asks this record to make concrete.

A content hash of the canonical record. Collision-free with no coordination,
which is genuinely the best answer to the question the sequential number fails.
Rejected because it changes when a typo in a comment is fixed, so every citation
that ever pointed at the entry breaks on a change with no meaning, and the
project would immediately grow a second stable identifier to cite instead. A
scheme whose first consequence is a second scheme is not the scheme.

A hash of the classification output rather than of the record. Stable under
cosmetic edits, which repairs the objection above, and unstable under exactly the
corrections that matter. Rejected because it is the wrong way round twice over: a
corrected metric that classifies the same keeps its identifier while a
recomputation that finds the old classification wrong changes it, so the
identifier moves when the code changes and holds still when the physics does. It
also cannot exist before the classifier does, and record 0003 requires an id on
the first record written.

A human-readable name as the identifier. Pleasant, and not unique. Rejected as
the identifier and kept as `name` and `aliases` in record 0003, which is where
the several reasonable names for one metric go. The slug above is not this
alternative: it is unique because a check refuses a duplicate, and it is readable
as a convenience that carries no promise.

A slug with no version, corrections landing in place. Rejected because a citation
would then name a moving target and there would be no way to ask whether the
entry has changed since it was cited, which is half of what the issue asks for.

A version that also covers the derived block. Rejected in the section above: it
would move on every recomputation and the signal would be worthless.

Keeping every version of every record on disk. Rejected because the catalogue is
the current state of knowledge and a directory holding four versions of
Schwarzschild invites a consumer to load the wrong one. The correction list plus
git history covers what an old copy would have been read for.

Redirecting a pinned id automatically to its successor. Rejected because
supersession is the case where the identity was wrong, so a silent redirect
answers a question about one entry with a different entry, and the consumer never
learns that the thing they cited was not what they thought.

Deciding entry 10 of the maintainer's question issue here, in the direction of
never removing anything. Rejected because it is not this record's to decide, and
because the index above makes the identifier scheme work under either answer, so
the decision does not have to be forced to unblock this one.

## What depends on this

Record 0003, whose `id` and `version` fields are specified here and whose
`correction` list this record adds to the asserted block.

Record 0005, whose family and stratum machinery is what the granularity paragraph
above is about, and which named this record as the place that answers it.

Record 0006, whose staleness anchor digests a different subset of the record for a
different question, and whose verification entries are outside what a version
covers.

Record 0008, issue #15, which fixes where a correction report and a supersession
report appear in the value a caller of `is_this_new` receives.

Record 0013, which lists the identifier and the correction path as part of the
envelope shared with `findbuch`, so this record is written naming no spacetime and
is one of the documents a second implementation would be built from.

Issue #35 and issue #36, the schema and the loader, which carry the refusals in
the first list above.

Issue #41, the identifier and the correction path implemented, which is this
record turned into code.

Issue #43 and issue #77, the schema validation check and the catalogue gate,
which carry the refusals in the second list and are the only place they can run.

Issue #73 and issue #74, the first entries, which are the first ids spent.

Issue #82, the interface another project may depend on, since a pinned
`(id, version)` is part of what is promised to a consumer.

Entry 10 of the maintainer's question issue, #2, which this record does not
decide and does not wait for.
