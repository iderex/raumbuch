# 0008. What is_this_new returns

## Status

Accepted

## Date

2026-08-08

## Question

One callable function is the deliverable of this board. Its return type is a
design decision with a research-integrity consequence attached, because the whole
complaint this project answers is that the field may be republishing known
geometries and has no cheap way to tell. A library that answers that question
badly is worse than one that does not exist.

What is the signature? What are the outcomes, exhaustively? What does the value
look like for each of them, including the one that admits the question was not
decided? Is the function pure, does it return a report or write a file, is the
catalogue an argument or a global, and what happens when the catalogue on disk is
not the one the caller expected?

Record 0007 fixed the relation being decided and the two paragraphs a report
carries. Record 0005 fixed the input contract, including what happens to a query
with undeclared parameters. Record 0009 fixed the `assumption` list and required
that no route publishes a value computed under an assumption without it. Record
0001 fixed the language this signature is written in. This record is where those
meet the caller.

## Answer

### The signature

```python
def is_this_new(
    query: Query,
    catalogue: Catalogue,
    *,
    budget: Budget,
    assumptions: Sequence[Assumption] = (),
) -> Verdict:
    ...
```

The catalogue is an argument and never a global. A global would mean the answer
depends on process state the caller cannot see, which makes two calls in one
program able to disagree for a reason nothing records, and it would put the
catalogue outside the value that reports which catalogue was consulted.

The function is pure. It reads nothing from the environment, it writes no file,
and it returns everything it has to say. Serialising the verdict is the caller's
step and `raumbuch` the command-line program is one such caller. A function that
writes a file has decided where, and a library that decides where a file goes is
a library that cannot be called twice concurrently or run on a read-only host.

It is deterministic in the sense of record 0012 tier one: for one query, one
catalogue, one commit and one budget, the verdict is the same value every time,
across worker counts and process invocations. The cost fields are the declared
exception, as they are there.

`budget` is required rather than defaulted. Record 0011, issue #20, fixes what a
budget is and what a cost report holds, and it has not landed, so this record
fixes only that a budget is an input and that exhausting it is an outcome rather
than a kill. Making it required and keyword-only is the one thing this record can
do to stop a default appearing later that quietly decides how much of somebody's
machine this function may take.

`assumptions` is the caller-supplied side of record 0009's second response. It
defaults to empty, which is the normal case, and every assumption that was
actually used comes back on the verdict.

### Three outcomes, and why not two

```python
Verdict = Match | Distinct | Undetermined
```

Two values, three answers. Whichever answer was given no value of its own would
have to be reported as one of the others, and the only one small enough to be
folded away is the one whose loss publishes a false novelty claim.

That is the sentence, and the type is what makes it hold rather than the sentence.
`Verdict` is the base class of exactly three frozen dataclasses, it is never
instantiated, and it defines `__bool__` to raise `TypeError` with a message
naming this record. So

```python
if is_this_new(q, cat, budget=b):      # raises TypeError
    publish()
```

fails at the moment of the mistake rather than treating every verdict as true,
and a caller has to say which of the three they meant. Record 0001 chose a
language with no compiler to refuse this before a run, and this is where that cost
is paid: the refusal is a runtime one, it is a guard, and issue #95 requires it to
be proved to bite by a test that removes it and watches the suite go red.

The name of the function inverts against `Match`, and that is deliberate. A
function called `is_this_new` returning a `Match` object cannot be misread the way
a function called `is_this_new` returning `True` can, because there is no reading
in which `Match` means new.

### What every verdict carries

Four things sit on all three outcomes, because all three are claims about a
particular catalogue made under particular conditions.

`catalogue`, a stamp: the catalogue release identifier, the number of entries
consulted, and a digest over them. A negative answer is a claim about the whole
catalogue and is meaningless without saying which catalogue.

`notices`, the corrections and supersessions of record 0004 affecting any entry
this verdict names, each carrying the pinned version, the current version and the
correction entries between them.

`assumptions`, record 0009's list, holding every assumption the run actually
relied on with the expression, the side assumed, where it came from, and the order
and frame it was applied at. An empty tuple is the normal case. A verdict computed
under a non-empty list is a weaker claim than one computed under an empty one, and
the list is what stops it being read as the same claim.

`cost`, whose shape record 0011 fixes and whose placement is fixed here.

And the two paragraphs of record 0007, carried verbatim from one module-level
constant, on every verdict rather than only on `Match`. Carrying them
conditionally would make the copy depend on the outcome, which is one more way for
the copies to differ.

### Match

The query is locally isometric to an entry, in the sense record 0007 fixed and no
larger sense.

It names the entry as `(id, version)`, the stratum and the chart the match holds
on, the invariants that agreed, and the frame that realises the match where one
could be produced. Where the frame could not be produced the field is absent and a
reason says so, because a frame is evidence and an absent frame is a weaker match
that should not look like a stronger one.

It carries the verification states of record 0006 for every matched value, with
the markers attached. A match against a `transcribed` Petrov type inherits that
state and no more, and the marker travels with the answer rather than sitting in
documentation the consumer is assumed to have read.

