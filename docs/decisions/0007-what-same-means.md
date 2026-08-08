# 0007. What "the same solution" means

## Status

Accepted

## Date

2026-08-08

## Question

The deliverable is a function that answers whether a metric is already in the
catalogue. The value of that answer depends entirely on what "already in the
catalogue" is taken to mean, and a reader will take it to mean the largest thing
the sentence can carry. If the software says two metrics are the same and a
reader concludes more than was decided, this project has produced a confident
wrong answer, which is worse than the paper status quo it replaces.

What relation does a positive answer assert? What does it not assert, in
particular where somebody will assume it does? Does a constant rescaling of the
metric preserve it, and does a constant conformal factor?

## Answer

### The relation is local isometry

Two metrics are the same solution here when they are locally isometric: there is
a diffeomorphism between a neighbourhood in one and a neighbourhood in the other
that carries one metric tensor to the other exactly.

That is the relation the Cartan-Karlhede algorithm decides, and this record does
not widen it by a word. The algorithm compares the Cartan invariants, which are
the frame components of the curvature and its covariant derivatives in a frame
fixed by the curvature itself, and their agreement as functional relations is
equivalent to local isometry. Everything below is the consequence of choosing
that relation rather than a larger one.

### The two paragraphs that are quoted verbatim

These two paragraphs are the text that the operator documentation, issue #99, the
`README`, and the report `is_this_new` returns all carry. They are quoted from
here and never paraphrased, because three documents restating one limitation in
three voices is three chances for one of them to be reassuring.

The positive paragraph:

```
A positive answer means the two metrics are locally isometric. On some
neighbourhood of each, there is a coordinate change carrying one metric to the
other exactly, and the answer names the invariants that agree and, where it can
be produced, the frame that realises the match. It is a statement about the
geometry of a neighbourhood and about nothing larger.
```

The limiting paragraph:

```
A positive answer does not say the two spacetimes are the same manifold, that
either is the maximal extension of the other, that a singularity in one chart is
physical, that the two carry the same matter interpretation, or that either
metric is correct. The algorithm never sees the topology, the extension or the
physics; it reads local invariants and it is silent about everything that is not
one.
```

Both blocks are fenced so that the text a consumer sees is byte-identical to the
text argued for here.

### What a positive answer does not cover, in full

The two paragraphs above are short because they are quoted. The list they compress
is this one, and every item on it is something somebody will assume.

Global sameness. The algorithm sees a neighbourhood. Two spacetimes with
identical Cartan invariants at every point can be different manifolds, because
the invariants are local data and the topology is not recoverable from them.

Maximal extension. Schwarzschild in the static exterior chart and Schwarzschild in
Kruskal coordinates are locally isometric on the region they share and are not
the same object. Record 0005 already fixed that both are charts of one entry, so
inside the catalogue this case is handled by construction; across a query and an
entry it is not, and the answer stays a local one.

Whether a singularity is physical. Whether a locus where a chart breaks down is a
curvature singularity of the spacetime or an artefact of the coordinates is a
question about the extension. Record 0005 makes a record say which it believes
each of its own boundaries to be, as an assertion. Nothing here computes it.

Matter interpretation. One metric can be presented as a vacuum solution and as a
solution with a particular stress-energy tensor, and those are the same geometry
with different physics attached. Record 0003 keeps `matter.model` in the asserted
block for that reason. Two records that differ only in `matter.model` are the
same solution under this record and are different entries in the catalogue, and
the report says so rather than hiding one of them.

Whether either metric solves anything. Local isometry to a catalogue entry says
nothing about whether the field equations hold. That is the separate derived
field `field_equations_hold`, issue #50, and a positive equivalence answer for a
metric that solves nothing is a correct answer to the question that was asked.

Correctness of the entry that matched. A match against a transcribed record
inherits that record's verification state and no more. Record 0006's markers
travel with the answer, so a match against a value no computation here has
confirmed is reported as such.

Equivalence of families rather than of members. Record 0005 fixed that a record
holds a family, that comparison runs per stratum, and what happens to a query
that still carries free parameters. This record fixes the relation being compared
and leaves that machinery where it is.

### A constant rescaling is not the same solution

Multiplying a metric by the square of a positive constant, `g -> k^2*g` with `k` a
number, produces a different solution in this catalogue.

The reason is that it is not an isometry. It is a homothety, and the invariants
the algorithm reads change under it: a curvature scalar of dimension length to the
minus two is divided by `k^2`. Calling the result the same solution would mean
answering a question nobody asked with the answer to a question they did ask.

The consequence is worth stating in the direction that stings. Schwarzschild is
scale covariant, so Schwarzschild with mass `M` and Schwarzschild with mass `2*M`
are related by a constant rescaling together with a coordinate change. Under this
record they are two members of one family and not one geometry, and a query for
one of them does not match the other. That is correct. The mass parameter is
measurable, the invariants distinguish it, and a catalogue that collapsed it could
not answer what the mass of a matched entry is.

