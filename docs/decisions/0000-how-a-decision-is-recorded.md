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
