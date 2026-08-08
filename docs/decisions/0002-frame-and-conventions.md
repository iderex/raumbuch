# 0002. Frame, signature and conventions

## Status

Accepted

## Date

2026-08-08

## Question

Every array the algorithm carries has a shape, and that shape is not a
consequence of the mathematics alone. A curvature component means nothing until
somebody says which frame it is a component in, which sign convention the Riemann
tensor was defined with, and which index sits where. A record already carries a
`signature` field, so the question is being answered by implication whether or
not it is written down.

Which frame formalism does the algorithm compute in? What is the metric
signature and the normalisation of the frame? What sign conventions fix the
Riemann tensor, the Ricci tensor and the field equations? Where do coordinate
indices stop and frame indices start? And which spacetime dimension does this
board support?

## Answer

### A complex null tetrad, in the Newman-Penrose scalars

The algorithm computes in a complex null tetrad `(l, n, m, mbar)` and consumes
the curvature through the Newman-Penrose scalars: the five complex Weyl scalars
`Psi_0` to `Psi_4`, the Ricci scalars `Phi_00` to `Phi_22` with the trace part
`Lambda`, and the twelve complex spin coefficients.

The reason is the discrete step this whole board turns on. Deciding a Petrov type
is deciding the root multiplicity pattern of the quartic

```
Psi_4*z^4 + 4*Psi_3*z^3 + 6*Psi_2*z^2 + 4*Psi_1*z + Psi_0
```

whose roots are the principal null directions. A multiplicity pattern is a
question about which of a small number of polynomial expressions in the
coefficients vanish, and record 0009, issue #17, is where the procedure that
answers such a question exactly is fixed. In a real orthonormal frame the same
question arrives as a degeneracy condition on an operator built from the Weyl
tensor, which is the same information reached through a longer route.

The spinor dyad is not a competing choice here. The Newman-Penrose scalars are
the components of the Weyl spinor and the Ricci spinor in a dyad, so choosing the
tetrad and choosing the dyad fix the same numbers. What the tetrad choice fixes
in addition is that the input boundary speaks tensors, which is what a record
holds.

The frame freedom is the six real parameters of the Lorentz group, and in this
formalism it arrives already split into the three stages the canonical frame
fixing in issue #51 uses. A null rotation about `l` with one complex parameter, a
null rotation about `n` with one complex parameter, and a boost in the `l`, `n`
plane with a spin in the `m` plane with one real parameter each. Two plus two
plus two is the six, and the count is worth stating because the isotropy
dimension the algorithm records at each order is a dimension inside this group.

### Signature and normalisation

The signature is `-+++`. One timelike direction with a minus sign, three spacelike
with a plus.

That was already fixed in practice rather than in principle. Record 0003 landed a
worked Schwarzschild record whose `signature` field reads `-+++` and whose `tt`
component reads `-(1 - 2*M/r)`, so a different answer here would have invalidated
the first record in the tree. Writing it down is what turns that from an accident
into a decision.

The tetrad is normalised so that

```
l.n = -1        m.mbar = 1
```

and every other inner product among the four legs vanishes. Equivalently

```
g_ab = -l_a*n_b - n_a*l_b + m_a*mbar_b + mbar_a*m_b
```

The two statements are one statement, and both are written because the second is
what the implementation checks a constructed tetrad against and the first is what
a reader compares against a paper.

This normalisation is not the one the formalism was first published in. With a
`+---` signature the usual normalisation is `l.n = 1` and `m.mbar = -1`, and
several signs in the published field equations follow from that choice rather
than from the geometry. The consequence for this board is a rule about how the
connection is obtained, in the next section, because a set of transcribed
equations under one convention silently reinterpreted under another is a defect
this repository has no cheap way to find.

### Curvature signs

Three independent sign choices, each fixed here.

The Riemann tensor is defined by the Ricci identity in this order:

```
(Nabla_c Nabla_d - Nabla_d Nabla_c) V^a = R^a_bcd * V^b
```

The Ricci tensor is the contraction on the first and third slots:

```
R_ab = R^c_acb
```

The field equations are written with the Einstein tensor on the left and
geometric units `G = c = 1`:

```
R_ab - (1/2)*R*g_ab + Lambda_cc*g_ab = 8*pi*T_ab
```

where `Lambda_cc` is the cosmological constant, spelled out rather than written
`Lambda` because `Lambda` is already the trace part of the Ricci scalars in this
formalism, and one symbol carrying two meanings inside one convention record is
exactly the confusion the record exists to remove.

