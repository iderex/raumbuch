# 0009. Arithmetic, and zero testing where it is undecidable

## Status

Accepted

## Date

2026-08-08

## Question

Every discrete step in the algorithm is a zero test. Is this Weyl scalar zero in
this frame. Does the quartic have a repeated root. Has the isotropy dimension
dropped between two orders. Is this Jacobian's rank one less than the last one.
Each of those is a branch, and a branch taken on a wrong zero test produces a
classification that is confidently wrong rather than absent, which is the failure
mode this board is a response to.

Which number domains does the arithmetic run in? What procedure answers a zero
test, and can the software tell a decision apart from a hope? What happens where
the question is undecidable, which is not exotic because large parts of the
reference literature are families with free functions in them? And does floating
point appear anywhere?

## Answer

### The domains, in the order they are entered

The ground field is the rationals `Q`, extended by `i`. The extension is not
optional and it is not a convenience: record 0002 chose a complex null tetrad, so
the Weyl scalars, the Ricci scalars and the spin coefficients are complex from
the first component, and the ground field is the Gaussian rationals `Q(i)`. Both
`Q` and `Q(i)` are exact, and arithmetic in them is closed under the four
operations with no representation choice left open.

Above that sits the field of rational functions in the declared symbols: the
coordinates a chart declares and the parameters a record declares, per record
0003. Elements are quotients of polynomials over `Q(i)` in those symbols, kept in
a normal form described below.

Above that sits the closed function list, issue #40. Each admitted function
appears as a symbol applied to an argument, and this record places two
requirements on that list which the parser issue has to satisfy rather than
choose.

The list is closed under differentiation. The algorithm differentiates
repeatedly, so a list containing a function whose derivative is not expressible in
the list would leave the domain on the first covariant derivative, and the domain
it left for would be undeclared.

Every relation the project relies on among the admitted functions is declared as
a rewrite to a normal form, and no relation is relied on that is not declared. The
Pythagorean relation between `sin` and `cos` is the one the first record in the
tree needs, since `r^2*sin(theta)^2` is in the worked Schwarzschild metric of
record 0003.

Named constants from the closed constant list are transcendental symbols with no
declared relations, which is sound for `pi` and is what makes the field they
generate a rational function field rather than something harder. The cost is
stated in the residual section below, because a normal form that treats `pi` as a
symbol does not know that `sin(pi)` is zero.

Free functions of the coordinates, which a family in the literature may carry,
are admitted as function symbols with no relations. Their derivatives enter as
further independent symbols, so a free function `f` of one coordinate contributes
`f`, `f'`, `f''` and as many more as the differentiation order reaches, each
independent of the others.

Algebraic extensions are entered as late as possible and, for the discrete steps
this board takes, are not entered at all. That is the next section.

### The Petrov type does not need the roots

The quartic whose roots are the principal null directions is written in record
0002. Its root multiplicity pattern is what the Petrov type is, and a
multiplicity pattern is obtainable from the coefficients alone, through the
greatest common divisor of the quartic and its derivative and the vanishing of
subresultants, without isolating or representing a single root.

So the classification does not construct the splitting field of the quartic. It
computes a small number of polynomial expressions in the five Weyl scalars and
applies a zero test to each. Every one of those expressions lives in the rational
function field above, and the arithmetic that decides the Petrov type is the
arithmetic of that field and nothing wider.

This matters for two reasons beyond cost. An algebraic number field over a
rational function field in several variables is where an exact implementation
becomes genuinely hard, and staying out of it keeps the zero test in a place
where it is a decision procedure. And a root of a quartic written as a radical is
a representation with a branch choice in it, and a branch choice in an
intermediate value is a place a classification could depend on something nobody
declared, which record 0012, issue #21, refuses.

Where an eigenvalue is genuinely needed rather than a multiplicity, for instance
in the Ricci classification in issue #47 if it is formulated through
characteristic roots, the same route applies first: the type is read from
multiplicities and invariant factors of the characteristic polynomial, and a root
is represented by its minimal polynomial over the coefficient field if one is
ever needed, never by a radical expression.

### The zero test

The zero test is a total normalisation, not a simplifier.

An expression is reduced to a quotient of two expanded polynomials over `Q(i)` in
one alphabet: the coordinates, the parameters, the named constants, the applied
function symbols after the declared rewrites, and the free function symbols with
their derivatives. The numerator is zero or it is not, and that is the answer.

