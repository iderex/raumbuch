# 0015. Where records 0003, 0005 and 0006 disagreed

## Status

Accepted

## Date

2026-08-08

## Question

Records 0003, 0005 and 0006 each leave part of the solution record to the others.
Record 0003 fixes the three blocks, the file format and the expression
sub-language, and delegates the parameter, stratum and chart blocks to record
0005 and the provenance block to record 0006. Read separately they agree. Read as
one field list, which is what writing `schema/record-1.schema.json` required,
they disagree in four places.

Three of the four are fields a later record requires and the worked Schwarzschild
record in record 0003 does not carry. The fourth is two records naming different
homes for one field.

Record 0005 says a record carries a `coverage_argument` field saying in prose why
the declared strata cover the declared range. The worked record has one stratum
and no `coverage_argument`.

Record 0005 says every derived field and every claimed field attaches to a
stratum, and that nothing attaches to the family as a whole. The worked record's
claimed block attaches to no stratum.

Record 0006 lists the provenance fields and says these and no others, marking
`doi` and `url` optional and nothing else. The worked record's provenance carries
no `locator`, which is the field record 0006 argues hardest for.

Record 0003 lists `cost` among the derived fields and says each derived entry
carries the cost of the run. Record 0006 stores the cost on the verification
entry instead, because cost is a property of a run and a record can carry several
runs at different commits.

The schema was required to validate the worked record, so in all four places it
permitted and did not require, and carried the gap in a `$comment` and in
`docs/record-format.md`. That is a schema knowingly weaker than the records it
encodes, and a reader who trusts it concludes that a record with no locator is a
complete record.

What does each of the four resolve to, and where a landed record is wrong in one
line, is it corrected or superseded?

## Answer

### The four resolve the same way, and it is not a coincidence

In each of the four, record 0003 is the outlier and the record that argued the
point is 0005 or 0006. They are not all the same kind of disagreement, and
sorting them is what decides how record 0003 is repaired.

Two of the four are a silence in record 0003's worked example rather than a
position it took. Record 0003 delegates the stratum block to record 0005 and the
provenance block to record 0006 in its own text, so an example carrying neither a
`coverage_argument` nor a `locator` was incomplete against a delegation record
0003 made itself. Completing the example decides nothing.

The other two are collisions between two answers. Record 0003 gives the claimed
block a shape, a table of field names each carrying its source, and record 0005
requires every claimed value to attach to a stratum, which that shape cannot
carry for a record with more than one. Record 0003 puts the cost of a run on the
derived entry and record 0006 puts it on the verification entry. In both, record
0003 states its answer and the later record argues for its own, and record 0006
lists record 0003's position among the alternatives it rejected.

### `coverage_argument` is required of every record

Record 0005 makes the coverage of the declared range by the declared strata an
assertion rather than a check, and says plainly why: deciding it means deciding
conditions over the expressions a record is allowed to write, which record 0009
does not promise. The prose field is therefore the only thing standing between a
stratum list and a gap in it that nothing sees. A field that is the sole defence
against a failure and is also optional is not a defence.

It is required of a record with one stratum too. There the argument is one
sentence, and the sentence is still the thing a reader checks: that the generic
stratum's condition is the declared range and not a narrower expression that
happens to look like it. A conditional requirement would exempt exactly the
records nobody reads twice.

### A claimed value attaches to a stratum, and the block becomes a list to carry it

The direction is record 0005's. Nothing attaches to the family as a whole,
because a classification valid on the generic subset and silently wrong on a
special locus is worse than no classification, and the way to make that
unwritable is to remove the place it would be written.

The shape that carries it is the part worth arguing. The claimed block as it
stood was a table of field names with one `source` key beside them. Adding one
`stratum` key to that table attaches every claimed value in the record to one
stratum. That is enough for Schwarzschild and it cannot carry record 0005's own
worked Kerr entry, where the claimed isometry dimension is 4 on the `a = 0`
stratum and 2 on the generic one. Record 0005 describes that entry as having a
claimed block whose keys are written per stratum. So the cheapest edit satisfies
the letter for the first entry in the catalogue and breaks on the second.

The claimed block is a list of entries instead, one per claimed value, each
naming the `field`, the `value`, the `stratum` it holds on and the `source` it
was read from. That is the derived block's shape, which is what record 0003 says
the two blocks are to each other: the same keys, differing in who wrote them and
in what stands behind them.

The per-entry `source` follows from the shape rather than being a fifth
resolution. Record 0003 already says a claimed field carries the source it was
read from, per key. One shared `source` key was the old block shape making that
unwritable, and a record reading two Petrov types out of two papers had nowhere
to say so.

### `locator` is required

Record 0006 lists the provenance fields as these and no others and marks exactly
two of them optional, `doi` and `url`. It also gives the reason the locator is
not one of them: a citation with no locator sends the next reader to a book
rather than to a line, and the next reader is usually somebody checking a
transcription, which is the reader this catalogue is built for.

`note` stays optional and this record says so rather than leaving it to be read
off the schema. Record 0006 defines it as prose for what the other fields cannot
carry, including a difference between what the source printed and what the record
holds. Most records have no such difference, and a required field with nothing to
say is filled with filler.