A vacuum solution has `R_ab = 0` under every one of those sign choices and their
negatives, so a vacuum entry cannot detect a convention applied backwards. What
distinguishes this set from its negatives is the sign of the Ricci scalar on a
geometry whose Ricci curvature does not vanish, and issue #49, the verification
corpus, owes at least one such entry for that reason and owes the sign it
expects, written down, rather than left to whichever way the first run came out.

### The connection is derived, never transcribed

Spin coefficients and the Newman-Penrose field equations are computed from the
tetrad and the Levi-Civita connection by their definitions. No published set of
equations is copied into this tree.

This costs a slower and less familiar implementation and it removes a defect
class with no other defence. The eighteen field equations plus the Bianchi
identities are dense in signs and index positions; a transcription error inside
them produces a classification that is confidently wrong for a subset of
metrics, and the subset is not the one anybody tests first. Deriving them means
the only convention in the tree is the one written above.

Published equations remain what the result is checked against. Issue #49 is where
that check lives, and the comparison is between a computed classification and a
published classification of the same metric rather than between two sets of
symbols.

Every entry in the verification corpus records the convention its published
source used and what was done to reconcile it. A corpus entry that agrees with a
paper without saying which convention the paper worked in is evidence about
nothing, and a sign convention reconciled silently once is reconciled wrongly
somewhere else.

### Indices, and where the transition happens

Coordinate indices are Greek and frame indices are Latin. A frame index runs over
the four legs in the fixed order `l`, `n`, `m`, `mbar`, and that order is part of
this decision because it is the order every stored component tuple is read in.

The transition happens once, at order zero, in one place. The loader produces
metric components in the coordinates a chart declares, which is coordinate
indexed by record 0003. Issue #51 builds an initial tetrad from those components,
and from that point on every array the algorithm carries is frame indexed and
every derivative is one of the four directional derivatives `D = l^a Nabla_a`,
`Delta = n^a Nabla_a`, `delta = m^a Nabla_a` and its conjugate.

Coordinate indices reappear in exactly two places, and both are outputs. The
Killing vectors in issue #57 are reported in the coordinates of the chart they
were computed in, because a reader wants a vector field in the coordinates they
wrote the metric in. The tetrad itself is reported in the same coordinates, since
it is what realises a match and the report in record 0007, issue #13, promises it
where it can be produced.

Nothing in the middle carries a coordinate index. That is what record 0010's
argument about index canonicalisation rests on: a component in a fixed frame is a
scalar with no free indices, so canonicalising a tensor expression under index
symmetries is not on the critical path. This record is the one 0010 named as
possibly overturning that argument, and it does not: the differentiation carries
no free indices.

### Four dimensions, and only four

This board supports four-dimensional spacetimes. The code is not
dimension-general and does not pretend to be.

The classification scheme is dimension specific rather than merely tuned. In four
dimensions the Weyl tensor has ten independent components which pack into five
complex scalars, and the Petrov classification is the multiplicity pattern of a
quartic with exactly six possible patterns. In three dimensions the Weyl tensor
vanishes identically and the classification is carried by the Cotton tensor
instead. In five dimensions the algebraic classification is a different scheme
with a different set of types, and the quartic does not exist.

What would have to move to support a second dimension, at the level of modules.

The frame module, issue #51, which constructs the tetrad and holds the leg count
and the normalisation.

The curvature module, issues #44 and #45, whose component packing into
`Psi` and `Phi` is four-dimensional and which would need a per-dimension
representation of the Weyl part.

The Petrov module, issue #46, which is a quartic root multiplicity routine and
would be replaced rather than parameterised.

The frame group action, issue #48, since the staged null rotation and boost
decomposition above is the structure of the six-parameter Lorentz group in four
dimensions.

The record schema, issue #35, whose `dimension` field is currently a value the
loader may as well refuse when it is not 4, and the loader in issue #36, which
should refuse it rather than accept a record nothing downstream can classify.

The bookkeeping in issue #53 and the termination test in issue #54 do not move.
Isotropy dimension and functionally independent count are dimension independent
statements, and that is the boundary a later dimension effort would work from.

### What would show this was wrong

No measurement stands behind the formalism choice. There is no code in this
repository yet, so nothing has been run.