On that class the test is a decision procedure, and the phrase is used in its
strict sense: the procedure terminates and its answer is correct, for every input
in the class. Record 0010 chose a normal form rather than a canonical form for
the pipeline, and this is the sentence that record was written to sit underneath.
Zero is recognisable here, which is all the algorithm asks, and on the subclass
where the alphabet carries no free function symbols the normal form is in fact
canonical, so 0010's simplification points do not move either way.

The software can tell a decision from a hope, and that is a property of the
implementation rather than a hope about it. The zero test returns one of three
values, `zero`, `nonzero` and `undetermined`, and the third is returned only
where the section below says it can be. A heuristic simplifier is never consulted
by a zero test. Where cheap reduction is wanted for size, that is record 0010's
unconditional normalisation point, and its output is fed to the same total
normalisation before any branch is taken on it.

A cheap filter runs before the full normalisation and can only refuse equality.
The expression is evaluated at a fixed pseudo-random rational point modulo a
large prime. A nonzero result proves the expression is not identically zero, and
the branch is taken with no full normalisation performed. A zero result proves
nothing and the full normalisation runs. The filter is exact arithmetic in a
finite field and not floating point, its point and prime are derived from a seed
fixed by record 0012, and it can change what a run costs but not what it answers.

### Where it is undecidable, and what happens

Two different things are called undecidable here and keeping them apart is the
point of this section.

The structural question, whether the expression as written is the zero element of
the field described above, is decided. It is the procedure of the previous
section.

The intended question, whether the expression vanishes for the particular unknown
function or on the particular subset of parameter space a record means, is not
decidable in general. A free function symbol `f` is not the zero element, and
whether the metric a physicist has in mind has `f'' = 0` on part of its domain is
not a question about the syntax. This is where a general zero test over the
expressions record 0003 admits stops being available, and no amount of
implementation effort moves the line.

Three responses, and the software takes each in a stated circumstance rather than
choosing per call site.

A case split, where the branch depends on whether one expression vanishes and the
number of open expressions is at or below a declared limit. The run proceeds down
each branch and the classification record carries every branch with the condition
that selects it. This is the honest answer and it is also the expensive one,
which is why it is bounded.

An assumption supplied by the caller, where a split is available but the branch
count would exceed the limit, or where the caller already knows which case they
mean. The caller passes conditions, the run proceeds under them, and each one is
recorded as assumed rather than proved.

A refusal, where neither is available: no split within the limit and no assumption
covering the open expression. The run stops and reports which expression it could
not decide, at which order, and in which frame. It does not pick a branch and it
does not report a classification.

Under no circumstance is an undetermined zero test treated as `zero`, and the
reason is worth writing where somebody is tempted. Treating an undetermined test
as zero is what produces a Petrov type that is too special, an isotropy dimension
that is too large, and a termination one order too early, and every one of those
is a wrong classification that reproduces perfectly on rerun.

### The field that records an assumption

Every assumption is recorded in a field named `assumption`, a list, and each entry
carries the expression as written, which side of the zero test was assumed, where
the assumption came from, and the differentiation order and frame it was applied
at. An empty list is the normal case and is what a run with no free functions
produces.

An assumption is not evidence, and the list is what stops it being read as
evidence. A classification produced under a non-empty `assumption` list is
published with the list attached, and a consumer comparing two classifications
compares the lists too: two records that agree on every invariant under different
assumptions have not been shown to be equivalent.

Where that field sits in the value returned to a caller is record 0008, issue #15,
which has not landed. What this record fixes is the field's name, its contents,
and that no route publishes a value computed under an assumption without it. The
derived entry in record 0003 carries the same list beside the command, the commit
and the date, because a derived value computed under an assumption and one proved
outright are not the same claim, and record 0006's four verification states are a
closed vocabulary this record does not widen.

A case split is not an assumption and does not populate the list. A split has
proved every branch and stated the condition for each; nothing was taken on
trust.

### Floating point

Floating point does not appear in the classification path at all.

Not as a filter, not as a pre-test, not as a heuristic ordering. The cheap filter
described above is exact arithmetic in a finite field, which does the job a
floating point filter would have been reached for and does it with a proof
attached.

The one place a floating point number appears in an artefact of this project is a
cost measurement: a wall clock in seconds, a peak memory in bytes. That is a
measurement of a run rather than arithmetic on a geometry, it is recorded per
record 0006 on the verification entry, and no branch is ever taken on it.

If a floating point path is ever added, it may only refute equality and never
establish it, and it would need the interval or error bound that turns a
refutation into a proof. There is no such path today and this record does not
open one.

### What would show this was wrong

No measurement stands behind the choices here. There is no code in this
repository yet, so nothing has been run and no number is quoted.