The worked record's provenance values are a placeholder until the first catalogue
entry lands under issue #73, and the record says so in a comment. It gains a
placeholder locator, so that what is deferred is the whole block rather than the
block minus one field nobody notices.

### The cost of a run is stored on the verification entry and nowhere else

Record 0006 is the record in force. Two things put it there.

It argued the point and record 0003 did not. Record 0006 gives the reason, that
cost is a property of a run rather than of a solution, and it lists storing the
cost on the record among its rejected alternatives, so it met record 0003's
position and refused it in writing.

The reason holds independently of which record said it first. The derived block
carries one entry per field per stratum per chart, and a record can carry several
runs of one command at different commits. A cost on the derived entry therefore
has to be either the last run's or an arbitrary one of them, and neither is a
thing a consumer can read.

Two consequences follow. A derived entry carries no `cost`, and the schema
refuses one. And `cost` leaves the closed list of derived field names, because it
is not a property of the geometry that a command computes. That list is also
where a verification entry draws its subject from, and a verification entry whose
subject is the cost of a run is not a claim about anything.

What a cost report holds is still record 0011, issue #20, and it has not landed.
The `cost` shape in the schema stays open for that reason, which is a separate
looseness from the four this record closes and is disclosed on its own.

### Record 0003 is corrected in place, not superseded

Record 0000 has one mechanism for a record that no longer says the right thing.
The old record's status becomes `Superseded by NNNN`, its date moves, and a new
record carries `## Supersedes` naming it.

That is the wrong instrument here. Record 0003 fixes the three-block separation,
the file format, the expression sub-language and the worked example, and one row
of one table in it is wrong. Superseding it would put a pointer at the top of all
of that saying the decision was displaced, and send the reader forward to a
record that repeats everything that did not move in order to change what did.

So record 0003 keeps its number, its title, its status and its text, and each of
the two collisions is corrected where it sits, under a heading saying what it is,
with what was wrong and how it was found. Its worked example moves with them,
because an example that no reader can validate is worse than no example, and the
two silences are filled in the same pass.

Record 0000 describes no state between an untouched record and a superseded one,
and this record uses one. Issue #110 holds whether record 0000 gains a shape for
a correction or states that supersession is the only route and a record wrong in
one line is superseded in full.

## Rejected alternatives

Resolve the three absent fields the other way, making them optional and editing
records 0005 and 0006 to say optional. Rejected because it decides all three in
favour of the document with no argument in it. Record 0005 and record 0006 each
carry a paragraph saying what a reader loses without the field. On the other side
is a worked example's silence, and silence in an example is the weakest evidence
in the tree about what a format requires.

Leave the schema loose and keep carrying the disclosure. This is the state this
record ends. Rejected because a disclosure is what is written while a gap is
open, not instead of closing one, and it protects only the reader who reaches
`docs/record-format.md` before writing a record.

Supersede record 0003 with a full replacement. Rejected in the answer above. It
duplicates a long record to move one table row, and record 0000's reason for
supersession is that a reader has to be sent forward from a decision that was
displaced. Nothing here displaces that decision.

Keep the claimed block a table and add one `stratum` key beside `source`. The
smallest edit that closes the second disagreement, and rejected in the answer
above: it cannot express record 0005's own worked Kerr entry, so it would be
undone by the second entry the catalogue gains.

Store the cost in both places, on the derived entry for the run that produced the
value and on the verification entry for the run that confirmed it. Rejected
because two homes is the defect being closed, and a consumer reading a cost would
have to know which of the two the writer used before the number meant anything.

Require `coverage_argument` only where a record declares more than one stratum.
Rejected in the answer above. The field is an assertion a reader checks, and a
conditional requirement exempts the records whose coverage claim nobody looks at.

Open one issue per disagreement and decide them separately. Rejected because
three of the four are one question, which is whether a worked example or the
record that delegated to it is the authority, and answering it three times
invites three answers.

## What depends on this

`schema/record-1.schema.json`, whose required lists, claimed block and derived
block carry all four resolutions, and which no longer names issue #107 in a
`$comment`.

`docs/record-format.md`, which is what somebody writing a record by hand reads,
and which held the list of four places the schema was weaker than the records.

Record 0003, which carries a correction beside its derived field table and
another beside its claimed block, and whose worked example gains a coverage
argument, a locator and a stratum on every claimed value. Its status, its number
and the rest of its text do not move.

Records 0005 and 0006, neither of which moves. All four resolutions are in the
direction those two already argue for, which is why they are unchanged.

Issue #36, the loader, and issue #38, the fixture corpus, which now have four
more refusals to carry and one fewer shape to be permissive about.

Issue #43, the schema validation check, whose closing statement about what a
green run means no longer has to exclude these four.

Issue #73, the first catalogue entry, which is where the placeholder provenance
in the worked example is replaced by a real citation and a real locator.

Issue #110, which holds what a correction to a landed record is, and which this
record made an instance of before its shape was written down.

Record 0011, issue #20, which fixes what a cost report holds. This record fixes
only where one is stored, and the shape stays open until that record lands.
