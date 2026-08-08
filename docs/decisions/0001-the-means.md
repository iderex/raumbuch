# 0001. The means: language, toolchain and symbolic algebra layer

## Status

Accepted

## Date

2026-08-08

## Question

Every later milestone reads this answer. The frame formalism decides the shape of
the arrays, the record format decides what the loader refuses, and both of those
are written in something. A means carried over from habit is an assumption about
this artefact borrowed from a different one, so the question is asked once, here,
against what this project actually has to do.

What the means has to carry is not a preference list. Record 0009 fixed the
arithmetic: exact computation in the Gaussian rationals `Q(i)`, a field of
rational functions above it in the coordinates, the parameters, the named
constants and the applied function symbols, a zero test that is a total
normalisation to a quotient of expanded polynomials, greatest common divisors and
subresultants for the root multiplicities the Petrov type is read from, and one
evaluation modulo a large prime as a cheap filter. Record 0010 fixed a
hash-consed store of subexpressions kept alive across differentiation orders, and
named memory rather than multiplication speed as the resource that runs out.
Record 0012 fixed that nothing about how the work was scheduled may reach the
output. Record 0003 fixed that a record is TOML validated against a published
JSON Schema, and that loading one parses text into a syntax tree and executes
nothing.

So: which language, which toolchain and which version pinning mechanism, and
which symbolic algebra layer? And what does the answer foreclose?

## Answer

### The choice

Python 3, on CPython, with SymPy as the symbolic algebra layer.

The interpreter version is pinned in one file at the repository root,
`.python-version`, holding one version and nothing else. Dependencies are
declared in `pyproject.toml` and locked to exact versions with hashes in
`requirements.lock`, which is committed. The installation route is
`pip install --require-hashes -r requirements.lock`, so an unlocked or
substituted artefact fails the install rather than reaching a run. The tool that
regenerates the lock is itself in the lock. Issue #27 is where the pin file, the
lock and the check that refuses drift between them land, and where the claim that
no workflow carries a version literal becomes a grep quoted in a pull request
body rather than a sentence here.

The command-line entry point is `raumbuch`, a console script over the package in
`src/raumbuch/`. Record 0003 already reserved the verbs `raumbuch classify`,
`raumbuch curvature` and `raumbuch verify` against the derived fields they
recompute, so the entry point name is fixed by that reservation rather than
chosen freshly here. The gate is one more verb of the same program, `raumbuch
gate`, and issue #24 is where its legs and its reporting land.

### The directory layout

Issue #24 takes its scope from this section, so the layout is fixed here and its
contents are not.

```
src/raumbuch/            the package, including the command-line entry point
src/raumbuch/algebra/    the arithmetic interface below, and its implementation
tests/                   the unit suite, headless and unprivileged
catalogue/               one solution record per file, per record 0004
schema/                  the published JSON Schema of record 0003, issue #35
docs/                    documents, including docs/decisions/ and docs/checks.md
.githooks/               the pre-push hook, which execs the gate verb
```

A `src` layout rather than a package at the root, because a package importable
from the checkout directory is a package the suite can pass against while the
built artefact is broken, and the reproducible build in issue #98 is where that
would surface at the worst moment.

### The arithmetic is behind one interface, and that is the load-bearing part

The weakness of this choice is arithmetic in interpreted Python at the orders
milestone 5 reaches. It is named as a weakness in the issue this record answers
and it is not argued away below. What this record does about it is structural:
everything record 0009 makes load-bearing sits behind one interface in
`src/raumbuch/algebra/`, and nothing outside that directory constructs a SymPy
object or names a SymPy type.

The operations on that interface are the ones record 0009 needs and no others:
reduce an expression to the normal form of record 0009, answer a zero test with
`zero`, `nonzero` or `undetermined`, evaluate at a rational point modulo a prime,
differentiate with respect to a declared symbol, take a greatest common divisor
and the subresultants of two polynomials, and apply the declared rewrites of the
closed function list.

The reason for the boundary is that the falsifying measurement below has a real
chance of coming back against SymPy, and the difference between a means decision
that can be revisited and one that cannot is whether the algorithm was written
against an interface or against a library. With the boundary, replacing the
implementation with a compiled kernel is a change inside one directory and a
second entry in the lock. Without it, it is a rewrite of milestones 4 through 6
and a second means decision under pressure.

The boundary is not free and the cost is stated rather than absorbed. It gives up
the operator overloading and the printing that make a SymPy expression pleasant to
work with at a call site, it means one more layer between a physicist reading the
curvature code and the algebra underneath, and an interface with exactly one
implementation is an interface nobody has yet proved is implementable twice. That
last one is why the falsifying run below is written as a spike against the
interface rather than as a benchmark of SymPy.

### The four questions the means check asks

Can the means carry a refusable property, an executed proof that the guard bites,
and a claim carrying the command that produced it?