```
Match(
  entry      = ("schwarzschild", 3),
  stratum    = "generic",
  chart      = "exterior",
  agreed     = ( ("petrov_type", "D"),
                 ("isotropy_dimension", (4, 4)),
                 ("independent_function_count", (0, 1)),
                 ("termination_order", 1) ),
  frame      = Frame(...),
  verification = ( ("petrov_type", "recomputed", marker=None),
                   ("killing_dimension", "transcribed",
                    marker="no computation in this repository has confirmed "
                           "this value") ),
  catalogue  = CatalogueStamp(release="2026.1", entries=10, digest="..."),
  notices    = ( Corrected(id="schwarzschild", pinned=1, current=3,
                           corrections=(...,)), ),
  assumptions = (),
  cost       = Cost(...),
  disclosure = (POSITIVE_PARAGRAPH, LIMITING_PARAGRAPH),
)
```

Several entries can match, and the field is a tuple rather than a single entry.
Record 0007 fixed that two records differing only in `matter.model` are the same
solution and are different entries, and that the report names both rather than
hiding one.

### Distinct

The query is not locally isometric to any entry in the catalogue that was
consulted.

This is the expensive answer, because it is a claim about every entry. It carries,
for every entry and every stratum, at least one invariant that differs, with both
values. Issue #62 is where the separating invariant a negative answer has to show
is decided, and this record fixes that a `Distinct` with no separating invariant
for some entry is not constructible: the field is required per entry, and an entry
the run could not separate is why the verdict is `Undetermined` instead.

```
Distinct(
  separated  = ( ("kerr", 2, "generic",
                  Differs(invariant="independent_function_count",
                          query=(0, 1), entry=(1, 2))),
                 ("godel", 1, "generic",
                  Differs(invariant="ricci_type",
                          query="the Ricci tensor vanishes",
                          entry="perfect fluid")),
                 ... one per entry per stratum ... ),
  catalogue  = CatalogueStamp(release="2026.1", entries=10, digest="..."),
  notices    = (),
  assumptions = (),
  cost       = Cost(...),
  disclosure = (POSITIVE_PARAGRAPH, LIMITING_PARAGRAPH),
)
```

A `Distinct` says the query is not in this catalogue at this release. It does not
say the geometry is unpublished, and the operator documentation in issue #99 is
where that gap between "not in the catalogue" and "new to the field" is written
for a reader. The coverage number in issue #79 is the other half of it.

### Undetermined

The question was not decided. This is a first-class answer and not an error.

It carries what was reached, what stopped it, and what would let it proceed. The
reason comes from a closed vocabulary, and a fifth reason is added by amending
this record rather than by writing one into a call site:

`budget_exhausted`, the declared budget was reached. Record 0011, issue #20, is
what a budget is; issue #69 is the refusal instead of an out-of-memory kill.

`derivative_bound_reached`, the declared bound on differentiation order was
reached with the termination test not yet satisfied. Issue #55.

`zero_test_undecided`, an expression could not be decided, no case split was
available within the declared limit, and no supplied assumption covered it.
Record 0009's third response. The entry names the expression as written, the
differentiation order and the frame, which is what record 0009 requires a refusal
to report.

`parameter_domain_undeclared`, the query carries free parameters without domains
and ranges. Record 0005 fixed that equivalence of two families is not defined
until the domains are, so this is the only honest answer and it is not politeness.

```
Undetermined(
  reason     = "zero_test_undecided",
  reached    = Reached(order=3, entries_eliminated=7, entries_open=3),
  stopped_by = OpenExpression(expression="f''(u) - 2*f'(u)/u",
                              order=3, frame="canonical at order 2",
                              entry=("kundt-wave", 1)),
  would_proceed = ( "an assumption on the sign of the expression above",
                    "a case-split limit above 4" ),
  catalogue  = CatalogueStamp(release="2026.1", entries=10, digest="..."),
  notices    = (),
  assumptions = ( Assumption(expression="M > 0", side="nonzero",
                             source="caller", order=0, frame="input"), ),
  cost       = Cost(...),
  disclosure = (POSITIVE_PARAGRAPH, LIMITING_PARAGRAPH),
)
```

`entries_eliminated` is on the value on purpose. An undetermined answer that ruled
out seven of ten entries has done real work, and a caller that has to treat it as
nothing learns nothing from a run that cost as much as a decided one. It is
reported as partial progress and never as a partial negative: the entries that
were eliminated are named, and the ones still open are named, and no field
anywhere in this type reduces to "probably new".

### The catalogue the caller did not expect

A caller pins by passing the pin to the loader, not to this function:

```python
catalogue = Catalogue.load(path, expect=CataloguePin(release="2026.1"))
```

A release mismatch raises `CataloguePinMismatch` from the loader. It is not a
fourth outcome and it is not a verdict.

The reason for a raise rather than an outcome is that a fourth member of the union
would be handled by the same `match` statement as the other three, sitting beside
two answers about geometry, and the first caller in a hurry would fold it into the
branch next to it. An exception cannot be mistaken for a verdict, and this is a
caller error rather than a fact about a spacetime.

