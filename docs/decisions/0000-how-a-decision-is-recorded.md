# 0000. How a decision is recorded

## Status

Accepted

## Date

2026-08-07

## Question

Fourteen decisions land in the first milestone and more will follow. Without a
fixed shape each record invents one, and the fourth reader cannot tell a
decision that was argued from a decision that was assumed. What shape does a
decision record take here, how is it numbered, what happens to one that is later
replaced, and where is the list of them kept?

## Answer

A decision record is one file under `docs/decisions/`, named
`NNNN-short-title.md`, where `NNNN` is a four digit number. A number is assigned
once, is never reused, and is never renumbered. `0000` is this record.

### The required sections

Every record carries all of these, spelled exactly as written here, at the
heading level shown, and in this order:

```
# NNNN. Title
## Status
## Date
## Question
## Answer
## Rejected alternatives
## What depends on this
```

This block is the list itself and not a copy of it. The check asked for in
issue #31 reads the required sections out of this fenced block, so there is one
list and nothing to drift against.

That check has to be aware of fenced code blocks in both directions, and this
record is the reason. The block above contains lines beginning with `#` that are
not headings of this document, and record 0003 contains a worked example in a
format whose comments also begin with `#`. A checker that scans for headings
line by line will read both as sections and refuse every record including this
one. Sections are the headings outside fences.

One further heading is allowed and is not required: `## Supersedes`, which only
appears on a record that replaces an earlier one. Headings below `##` are free.

### What each section holds

`## Status` holds exactly one of these words or phrases and nothing else:

```
Proposed
Accepted
Superseded by NNNN
```

`## Date` holds one `YYYY-MM-DD` date, the date the status last changed.

`## Question` states what was open, in enough detail that a reader who was not
there can see why an answer was needed. A record whose question is a restatement
of its title has not written this section.

`## Answer` states what was decided. It is written in the present tense, as the
state of the project, not as a proposal.

`## Rejected alternatives` lists the options that were considered and not taken,
each with the reason it was not taken. An option listed with no reason is not a
rejected alternative and does not count as one. This section is the reason the
shape exists: most arguments about a decision six months later are arguments
about an option somebody believes was never considered, and the cheapest answer
is a paragraph saying it was considered and what it cost.

`## What depends on this` names what would have to move if the answer were
revisited. Issues, other records, file formats, published interfaces. This is
what tells a later reader the price of reopening the question, and it is the
section that makes a record more than a diary entry.

### Superseding a record

A record is never deleted and never rewritten to say something else. A record
that vanishes takes its reasoning with it, and a record edited in place leaves a
reader unable to tell which version an old argument was against.

When decision `0003` is replaced by a new decision, two things happen and both
are pointers:

The old record keeps its number, its title and its whole text. Its `## Status`
section becomes `Superseded by 0021`, and its `## Date` becomes the date of that
change. Nothing else in it moves.

The new record `0021` carries a `## Supersedes` section naming `0003`.

The link is written from both ends on purpose. A reader arriving at the old
record needs to be sent forward, and a reader arriving at the new one needs to
know what it displaced and where the argument against the old answer is.

A status of `Superseded by NNNN` naming a record that does not exist is a
refusal, not a warning, and issue #31 carries the check.

### Correcting a landed record

A correction exists here as a thing distinct from a supersession, and the two are
not interchangeable.

Supersession is for a decision that was displaced. The answer moved, and a reader
arriving at the old record has to be sent forward to the one that replaced it.
Correction is for a record whose answer stands and whose text is wrong somewhere:
a row of a table, a field name, a worked example that no longer validates against
what the record delegated to another one.

The boundary is the record's own `## Question`. Where the answer to that question
moves, the record is superseded. Where the answer stands and something written
under it is wrong, the record is corrected. A supersession whose new record has
to repeat every part that did not move is a correction wearing the wrong
instrument, and the cost of that is paid by the reader, who is told a decision
was displaced when it was not.

A correction is written into the record, at the place the wrong text sits, and
the wrong text stays. This is not the in-place rewrite refused above. Nothing
already written is deleted or changed to say something else, so a reader meeting
an old argument can still see the version it was made against, which is the whole
reason for that refusal.

What one looks like:

A heading `### Correction, YYYY-MM-DD, on <what it corrects>`, immediately below
the passage it corrects. Headings below `##` are free, so a correction adds no
section and the required list above is untouched.

Its body says what the text above says, what is right instead, which record or
issue argues it, and how it was found. How it was found is the half a later
reader cannot reconstruct, and it is the half that tells the next person whether
to go looking for more of the same.

Where the corrected passage sits far enough above that a reader will not meet the
correction, the passage gains one sentence pointing down at it. That sentence is
the only place a correction touches the old text, and it adds a pointer rather
than changing a claim.

`## Status` and `## Date` do not move. The status is unchanged because the record
is still the decision in force, and `## Date` is defined above as the date the
status last changed, so a correction that changes no status changes no date. The
correction carries its own date in its heading, which is where a reader looks for
when it was made. The index carries the number, the title and the status, so no
row in it moves either.

A record whose status is `Superseded by NNNN` gains no correction. It is
finished, and whatever is wrong in it either no longer matters or is wrong in the
record that displaced it, which is where the correction belongs.

What the check in issue #31 requires of a correction:

A heading beginning `### Correction,` outside a fenced block carries a
`YYYY-MM-DD` date directly after that comma.

No such heading appears in a record whose `## Status` is `Superseded by NNNN`.

Nothing else. The required section list, the allowed status words and the index
rows are unaffected, so a record carrying a correction is well formed exactly
when it was well formed without one. Whether the body says what was wrong and how
it was found is not decidable by reading the tree, and the review is where a
correction that says neither is caught.