Yes, and none of the three needs anything Python does not already have. A check
is a leg of the gate verb that exits non-zero, which is refusable in the sense
issue #95 requires. A proof that a guard bites is a test that feeds the guard a
fixture violating exactly one property and asserts the refusal names that
property, which is an ordinary test. A claim carrying its command is a property of
how a body is written and not of the language. The one thing worth naming is that
Python has no compiler to refuse a wrong type before a run, so where this project
wants a refusal at the earliest moment it has to be a check rather than a build
failure. The verdict type in record 0008 is the case where that matters, and it
is answered there by a runtime refusal rather than by trusting a type checker.

Is anything outside this repository forcing the choice, and how far does that
force reach?

Two forces, and both are held to their smallest surface. The first is the
literature and the people in it. The contributors this catalogue needs are
physicists who read tensor code, and the field's tooling that is not a closed
system is overwhelmingly Python, so a means that a domain reader cannot follow
costs contributions that no amount of internal quality replaces. That force
reaches the readable layer and stops at the algebra boundary above. The second is
`indexwerk`, the sibling board building index canonicalisation behind a C
interface. Record 0010 declined a hard dependency on it and admitted it behind an
optional interface, and Python reaches a C ABI through `ctypes` in the standard
library, so the door record 0010 asked to keep open is open with no dependency
added and none planned. That force reaches one optional module and nothing else.
A third force that is often assumed and is not present here: nothing outside this
repository requires the catalogue to be readable by any particular tool, because
record 0003 chose TOML precisely so the data outlives the means.

What language, runtime or dependency does the choice add, and is the cost paid
knowingly?

One runtime, CPython, and one substantial dependency, SymPy, plus whatever the
lock resolves under them. That is one language for the whole tree. The gate verb,
the loader, the classifier and the tests are all Python, so there is no second
suite and no shell logic inside a workflow file. The cost that is paid knowingly
is performance, and the record says where the bill arrives: the classification
runs that approach the memory ceiling in milestone 7, and nowhere else. The cost
that is paid less visibly is the supply chain, since a Python dependency set is
larger than the two or three libraries a compiled route would link. Issue #93 and
issue #98 are where that surface is measured, and the licence claims in the next
section are among the things they turn from a claim into a machine-read fact.

Would the artefacts be testable by the suite this repository will have, or do
they need a parallel apparatus nobody maintains?

By the suite. Everything this project builds is a library function, a file
loader, a document check or a command-line verb, and all four are testable in one
`pytest` process with no display attached and no elevation, which is what issue
#28 turns into a contract and a check. The one thing that genuinely does not fit
is the classification runs at the memory ceiling, and record 0011, issue #20,
together with the separate harness named in issue #1 is where those go. That
separation exists because of the size of the runs and not because of the means,
so it would exist under every candidate below.

### What this forecloses, and what it does not

Nothing.

CPython is distributed under the Python Software Foundation licence and SymPy
under BSD-3-Clause. Neither is a reciprocal licence, so every option in entry 1
of the maintainer's question issue, #2, remains available: no licence, MIT,
BSD-2-Clause, Apache-2.0, MPL-2.0, GPL-3.0 and AGPL-3.0. The conditional in that
entry, that a GPL symbolic layer collapses the choice to the copyleft options,
does not fire.

Keeping that conditional from firing is a reason for this choice and not a side
effect of it. Three of the candidates below are GPL, and choosing one of them
would have decided a question this record has no standing to decide.

Those two licence statements are read from the projects' own licence files. No
command in this tree verified either, because there is no code here yet and
nothing is installed. They are claims. Issue #98 is where the licence of every
locked dependency becomes a fact a command produces, and if either claim is wrong
the foreclosure paragraph above is wrong with it and this record is revisited.

### What would show this was wrong

No measurement stands behind this choice. There is no code in this repository
yet, nothing has been run, and no number appears above.

The claim that could be falsified is that the interpreted layer is not where the
time and the memory go. Record 0010 already argued that the cost is in the number
of distinct subexpressions rather than in the speed of one multiplication, and
this choice rests on that argument being right.

The run that decides it, and it is a spike rather than a benchmark. Implement the
algebra interface twice, once over SymPy and once over a compiled exact
arithmetic library reached through the C ABI, and classify one expensive entry
through each, recording peak resident memory, wall clock and the count of full
normalisations per differentiation order. Issue #74 is where an entry chosen to
be expensive rather than convenient comes from, and issue #70 is where the
numbers land.

If the compiled implementation is within a small factor on peak memory, the
choice stands and the interface was insurance nobody had to claim. If it is a
large factor lower on peak memory, the implementation behind the interface moves
and the language does not, which is the outcome the boundary was built for. If
the difference turns out to be in the interpreted layer above the boundary rather
than inside it, this record is wrong in a way the boundary does not repair, and
the honest response is to reopen it rather than to move code across the line one
function at a time.

A second thing would show this wrong and no run decides it: if the contributor
this record is written for does not appear. The reason the readable layer is
Python is the physicist who will read the curvature code, and if a year of entries
arrives with no such reader among them, the force that held the readable layer up
was not real and the trade should be re-argued rather than defended.

