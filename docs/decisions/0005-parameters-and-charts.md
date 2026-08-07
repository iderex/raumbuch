# 0005. Parameters, strata and charts

## Status

Accepted

## Date

2026-08-07

## Question

A line element with a free parameter is not one geometry. Kerr with the spin set
to zero is Schwarzschild, and asking whether the Kerr family is equivalent to the
Schwarzschild family is a different question from asking it about two particular
members. Four things follow from that and none of them can be left to whoever
writes the first entry.

Does a record hold one geometry or a family, and if a family, how are the
parameter ranges and reality conditions written down?

What happens at a degenerate limit, where the Petrov type or the isometry group
dimension jumps on a lower-dimensional subset of parameter space?

What is a coordinate range, and is a solution written in two charts one entry
with two charts or two entries?

What does `is_this_new` do when it is handed a metric that still has free
parameters in it?

## Answer

### A record holds a family

A record holds a family. Parameters are declared, each with a name, a domain,
a range written as conditions, and a meaning in one line. A single geometry is
the case where the parameter list is empty, which is a family of one rather than
a second kind of record.

The reason is that the literature publishes families and a record per parameter
value is not a finite object. The cost is that almost every question about an
entry has to name which member or which subset it is about, and the rest of this
record is the machinery for saying that.

The declared range is a statement about which geometries the entry claims to
cover. It is not a statement about where the stored derived values hold. Those
are two different things and conflating them is the failure this record is
mostly about.

### Strata carry the classification, never the family

A record carries a list of strata. A stratum is a named subset of the declared
parameter range, given as conditions on the parameters. Exactly one stratum is
marked generic, and it is the declared range minus the union of the others.

Every derived field and every claimed field attaches to a stratum. Nothing
attaches to the family as a whole. A classification that is valid on the generic
subset and silently wrong on a special locus is worse than no classification, and
the only way to make that shape unwritable is to remove the place it would be
written.

A stratum is declared where a stored field jumps. A special locus where nothing
this catalogue stores changes is not a stratum, and the entry says so in prose
instead. That boundary moves if the catalogue later stores a field that does jump
there, and when it moves, every value stored against the generic stratum has to
be re-read as excluding the new one. That is a real cost and it is the reason the
strata are declared per record rather than discovered per query.

What the loader can and cannot refuse here has to be said plainly. It refuses a
record with no generic stratum, a derived or claimed value attached to no
stratum, and a stratum naming a parameter the record did not declare. It cannot
in general decide whether the declared strata cover the declared range or whether
they overlap, because that is a decision problem over the conditions the record
is allowed to write, and record 0009, issue #17, is where the limits of deciding
anything about those expressions are argued. So coverage is an asserted claim: a
record carries a `coverage_argument` field saying in prose why the strata cover
the range, and a reader checks it. This is an assertion, and calling it a check
would be false.

### Charts

A chart carries the coordinate names in order, the coordinate range as
conditions, any identifications, the metric components in those coordinates, and
one sentence saying which region of the spacetime it covers.

A coordinate range is an open set given by conditions on the coordinates. A
coordinate carrying no condition is unrestricted. The range excludes the loci
where the chart breaks down, and a record says which of those are singularities
of the chart and which are singularities of the spacetime, because a reader who
cannot tell the two apart will read `r > 2*M` as a claim that the spacetime ends
there.

A solution written in two coordinate systems is one entry with two charts. The
entry is the spacetime; the coordinate system is how somebody wrote it down. Two
entries would make the catalogue answer that a chart change produced a new
solution, which is the exact failure the project exists against. Schwarzschild
and Kruskal are the canonical case and they arrive on the first day.

Each chart after the first names its relation to another chart in the same
record, from a closed vocabulary. `same_region` means the two cover the same
open set and the coordinate transformation between them is given as an asserted
field. `extends` means the other chart's region is a proper subset of this one,
which is the Kruskal case. `overlaps` means the intersection is non-empty and
neither contains the other, and the overlap is stated. A relation is an
assertion, not a computation; nothing here verifies that a written transformation
does what it says.

The algorithm is local and its input is a metric in coordinates, so a
classification runs per chart per stratum. Two charts related by `same_region`
must produce the same classification, and that is not a tautology; it is a
property worth testing, and issue #64 is the corpus of known-equivalent pairs
written in different coordinates that tests it. Charts related by `extends` agree
on the overlap and may differ outside it.

### is_this_new with free parameters

`is_this_new` compares families to families.

A query that still carries free parameters must declare them the same way a
record does, with domains and ranges. Where it does not, the answer is the
undetermined one, with the reason that the parameter domain was not declared.
This is not politeness. Equivalence of two families is not defined until the
domains are, so an answer either way would be a guess wearing the shape of a
result. The vocabulary the answer is expressed in is record 0008, issue #15, and
this record only fixes what has to be passed in for a definite answer to be
possible.

Where the domains are declared, the comparison is per stratum. The discrete part
must agree on corresponding strata, which is issue #58, and the continuous part
must agree as functional relations among the Cartan scalars, which is issue #59.
A family can match another family on its generic stratum and differ on a special
one, and the answer says which strata matched.

A query carrying concrete numeric values for its parameters is not a family
query. It is instantiated first, and the paragraph below is that step.

### Getting from a family to a single geometry

The software does this step, not the consumer.

