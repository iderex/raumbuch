# 0012. Determinism of a classification

## Status

Accepted

## Date

2026-08-08

## Question

If two runs of the same metric produce two different classification records, the
catalogue cannot be regenerated, a correction cannot be told apart from noise, and
the catalogue gate in issue #77, which compares a stored derived value against a
fresh computation, refuses or passes for reasons that have nothing to do with the
mathematics.

The threats are ordinary and cheap to introduce by accident. A map iterated in
hash order, and the order terms were summed in reaches the output. A parallel
search over frame candidates where the first success wins. A cache whose output
depends on what was inserted before. A canonical frame that is canonical only up
to a discrete ambiguity nobody resolved.

Which artefacts have to be identical between runs? Identical across what: thread
count, machine, platform, version of the symbolic layer? And what happens where a
genuinely arbitrary choice exists?

## Answer

### The property, in two tiers

The first tier is the one this project enforces and replays.

For one input record, one commit of this repository, one declared budget and one
machine, the classification record is byte-for-byte identical between runs. It is
identical across thread counts, across the number of workers a parallel stage
chooses to use, across process invocations, and across the order the entries of a
catalogue were loaded in. Nothing about how the work was scheduled reaches the
output.

The second tier is a weaker property over a named subset, required across
platforms and across admitted versions of the symbolic layer.

The discrete part of the classification is identical: the Petrov type, the Ricci
type, the isotropy dimension at each order, the count of functionally independent
functions at each order, the termination order, and the Killing vector count.
Those are the fields record 0007, issue #13, compares first, and a platform that
disagreed on one of them would be classifying a different geometry.

The continuous part is not required to be byte-identical across platforms or
across versions of the symbolic layer. The normal form of an expression is a
normal form and not a canonical form, per record 0010, so two implementations of
the same reduction may agree on what is zero and differ on how a nonzero
expression is written. Requiring byte equality there would mean pinning one
implementation of the algebra as the definition of correctness, and the cost is
paid on every dependency update forever.

The line between the tiers is the line between what the mathematics fixes and what
an implementation chooses, and it is drawn there on purpose rather than at the
point where enforcement is convenient.

### What is deliberately outside the scope

The cost fields. Wall clock, peak memory and the count of normalisations are
measurements of a run, they differ between two runs on one machine for reasons
this project does not control, and record 0006 stores them on the verification
entry for exactly that reason. A gate that required them to match would be red on
every second run.

The human-readable log. Its content is not compared and its line order is not
promised, because a log is where progress is reported and a progress report is
allowed to know how many workers there are. What the log may not do is be the
only place a decision is recorded: anything a later reader needs in order to
understand the verdict belongs in the classification record, which is in scope.

The contents of the shared subexpression store record 0010 keeps alive across
orders. Nothing consumes it, it is an internal cache, and its shape may depend on
insertion order. What may not depend on insertion order is the normal form the
cache returns, which is the next section.

Timestamps. A date is written into a derived entry by record 0003 and it changes
between runs by construction. The replay check compares the record with the
timestamp fields excluded, and the set of excluded fields is a list in the check
rather than a rule the reader has to reconstruct.

### The four rules that make it hold

Ordered iteration. Nothing iterates a set or a map in its native order where the
result reaches the output. Every such iteration is over a key sequence sorted by
a declared total order. The sort is not an optimisation and removing it is not a
cleanup.

No first-wins parallelism. A parallel stage collects every result and then reduces
them in a fixed order. Where a stage searches for one of several acceptable
answers, it does not stop at the first: it collects all of them from the candidate
set it was given and selects by the tie-break rule below. This costs work that a
first-wins search would have skipped, and it is what makes the thread count
invisible in the output.

Normalisation is a function of the expression. The normal form of an expression
depends on the expression and on nothing else, per record 0009. A cache that
returns a different form because of what was inserted before it is a defect and
not a performance characteristic, and the cache is content addressed so that the
shape is not available to it.

