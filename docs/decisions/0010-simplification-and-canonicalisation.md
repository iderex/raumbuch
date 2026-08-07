# 0010. Simplification and index canonicalisation

## Status

Accepted

## Date

2026-08-07

## Question

The cost of the whole algorithm is dominated by expression growth between
differentiation orders, and the difference between an entry that fits in memory
and one that does not is usually a simplification decision rather than an
algorithmic one.

Where does simplification run? What normal form is targeted, and is it canonical
or not? Are intermediate results stored or recomputed? And where does index
canonicalisation happen, given that a sibling board, `indexwerk`, is building
exactly that behind a C interface?

## Answer

### Three simplification points, and only three

A cheap normalisation runs unconditionally on every component produced by a
covariant derivative or a frame transformation. It puts coefficients into a
rational normal form, collects like terms, and applies only the rewrite rules
that reduce size unconditionally. Its cost is bounded and it never searches.

A full reduction runs on a single component when that component's node count
crosses a declared threshold, and on nothing else. This is the point that stops
one runaway expression from carrying the whole run, and it is targeted so that
the cost is paid where the growth is rather than across the whole frame.

A full reduction runs across the whole set once at the end of each
differentiation order, before the invariants of that order are read off. That is
the one place where a result is consumed instead of being fed forward, so it is
the one place where the effort spent on a smaller form is not thrown away by the
next derivative.

The threshold is a declared number rather than a constant buried in the code, and
the sweep that would show it is the wrong lever is written down below.

### A normal form, not a canonical form

The target is a normal form. Zero is recognisable; two expressions that are equal
may still differ.

The algorithm consumes ranks and multiplicities. Root multiplicities of the Weyl
characteristic polynomial for the Petrov type, the rank of a matrix of invariants
for the isotropy dimension, the rank of a Jacobian for the number of functionally
independent scalars. Every one of those is a question about which things are
zero, and none of them asks whether two representations are identical.

A canonical form is not available in general over the expression class a record
may hold. Once the closed function list admits transcendental functions, whether
two expressions are equal is the general zero problem, and a canonical form would
have to decide it. Record 0009, issue #17, is where the arithmetic and the
practical zero test are decided, and this record is written to sit underneath
whatever it chooses: if 0009 restricts the admitted class to one on which the
zero test is a decision procedure, then on that class the normal form here is
canonical without any simplification point moving. The dependency runs one way
and this record does not pre-empt it.

### The storage trade

Intermediate results are stored, not recomputed: one hash-consed store of
subexpressions stays alive across all differentiation orders, trading memory for
time on the argument that at the orders that hurt the growth is in the number of
distinct subexpressions rather than in the size of any one of them, so
recomputing a connection component at order three costs more than holding it.

That is a direction, and the run that would show it is backwards is below.

### Index canonicalisation

This board takes no hard dependency on `indexwerk`.

The critical path of this algorithm computes with components in a fixed frame,
and a component is a scalar with no free indices, so canonicalising a tensor
expression under its index symmetries is not on it. Where an index expression
does arise, what is needed at the orders reached is the monoterm symmetries of
the Riemann tensor and the first Bianchi identity, and a small canonicaliser in
this tree covers exactly that.

That argument leans on the frame formalism, which is record 0002, issue #7, and
which has not landed. It holds across the formulations that decision is choosing
between, because all of them compute in components. If 0002 chooses a
formulation that carries free indices through the differentiation, this record
has to be revisited, and that is written into the dependencies below rather than
assumed away.

`indexwerk` is admitted behind an optional interface, never as a build
requirement. What happens to this board when it is unavailable, which is the
default state: the build passes, the gate passes, and every classification
produces the same answer, because the algorithm consumes ranks and
multiplicities rather than representations. Only the cost table changes. The
sentence about the answers being the same is a property to be tested by the suite
in issue #91, not an assertion made here.

The dependency was declined rather than deferred, and the reasons are that it
couples this board's release to another board's, that a C interface adds a
foreign-function surface and a build toolchain that record 0001, issue #5, would
have to price, and that it buys speed on a path this algorithm does not spend its
time on.

### What would show each choice was wrong

No measurement stands behind any of the three choices. There is no code in this
repository yet, so nothing has been run and no number below is a result. These
are the runs that would decide, written down now so a later run can falsify the
choice instead of arguing with it.

For the threshold. Sweep it over three decades on one entry, and record peak
resident memory and wall clock per differentiation order. If peak memory varies
by less than a factor of two across the whole sweep, the threshold is not the
lever, and the cost is in the unconditional cheap point instead.

For the storage trade. Run one entry with the shared store enabled and disabled,
and record peak memory and wall clock for each. If disabling the store lowers
peak memory and does not raise wall clock by at least a quarter, the trade is
backwards and the store should go.

For the canonicalisation choice. Count the index expressions that reach the
in-tree canonicaliser during a full catalogue run, and the time spent inside it.
If either is a measurable fraction of the run, the claim that canonicalisation is
off the critical path is wrong and the `indexwerk` question reopens on evidence.

The entry these run on should be one that is expensive rather than one that is
convenient. Issue #74 is where the catalogue gets entries chosen to exercise the
classification, and the cost table in issue #70 is where the numbers land.

## Rejected alternatives

Full simplification after every operation. Rejected because it is the standard
way a symbolic pipeline spends its whole budget: most of those expressions are
about to be differentiated again and discarded, and the effort spent making them
small is paid on every one of them and recovered on few.

No simplification until the end. Rejected because the end is not reached.
Intermediate growth between orders is the thing that exhausts the machine, and a
strategy that only acts after it is over has acted after the process was killed.

Simplification driven purely by expression size, with no unconditional point.
Rejected because the cheap normalisation is what keeps the size measurement
meaningful; without it the node count is dominated by uncollected like terms and
the threshold trips on noise.

A canonical form as the target. Rejected as unavailable in general over the
admitted expression class, for the reason above, and unnecessary, because the
algorithm asks only which things are zero.

Recomputing intermediate results instead of storing them. Rejected in the
direction stated above, and it is the alternative the falsifying run tests, so
this rejection is the one most likely to be revisited on evidence.

A hard dependency on `indexwerk`. Rejected for the release coupling, the foreign
function surface and the fact that the work it accelerates is not where this
algorithm spends its time.

Vendoring a narrowed copy of `indexwerk`. Rejected because a vendored
canonicaliser is a fork that receives neither the upstream fixes nor this
project's attention, and because the piece actually needed here is smaller than
the vendoring would be.

No canonicalisation at all. Close to what was chosen and rejected in its pure
form, because the first Bianchi identity is the one relation whose absence shows
up early as expression size that nothing else removes.

## What depends on this

Record 0002, issue #7, in the other direction: if the frame formalism carries
free indices through the differentiation, the canonicalisation argument here does
not hold and this record is revisited.

Record 0009, issue #17, which fixes the arithmetic and the zero test that the
normal form here is defined against.

Issue #52, covariant differentiation to the next order, which is where the three
simplification points are implemented.

Issue #67 and record 0011, issue #20, which measure and bound what this record
trades.

Issue #70, the published cost table, which is where the falsifying runs above are
reported.

Issue #72, the one measurement-driven reduction of the peak, which is the issue
this record is trying to keep honest: a reduction chosen without one of the
measurements above is the thing that issue refuses.

Issue #91, the property suite, which is where the claim that the optional
canonicaliser does not change an answer is tested rather than asserted.