Whether the comparison also detects that two inputs are related by a homothety is
not promised here. It is a different relation, it needs its own machinery, and
issue #62 is where the separating invariant a negative answer has to show is
decided. If it is ever added, it is an additional field on the report and never a
change to the verdict.

### A constant conformal factor is the same operation, and the parameter case is not

A conformal factor that is a constant on the manifold is the constant rescaling
above, so it gets the same answer. Writing the two questions separately is worth
one paragraph, because the interesting case hides between them.

A factor that is constant on the manifold but built from the record's parameters,
so that it varies from member to member of one family, is not a rescaling of a
geometry. It is a reparameterisation of a family. Two records where one is the
other with `M` replaced by `2*M`, or with the parameters renamed, hold the same
set of geometries, and this record fixes that they are the same family. A
comparison that reported a new solution because somebody wrote `a = 2*b` would be
reporting a difference in notation as a difference in physics.

What that costs is that the family comparison in issue #59 has to look for a map
between the two parameter domains rather than for equality of the domains, and it
has to report which map it found. Where it cannot find one and cannot rule one
out, the answer is the undetermined one rather than a negative, for the reason
record 0009, issue #17, gives about which questions over these expressions are
decidable.

A non-constant conformal factor is a third thing and is out of scope. Conformally
related spacetimes are a real and useful relation, they are not local isometry,
and nothing in this project decides them. A record whose metric differs from
another's by a non-constant factor is a different solution here.

### Where the wording is enforced and where it is not

The three places that carry the two paragraphs above are the operator
documentation, the `README` and the runtime report, and nothing in this
repository refuses a fourth place that paraphrases them. That is a real gap and
it is worth naming rather than assuming the rule will hold: the quoted blocks are
a convention until a check reads them out of this record and compares them to the
copies, which is the same shape as the section list in record 0000 and the same
argument for it.

Issue #99 is where the operator documentation lands and is where the copy is
first made. Issue #31 is the check over decision records and does not cover this.
No issue covers it today, and this sentence is the disclosure rather than a plan.

## Rejected alternatives

Isometry rather than local isometry. Rejected because it is not what the
algorithm decides, so promising it would mean promising an answer the software
cannot produce. The honest version of wanting it is the limiting paragraph above.

Diffeomorphism equivalence, so that any two metrics related by a coordinate change
of the manifold count. Rejected because it is the same relation as local isometry
once the metric is carried along, and reading it as a relation on manifolds alone
would make every four-dimensional spacetime equivalent to every other, which is
the relation with no content.

Conformal equivalence. Rejected because it answers a different question and
because the field this board serves asks whether a solution is new, not whether
it is conformally related to a known one. A conformal classification is a
separate project that would reuse the catalogue.

Homothety, so that a constant rescaling counts as the same solution. Rejected in
the section above. It would collapse the mass parameter of the most cited entry in
the catalogue, and the answer to "which entry is this" would stop determining the
scale of the geometry it names.

Equivalence up to a constant conformal factor for vacuum entries only, where the
factor is unobservable. Rejected because a relation that holds for a subset of
entries is a second relation, and a consumer cannot see from a verdict which one
they were given.

Equivalence including the matter interpretation, so that two records with
different `matter.model` are different solutions. Rejected because it makes the
same geometry answer differently depending on a field in the asserted block that
no computation checks, and because record 0003 deliberately keeps that field
asserted. The report names both records instead.

Leaving the constant rescaling question to the implementation. Rejected because
the two defensible answers differ on the most cited family in the catalogue, so
whichever branch of the comparison ran first would have decided it, and the
decision would have been discoverable only by experiment.

Writing the limitation once in the operator documentation and referring to it from
the report. Rejected because a report is read where the documentation is not, and
because a reference that a reader does not follow is a limitation that was not
disclosed. The cost is three copies of one paragraph and the disclosure above
about what holds them in step.

## What depends on this

Record 0005, whose family and stratum machinery is what the relation fixed here is
compared across, and whose undetermined answer for an undeclared parameter domain
this record leans on.

Record 0008, issue #15, which fixes the outcomes `is_this_new` returns and carries
the positive paragraph above in its report.

Record 0009, issue #17, which fixes which questions about these expressions are
decidable, and therefore when the family map above cannot be found or ruled out.

Issue #58, the discrete comparison, and issue #59, the continuous comparison,
which together decide the relation this record names. Issue #59 carries the
parameter map.

Issue #60, `is_this_new`, and issue #62, the separating invariant a negative
answer has to show, which is where a homothety field would land if it is ever
added.

Issue #64 and issue #65, the two corpora, which are tests of this relation:
known-equivalent pairs in different coordinates must match, and pairs separated
by one further order must not.

Issue #99, the operator documentation, which carries the two quoted paragraphs.

Record 0013, which lists the notion of equivalence as unshared with `findbuch`,
and which this record does not move.

Revisiting the relation means revisiting every verdict the catalogue has
published, because a verdict is only meaningful against the relation it was
computed under. There is no cheap version of this change.