Arbitrary choices are made by a written rule. Where the mathematics leaves a
choice, the choice is fixed by a rule in this repository, the rule is written down
where the choice is made, and the rule refers only to the data. A choice that
refers to the order candidates arrived in is not a rule.

### The tie-break rule, worked through

The canonical frame fixing in issue #51 reduces the frame freedom as far as the
curvature allows and records what is left. Where what is left includes a discrete
ambiguity, a rule has to pick one, and Petrov type D is the case that arrives
first because it is the type of the first two entries the catalogue will hold.

At type D, four of the five Weyl scalars vanish in a canonical frame and `Psi_2`
does not. The remaining continuous freedom is the boost in the `l`, `n` plane
together with the spin in the `m` plane, and `Psi_2` is unchanged by both, so
neither can be used to fix anything further at this order. What remains beyond
that continuous freedom is discrete: interchanging `l` with `n` while
interchanging `m` with `mbar` maps the scalar set to itself and leaves `Psi_2`
where it was. Two frames therefore satisfy every condition the order zero
classification imposes, and nothing in the mathematics prefers one.

The rule. Compute the first order Cartan scalars in both frames. Serialise each
frame's ordered tuple of scalars, in the fixed component order record 0002 sets,
using the normal form of record 0009, and compare the two serialisations
bytewise. The frame whose serialisation sorts first is the canonical one. Where
the two serialisations are equal, the two frames are indistinguishable to the
algorithm at every order, so either may be taken and the rule takes the first.

Two things about that rule are worth saying plainly. It is arbitrary: sorting last
would have served equally well, and nothing about the geometry recommends first.
And its value is entirely in being written down, so it may be changed only by
changing this record, because changing it silently rewrites every stored frame in
the catalogue while every discrete field stays as it was, which is a difference
the gate would report as a mismatch with no cause visible in the diff.

The rule is stated in terms of the serialisation of a normal form, which is a
tier one object rather than a tier two one. Across platforms the two frames may
serialise differently and the tie may break the other way, which is inside what
tier two deliberately does not promise, and the discrete classification is
identical either way. That consequence is the reason the two tiers exist rather
than one.

### Randomness

One place in the design draws a random number: the cheap filter in record 0009,
which evaluates an expression at a pseudo-random rational point modulo a large
prime to prove it is not identically zero.

Its seed is derived from a digest of the input record, so the sequence is a
function of the input and not of the clock, the process or the machine. That is
what keeps it inside tier one.

The seed is not what makes the filter safe. The filter can only refuse equality:
a nonzero evaluation is a proof, a zero evaluation is inconclusive and the full
normalisation runs. So a different seed changes which expressions took the cheap
route and therefore what the run cost, and it cannot change an answer. Both
defences are in place because the seed is easy to make non-deterministic by
accident and the proof is what holds when somebody does.

### The check that refuses a violation

Issue #32, the determinism replay check, is where this record is enforced, and it
is built in milestone 2 before the classifier it will judge exists.

What it does: classify the same input twice in one gate run, with different worker
counts, and compare the two classification records byte for byte with the excluded
timestamp fields removed. A difference reds the check and prints the first
differing field rather than the whole record.

Two properties that check owes, and they are the ones a replay check most easily
fails to have. It has to use more than one worker in at least one of the two runs,
because two single-threaded runs of the same code agree for reasons that have
nothing to do with this record and the check would pass on a tree that violates it
everywhere. And it has to be proved to bite, in the sense the target gate in
issue #95 requires: a fixture whose stage iterates a map in native order, or
whose parallel stage takes the first success, and which the check refuses for that
reason and not for another. A replay check that has never been shown to fail is a
check nobody has run against a violation.

The property in tier two is not covered by that check, because one gate run
happens on one platform and against one version of the symbolic layer. Nothing in
this repository refuses a tier two violation today. No open issue holds a
cross-platform run either: issue #91 is the property suite and issue #93 is the
supply-chain and static-analysis parity work, and neither is a second platform.
So tier two is a stated requirement with no route that tests it, which is a gap
rather than a plan, and it is named here rather than left for a reader to infer
from the replay check's scope.