The claim that a run could falsify is that total normalisation is affordable at
the orders the algorithm reaches. The run that decides it: classify one expensive
entry with the cheap filter enabled and disabled, and record the count of full
normalisations, the largest numerator node count, and the peak memory per order.
If the total normalisation dominates the run so heavily that the entry does not
finish where a heuristic simplifier would have, then the choice is not wrong but
its cost is the reason entries fall outside the ceiling, and that belongs in the
cost table in issue #70 rather than in a quiet switch to a simplifier.

The claim about the filter is that it saves work. If the count of full
normalisations avoided is a small fraction of the total, the filter is complexity
with no return and should go.

## Rejected alternatives

Floating point anywhere in a branch, as a fast path with an exact fallback.
Rejected because the fallback is the whole cost and the fast path buys nothing
that the finite field filter does not buy with a proof attached. A tolerance is
also a number somebody has to choose, and a classification that depends on a
tolerance depends on that choice rather than on the geometry.

A heuristic simplifier as the zero test. Rejected because its two answers are
"this is zero" and "I could not make it zero", and it reports them identically. A
branch taken on the second is the confident wrong classification this record is
built against, and the report would look the same as a correct one.

A canonical form for the whole admitted class. Rejected as unavailable, for the
reason record 0010 already gives: once the closed function list and free
functions are admitted, a canonical form would have to decide the intended
question above, and nothing does.

Constructing the splitting field of the quartic so that the roots are available.
Rejected because the Petrov type is a multiplicity pattern, which the coefficients
answer, and because an algebraic extension of a multivariate rational function
field is where an exact implementation becomes hard for no gain here. Radical
expressions for roots are rejected additionally because a branch choice inside a
representation is a hidden dependency record 0012 refuses.

Admitting arbitrary transcendental constants with declared relations. Rejected
because the relations are what make the field hard, the closed constant list is
short, and a record needing a constant not on the list is a change to the list and
therefore to this record, which is the visible route.

Refusing every record that carries a free function. Rejected because it would
exclude a large part of the reference literature, and the families with free
functions are not a fringe case. The three responses above are the price of
admitting them.

Branching on both possibilities always, with no limit. Rejected because the
branch count is exponential in the number of open expressions, so an unbounded
split turns a classification into a search that does not finish and reports
nothing, which is the outcome the declared budget in record 0011, issue #20,
exists to convert into a refusal.

Asking the caller for an assumption as the first response rather than the second.
Rejected because a caller asked for an assumption will supply the one that makes
the run finish, and a case split needs nothing from anybody. Where both are
available the split is the answer that carries its own evidence.

Recording assumptions in a log rather than in a field on the record. Rejected
because a log is not loaded with the record, so a consumer would compare two
classifications without knowing that one of them rests on something unproved.

## What depends on this

Record 0002, which chose the complex tetrad this record's ground field follows
from, and whose quartic is what the multiplicity argument above is about.

Record 0003, whose expression sub-language this record fixes the arithmetic of,
and whose derived entry carries the `assumption` list.

Record 0005, which named this record as the reason a record's stratum coverage is
an asserted claim rather than a check, and whose automatic stratum discovery was
rejected on the limits set out here.

Record 0006, whose four verification states are closed and are not widened by
this record. An assumption travels as a field, not as a fifth state.

Record 0007, issue #13, whose family comparison returns the undetermined answer
where the parameter map can neither be found nor ruled out, which is this record's
line.

Record 0008, issue #15, which fixes where the `assumption` list sits in the value
a caller receives, and which has not landed.

Record 0010, whose normal form is defined against the procedure here, and whose
three simplification points feed the zero test rather than replacing it.

Record 0012, issue #21, which fixes the seed the cheap filter derives its point
and prime from, so that the filter changes cost and never an answer.

Issue #40, the expression parser and its closed function and constant lists,
which owes two properties this record requires: closure under differentiation, and
a declared relation set with a rewrite to normal form.

Issue #46 and issue #47, the Petrov and Ricci classifications, which are the
first consumers of the multiplicity route.

Issue #53 and issue #54, the bookkeeping and the termination test, whose ranks and
dimensions are stacks of zero tests, and which are where an undetermined test
becomes a refusal rather than a guess.

Issue #56, the classification record a finished run writes, which carries the
`assumption` list and the branch conditions of a case split.

Issue #90, the fuzzing of the loader and the expression parser, which is where the
normalisation meets input nobody wrote by hand.

Issue #91, the property suite, which is where the claim that the cheap filter
cannot change an answer is tested rather than asserted.