### The first correction was made before this shape was written

Record 0003 carries two corrections dated 2026-08-08, one on where the cost of a
run is stored and one on the shape of the claimed block. Both were made under
issue #107 and argued in record 0015, and record 0015 says of itself that this
record described no state between an untouched record and a superseded one and
that it used one anyway.

The shape above is read off those two rather than invented beside them. The
heading form, the position below the corrected passage, the untouched original,
the pointer sentence added above the claimed block, and the unmoved status and
date are all what record 0003 does today:

    git grep -n '^### Correction' -- docs/decisions/
    docs/decisions/0003-the-solution-record.md:98:### Correction, 2026-08-08, on where the cost of a run is stored
    docs/decisions/0003-the-solution-record.md:118:### Correction, 2026-08-08, on the shape of the claimed block

So the instance is inside the answer, and no landed record needs an edit to come
into it.

### This section is an addition rather than a correction

Nothing above it was wrong. This record said nothing about corrections, and
saying nothing is not saying something else, so the refusal of an in-place
rewrite does not reach text that answers a question the record had taken no
position on.

That is a third shape and it gets one rule here so that nobody has to invent a
fourth. An addition to a landed record names its date and the issue that asked
for it, contradicts nothing already in the record, and moves neither the status
nor the date. Where it would contradict something, the thing it contradicts is
corrected under the shape above and the addition is that correction.

Added 2026-08-08 under issue #110.

### The index

`docs/decisions/README.md` lists every record. Each row carries the number, the
title, the status and a link to the file. Every file under `docs/decisions/`
other than `README.md` appears in the index exactly once, and every row in the
index points at a file that exists. Issue #31 carries the check for both
directions, because an index that silently misses a record is worse than no
index: a reader who trusts it concludes the decision was never made.

## Rejected alternatives

Let each record find its own shape. This is the state this record ends, and its
cost is already visible in what the first milestone contains: fifteen records
written over a short period by whoever picked the issue up. Without a shape the
rejected alternatives get dropped first, because they are the section that costs
effort and reads as optional.

A fuller template, with context, decision drivers, and a pros and cons list per
option. More sections than are argued here. Sections that are optional in
practice get filled with filler, and filler in a decision record is worse than
an absent section because it looks like an answer.

A one sentence form, in the style of "in the context of X, facing Y, we chose Z
to achieve W". Compact and it has no room for the rejected alternatives, which
is the one section this project is least willing to lose.

Keep decisions in the issue tracker only. The tracker is where the planning
happens and it stays that way, but an issue body is not versioned with the code
it constrains, it can be edited without leaving a trace in the tree, and a
reader with a checkout has no copy of it. A decision that shapes a file format
belongs beside the file format.

One running decisions document. Every record then edits the same file, which
collides the moment two decisions are written at once, and a superseded decision
either disappears from it or the file grows without bound with no way to see
which parts are still in force.

Number the records by date instead of by sequence. Two records written on one
day collide, and a date in the name invites the reader to treat recency as
authority rather than reading the status.

The alternatives below were considered for the correction shape, and were added
with it on 2026-08-08 under issue #110.

Supersession as the only route, with a record wrong in one line superseded in
full and the cost of that stated rather than left to whoever meets it first. This
is the answer issue #110 holds open beside the one taken. Rejected because the
case has already arrived and the instrument was already found wrong for it:
record 0003 is wrong in one table row and right in the three-block separation,
the file format, the expression sub-language and the worked example, and a
replacement would carry all of that across to move the row. The reader of the old
record would then be sent forward by a pointer that says the decision was
displaced, which is a false statement about a decision still in force.

Rewrite the wrong line in place and leave no trace. Rejected for the reason the
supersession section above already gives: a reader who meets an old argument
cannot then tell which version it was made against. That reason does not weaken
because the change is one line.

Collect a record's corrections in one section at the end of it. Rejected because
the reader who needs a correction is the reader reading the wrong passage, and a
list at the end is found only by somebody who already doubted what they read.

Give each correction its own numbered record. Rejected because it spends a
number and a full set of six sections to move one row, and it puts the reader one
hop further from the text that is wrong. Record 0015 is not that shape and is not
a precedent for it: it is the decision record for four disagreements between
three records, and the corrections it argued were written into record 0003
itself.

Move `## Date` when a correction is made, so that the front of the record shows
it was touched. Rejected because that section is defined above as the date the
status last changed, and a date meaning two things is a date nobody can read. The
correction's own date is in its heading, where it belongs to the correction
rather than to the record.

## What depends on this

Every record from `0001` onwards, all of which are written to this shape.

`docs/decisions/README.md`, whose row shape is fixed here.

Issue #31, the check named `Decision records are well formed`, which reads the
required section list and the allowed status words out of this record rather
than carrying its own copy. Changing a heading here changes what that check
requires, which is the intended coupling and the reason the list sits in a
fenced block.

Any later tooling that reads decision records, which may rely on the section
names being stable and on numbers never being reused.

Issue #31 again, and for two rules beyond the ones above: the date form on a
correction heading, and the refusal of a correction on a superseded record. Those
sit in the answer above rather than in the check, on the same coupling as the
required section list.

Record 0003, whose two corrections are the first instance of the shape and are
what it was read off. A change to the heading form here makes that record the one
that no longer matches, so the form moves only with an argument about those two.

Record 0015, which resolved the four disagreements between records 0003, 0005 and
0006 and chose correction over supersession for record 0003 before there was a
shape to choose. It named the gap and pointed at issue #110, which is what this
section answers.