### What would show this was wrong

The choice with a cost worth measuring is the second rule, collecting every result
of a parallel stage instead of taking the first acceptable one. There is no code
in this repository yet, so nothing has been run and no number is quoted.

The run that decides it: classify one expensive entry with the candidate search
collecting all results and with it stopping at the first, and record wall clock
and peak memory for each. If collecting all costs a large multiple rather than a
margin, the answer is not to take the first: it is to make the candidate set
smaller so that the choice does not arise, or to fix the selection by a rule
evaluated before the expensive part rather than after. Either of those keeps the
property. The measurement belongs in the cost table in issue #70.

## Rejected alternatives

Determinism across platforms and across versions of the symbolic layer, for the
whole record. Rejected as the top-level property because it makes one
implementation of the algebra the definition of a correct expression, so a
dependency update becomes a catalogue-wide diff with no mathematical content, and
because a normal form is not a canonical form. Kept for the discrete part, where
the mathematics does fix the answer.

Determinism across runs on one machine only, for the whole record, with nothing
required across platforms. Rejected because the discrete classification is what
the catalogue publishes and what a citation refers to. A project that could not
say the Petrov type of an entry is the same on another machine has not classified
anything.

Determinism of the intermediate artefacts and the log as well. Rejected because
the log's job includes reporting progress, which legitimately knows how many
workers are running, and because the intermediate store is a cache nothing
consumes. Extending the property there would make the property large enough that
the first failure would be answered by weakening it.

A single-threaded implementation, so the question does not arise. Rejected because
the entries that approach the memory ceiling are the reason milestone 7 exists,
and because it converts a property into a restriction on the design that would be
lifted the first time an entry did not finish. The property has to survive
parallelism rather than forbid it.

A canonical form for expressions, which would make byte equality across
implementations achievable. Rejected in record 0010 and for the reasons record
0009 gives: it is not available over the admitted expression class.

Sorting only where a determinism failure has been observed. Rejected because that
is a rule about what has been noticed rather than about what the code does, and
the failure surfaces as a gate that is red once in twenty runs, which is the shape
that gets rerun rather than fixed.

Choosing among equivalent frames by a rule that refers to the search order.
Rejected because it is not a rule, it is a description of the current
implementation, and any change to the candidate enumeration silently rewrites
stored frames.

Storing the chosen frame and treating it as the tie-break for later runs.
Rejected because the catalogue would then be the authority for a choice the code
is supposed to reproduce, so a fresh classification could never disagree with a
stored one and the gate in issue #77 would be comparing a value against itself.

## What depends on this

Record 0002, whose fixed frame index order and component order are what a
serialisation of a scalar tuple is defined against.

Record 0009, whose normal form the tie-break rule serialises and whose cheap
filter draws the one random number in the design, seeded from the input digest
here.

Record 0010, whose shared subexpression store is outside the scope of this record
in its contents and inside it in what it returns.

Record 0006, whose cost fields are outside the scope, and whose staleness anchors
are digests over the record and the source rather than over a run, so they are
unaffected by the exclusions here.

Record 0011, issue #20, the declared budget, which is part of the input the
property is stated against: two runs under different budgets are not required to
agree, because one of them may have refused.

Issue #32, the determinism replay check, which owes a run with more than one
worker and a proof that it bites.

Issue #48, the frame group action, and issue #51, the order zero frame fixing,
which is where the tie-break rule is implemented and where it is written down
beside the code that applies it.

Issue #53, the bookkeeping, whose ranks are computed from matrices whose row
order must not depend on iteration order.

Issue #56, the classification record, whose field set is what byte equality is
asserted over, and which owes the excluded timestamp list.

Issue #77, the catalogue gate, which compares a stored derived value against a
fresh one and is meaningless without this record.

Issue #91, the property suite, which is the nearest thing to a test of the tier
two claim and is not a second platform. Nothing in the plan is, which is the gap
named above.

Issue #95, every guard proved to bite, which covers the replay check's own proof.