## Rejected alternatives

Python with SymPy alone, with no algebra boundary. This is the shortest route and
it is the same language and the same library, so it is rejected on one point
only: it welds the algorithm to the library. Pure-Python arithmetic at this scale
is the known failure mode named in the issue, `symengine` as a backend has its own
coverage gaps, and either way the day the measurement comes back badly is the day
a project without a boundary rewrites three milestones. The rejection is of the
shape, not of the library.

Python driving a compiled kernel through a narrow interface, with the kernel
written now. Rejected on timing rather than on merit, and it is the alternative
this record is closest to. The interface above is exactly the narrow interface
this option asks for. What is rejected is building the kernel before any
measurement says which operations are hot, because a kernel written against a
guess is a second implementation of the arithmetic to maintain from the first day,
and the spike above is cheaper than the guess. The door is left open by
construction rather than by intention.

C++ with GiNaC. Fast, exact and designed for expressions of this kind. Rejected
because it is GPL, so it decides entry 1 of the maintainer's question issue, which
this record has no standing to decide. Beyond the licence, its polynomial and
Groebner layer is thin next to a general computer algebra system, and while
record 0009 deliberately keeps the discrete classification out of algebraic
extensions, the continuous comparison in issue #59 has to look for a map between
two parameter domains and that is where the thin layer would be found out.

Julia with Symbolics.jl. Good performance, a type system that would express
record 0008's three outcomes better than Python does, and a permissive licence
that forecloses nothing. Rejected on the decade, not on the code: this catalogue
has to still load in ten years, the package ecosystem moves faster than that, and
the pinning story a catalogue needs is one where a lock resolved today installs
byte-identically in five years. Losing the type system is a real cost and record
0008 pays it explicitly with a runtime refusal.

Rust. Nothing in the ecosystem is a computer algebra system at the level this
needs, so choosing Rust means writing one. That is a larger project than this one
and it is the whole reason for the rejection. The narrower observation is that
the readable layer would then be unreadable to the contributor this project needs
most, and the arithmetic would be written by the people least able to check the
physics.

SageMath. Bundles everything this project could want, including a real Groebner
engine, and it is rejected on three counts rather than one. It is GPL, so it
decides the licence question. It is enormous and hard to package, which collides
with the reproducible build in issue #98. And it pulls in a licence mixture that
would have to be examined rather than assumed, which is work this project would
be doing for components it does not use.

Cadabra2. Tensor-aware from the start and Python-facing, which is a genuine fit
for the field. Rejected because it is GPL, again deciding the licence question,
and because its maintainer base is small enough that a catalogue with a ten-year
horizon would be taking a single-maintainer risk on its critical path. Record
0010 also removed the part of the case for it that was strongest, by finding that
index canonicalisation is not on this algorithm's critical path.

Maxima on a Lisp runtime. Closest to the route the original working
implementation took, and the one candidate with a real claim to having done this
before. Rejected because it is GPL, and because the contributor pool under fifty
is small enough that a project depending on it is depending on people who are
already retiring. That is a statement about a population and not about the
software, which is good and is still the risk.

Two candidates the issue did not list, rejected here so they are not raised as
overlooked. Mathematica or Maple as the implementation language, rejected because
a catalogue whose verification cannot be reproduced without a paid licence has
reproduced nothing, and because entry 4 of the maintainer's question issue keeps
a closed system as an optional external cross-check, which is a different and
much smaller role. And a means chosen to match whatever `findbuch` chose,
rejected because that board's arithmetic requirements are not this one's, and
because record 0013 already found that a language difference reduces the sharing
question to a shared file format, a shared vocabulary and a shared fixture
corpus, all of which survive two languages.

## What depends on this

Issue #24, the project skeleton and the gate verb, whose scope is the directory
layout fixed above.

Issue #25, issue #27, issue #28, issue #29 and issue #32, which are the named
checks of milestone 2 and are legs of the verb named above, running on the
toolchain pinned as described.

Record 0003, whose reserved command names fix the entry point this record names,
and whose TOML and JSON Schema choice is deliberately independent of everything
here.

Record 0008, issue #15, whose signature is written in the language chosen here
and whose verdict type pays for the absence of a compiler.

Record 0009 and record 0010, which are what the algebra interface above was
derived from, and which are the records that would have to be revisited if the
interface turns out to be the wrong cut.

Record 0013, whose first two answers to entry 6 of the maintainer's question
issue need `findbuch` to have chosen the same language. This record does not know
what that board chose, so whether those answers remain available is not settled
here and is not claimed to be.

Issue #93 and issue #98, the supply-chain parity work and the software bill of
materials, which are where the two licence claims above stop being claims.

Entry 1 of the maintainer's question issue, #2, which this record leaves open in
every direction, and entry 4, which is untouched because a closed system as an
external cross-check is a harness rather than a means.