The claim this record makes that a run could falsify is that the discrete steps
are cheaper to decide exactly in this formalism than in a real orthonormal frame.
The run that decides it: classify the same entry through both, and compare the
node count of the largest expression a zero test is applied to, and the count of
zero tests taken, at each order. If a real frame reaches the same Petrov type
with fewer or smaller tests, the reason given above is wrong and the trade
reopens. Issue #70 is where a number like that gets published.

The claim about a transcription defect class is not falsifiable by a run, and it
is a judgement rather than a measurement. It is written as the reason for a rule
and not as a result.

## Rejected alternatives

A real orthonormal frame. It would have made three things easier, and each is a
real cost of the choice above. Reality conditions on parameters stay statements
about real expressions, where in a null tetrad a reality condition becomes a
statement relating an expression and its conjugate. Every component is real, so
the arithmetic layer needs no complex extension, which is a domain record 0009
now has to carry. And the six-parameter Lorentz action is the one most readers
have met, so a canonical frame fixing written in it is easier to check by eye.
Rejected because the Petrov type, which is the first discrete branch the
algorithm takes, arrives as a root multiplicity pattern in the null tetrad and as
a degeneracy condition on a derived operator in the orthonormal frame, and an
exact answer is cheaper from the first shape.

A spinor dyad as the primary representation. Not rejected as mathematics, since
it fixes the same numbers as the tetrad. Rejected as the primary representation
because the input boundary is a record holding a metric in coordinates, so a
dyad-first implementation puts a translation layer at the point where records
arrive rather than at the point where curvature is classified, and the first is
the boundary a hand-written record is most likely to be wrong at.

Both a null tetrad and an orthonormal frame, chosen per entry. Rejected because
it doubles the corpus that has to be verified while adding no classification the
project can otherwise not reach, and because the first entry classified in the
wrong one of the two would be indistinguishable from a correct one.

The `+---` signature with the original normalisation. Attractive for exactly one
reason, that published Newman-Penrose equations could be read straight across.
Rejected because the tree already landed a record and a worked metric under
`-+++`, so taking it would mean rewriting a landed record, and because the
connection is derived rather than transcribed, which is what the reading-across
would have bought.

A signature flag on the record, so that either convention may be written.
Rejected because a per-record convention means every comparison between two
records has to reconcile two conventions before it can begin, and the comparison
is the deliverable. One convention in the tree, and a transformation applied once
at transcription time, puts the reconciliation where a human is already reading a
paper.

Transcribing the published field equations for speed, with a test comparing them
against a derived version. Rejected because the test is the derivation, so the
transcription buys nothing after the derivation exists, and because a test
comparing two implementations of the same equations passes when both carry the
same misread sign.

Dimension-general code from the start. Rejected because the classification scheme
is not dimension general, so what would be general is the plumbing and not the
mathematics, and a module named as dimension general that only works at four is a
claim in an identifier where nobody looks for one.

Deciding the dimension later. Rejected because the packing of the Weyl tensor
into five complex scalars is in every array the algorithm carries, so a later
answer is a rewrite of the layer everything else sits on.

## What depends on this

Record 0003, whose `signature` field this record fixes and whose worked record
was already written under it, and whose `dimension` field this record bounds
to 4.

Record 0009, issue #17, which has to carry a complex extension of the rational
domain because the scalars this record chooses are complex, and which fixes the
procedure the root multiplicity pattern above is decided by.

Record 0010, which named this record as able to overturn its index
canonicalisation argument. It does not. The differentiation carries frame
components with no free indices, so the argument holds and `indexwerk` stays an
optional interface.

Record 0007, issue #13, whose report promises the frame that realises a match,
which is a tetrad in this formalism and is reported in chart coordinates.

Issues #44 and #45, the curvature computation, which produce exactly the scalars
named here.

Issue #46 and issue #47, the Petrov and Ricci classifications, whose input is the
scalar set and whose discrete step is the multiplicity pattern above.

Issue #48, the frame group action, which implements the six parameters in the
three stages named here.

Issue #49, the verification corpus, which owes at least one entry with
non-vanishing Ricci curvature, because a vacuum entry cannot detect a
misapplied curvature sign convention, and which records the convention of every
published source it compares against.

Issue #51, which builds the initial tetrad and is where the one coordinate to
frame transition happens.

Issue #57, the Killing vectors, which are reported back in coordinate indices.

Issue #35 and issue #36, the schema and the loader, which should refuse a
`dimension` other than 4 rather than accept a record nothing can classify.

Revisiting the formalism is a rewrite of milestones 4 and 5. Revisiting the
signature is a rewrite of every landed record. Both are cheapest today and the
second is already not free.