Per-record pins are different and are not errors. A caller pinning `(id, version)`
under record 0004 and finding a corrected or superseded entry gets the load and
gets a notice, and the notices for every entry the verdict names travel on the
verdict. A correction is information the caller asked to be told; a release
mismatch means the computation would have been run against something other than
what was asked for.

`is_this_new` never loads anything, so it never has to decide this. That is the
purity above doing its second job.

### What is not enforced

Record 0007 named the report as the third place carrying its two paragraphs, and
named it as the copy nothing compares against the record. That is still true.
Putting both paragraphs behind one module-level constant narrows the drift to one
place; it does not compare anything, and a constant edited in a hurry passes every
route in this tree today. Issue #105 now holds the check that would refuse a
difference. Record 0007 also says nothing refuses a fourth place that paraphrases
the paragraphs, and this record does not change that either.

The `__bool__` refusal is a guard and, until the suite exists, it is a guard with
no proof that it bites. Issue #95 is where that proof is owed, and until milestone
2 lands there is no suite for it to live in. Nothing in this repository refuses
anything described in this record today, because there is no code here.

## Rejected alternatives

A boolean. Rejected in the section above, and worth one more sentence about why it
is tempting: the question in the function's name is a yes-or-no question, and the
algorithm's inability to answer it is a property of the mathematics rather than of
the caller's need. A type that hides that is a type that lies on behalf of the
implementation.

An optional, so that `None` means undecided. Rejected because `None` is falsy, so
`if not verdict` treats "I could not tell" and "not equivalent" identically, which
is precisely the collapse this record exists to make hard. It is the boolean
rejection with an extra step.

An enum of three values with the evidence returned separately or logged. Rejected
because the evidence is what makes each answer usable and separating it means the
first caller keeps the enum and drops the rest. A negative answer with no
separating invariant is an assertion, and record 0012 already refuses the log as a
place a decision is recorded.

Raising an exception for the undetermined case. Rejected because an exception is
what a caller writes a bare `except` around, and because an undetermined run has
produced real information: the entries eliminated, the order reached, the
expression that stopped it. Throwing that away is throwing away the most expensive
part of the run. Exceptions are kept for the one case that is genuinely a caller
error, which is the pin mismatch.

Returning the verdict and also writing a report file. Rejected because it decides
where, it makes the function impure for no gain to a library caller, and the
command-line program can serialise the returned value with no help from the
library.

A global or module-level catalogue, set once at import. Rejected because the
answer would then depend on state the value cannot report, and because two
catalogues in one process is an ordinary thing for a test suite to want.

A default budget. Rejected because a default is a decision about how much of
somebody's machine this function may take, made by whoever wrote the default, and
milestone 7 exists because that number matters. Requiring it costs one argument at
every call site and makes the caller name the number.

Collapsing `parameter_domain_undeclared` into a refusal at the input, so that the
function raises on an underspecified query. Rejected because record 0005 fixed
that a query carrying free parameters is a normal query and only an undeclared
domain is the problem, and because the undetermined answer with that reason tells
the caller exactly what to add. A raise would tell them the same thing in a form
they are more likely to swallow.

Reporting an undetermined run as a negative when most entries were eliminated.
Rejected as the exact failure this board exists to reduce. There is no threshold
at which "I ruled out nine of ten" becomes "this is new", and a field carrying a
proportion would grow one.

Widening the verdict to say whether the query is related to an entry by a
homothety. Rejected here because record 0007 already fixed it as a different
relation and said that if it is ever added it is an additional field and never a
change to the verdict. Issue #62 is where that would land.

## What depends on this

Record 0007, whose two paragraphs this record carries and whose disclosure about
the third copy this record repeats rather than repairs.

Record 0005, whose input contract this signature implements and whose undetermined
answer for an undeclared parameter domain is one of the four reasons.

Record 0009, whose `assumption` list is placed on every verdict here, and whose
third response is the `zero_test_undecided` reason.

Record 0004, whose corrections and supersessions arrive as notices, and whose
`(id, version)` pair is what a `Match` names.

Record 0006, whose verification states and markers travel on a `Match`.

Record 0011, issue #20, which fixes what a budget and a cost report are and which
this record deliberately does not pre-empt.

Record 0012, whose tier one determinism is asserted over this value, and whose
excluded cost fields are the exception named above.

Record 0001, whose language this signature is written in and whose absent compiler
the `__bool__` refusal stands in for.

Issue #58, issue #59 and issue #62, which produce the agreed invariants, the
parameter map and the separating invariant this value carries.

Issue #60, `is_this_new` itself, which is this record turned into code.

Issue #69, the refusal instead of an out-of-memory kill, which is the
`budget_exhausted` reason reaching a caller.

Issue #95, which owes the proof that the `__bool__` refusal bites.

Issue #99, the operator documentation, which carries the same two paragraphs and
whose check covers the documentation copies and not this one.

Issue #105, which owes the check that compares this record's copy of the
paragraphs against record 0007.