`instantiate` takes a record and a value for every declared parameter. It
refuses a value outside the declared range or failing a reality condition. It
selects the stratum the values fall into, and where it cannot decide which
stratum that is, it refuses rather than picking the generic one. It returns a
record with an empty parameter list and one stratum.

The consumer supplies values and nothing else. The reason is that substitution
before classification is exactly where a consumer would drop a reality condition
without noticing, and a reality condition dropped in silence turns a real metric
into a complex one several steps later, where the error surfaces as an
unexplained arithmetic failure rather than as a bad input.

### Kerr, worked through

Kerr in Boyer-Lindquist coordinates, on the black hole branch, in the record
shape of 0003. The classification values below are claims read from the
literature. Nothing here has been computed by this project, and the record shape
puts them in the claimed block for that reason.

The declared parameters are the mass parameter `M` with range `M > 0` and the
spin parameter `a`, real, with `a^2 <= M^2`. Both are real, which is the reality
condition, and the branch condition `a^2 <= M^2` is what restricts the entry to
the black hole case.

Two strata.

The special stratum `a = 0`. The claimed isometry dimension is 4 and the claimed
Petrov type is D. This is Schwarzschild, and it is the degenerate limit the issue
names. The jump is in the isometry dimension, from 2 to 4, and it happens on a
subset of parameter space of lower dimension than the family. A record storing
one isometry dimension for the whole Kerr family would be wrong on exactly this
locus, which is a set of measure zero and also the single most cited member of
the family.

The generic stratum, `a != 0`. The claimed isometry dimension is 2, from the
stationarity and the axial symmetry, and the claimed Petrov type is D.

The extremal locus `a^2 = M^2` is inside the generic stratum and is not a
stratum. The global structure degenerates there, and nothing this catalogue
currently stores jumps. The entry says that in prose. If the catalogue later
stores a field that does jump at extremality, a third stratum is added and the
generic stratum's stored values are re-read as excluding it.

The limit `M = 0` is outside the declared range, which excludes it by `M > 0`.
That limit is flat spacetime, with Petrov type O and isometry dimension 10, and
a record that extended its range down to `M = 0` without declaring a stratum
there would claim type D on a locus where the answer is O. The point of working
it through is that the range and the strata are two separate defences and the
record needs both: the range says the entry does not cover `M = 0`, and if a
later editor widens the range, the strata are what has to move with it.

The exterior chart covers `r > M + sqrt(M^2 - a^2)`, with `theta` strictly
between 0 and `pi` and `phi` identified modulo `2*pi`. The inner boundary is a
horizon and a singularity of this chart, not of the spacetime, and the record
says so. A second chart in Kerr-Schild coordinates would be a chart of the same
entry with relation `extends`.

The record for Kerr therefore has one parameter block with two entries, one
strata block with two entries, one chart block, and a claimed block whose keys
are written per stratum. Its derived block is empty until the commands in record
0003 exist.

## Rejected alternatives

One record per geometry, with a family written as a generator. Rejected because
a generator is a program, the record format refuses to hold a program for the
reasons in record 0003, and the catalogue would then be infinite or arbitrarily
truncated.

A family with no strata, classified on the generic subset only, with the special
loci left to the reader. Rejected because it is the silently-wrong-on-a-subset
case the issue names, and because the special loci are the members people
actually look up.

Strata discovered automatically by the software rather than declared. Attractive,
and it is not available: finding where an invariant degenerates over a parameter
space means deciding conditions on symbolic expressions, which record 0009,
issue #17, does not promise to do in general. Declared strata with an asserted
coverage argument is the honest version of the same intent.

Schwarzschild and Kruskal as two entries, linked by a field saying they are the
same spacetime. Rejected because the link would be the thing that gets forgotten,
and because a catalogue whose primary key is a coordinate system answers the
wrong question by construction.

One chart per entry, with other coordinate systems left out. Rejected because the
second chart is often where a solution is usable, and because a chart change is
the transformation `is_this_new` most needs to survive.

Refusing a query that carries free parameters. Rejected because the question the
board is built to answer is frequently asked about a family, and answering only
about single geometries would push the family comparison into the consumer, which
is where it would be done wrong.

Instantiating in the consumer rather than in the software. Rejected in the
paragraph above: the reality conditions are declared in the record and the
consumer has no reason to read them.

## What depends on this

Record 0003, whose parameter, stratum and chart blocks are specified here.

Issue #35 and issue #36, the schema and the loader, which carry the refusals this
record creates: no generic stratum, a value attached to no stratum, a stratum
naming an undeclared parameter.

Issue #58 and issue #59, the discrete and continuous comparison, which run per
stratum because of this record.

Issue #60, `is_this_new`, whose input contract is fixed here, and record 0008,
issue #15, which fixes what it may answer.

Issue #64, the corpus of known-equivalent pairs in different coordinates, which
is the test of the `same_region` claim.

Issue #73 and issue #74, the first catalogue entries, which are the first real
use of the strata.

The maintainer's question about whether an entry may ever be removed, issue #2
entry 10, touches this record at one point: superseding a record that holds a
family is coarser than superseding one geometry, and if entries are only ever
superseded and never deleted, a correction to one stratum supersedes the whole
record. That is left to record 0004, issue #9, and is named here so it is not
discovered later.
