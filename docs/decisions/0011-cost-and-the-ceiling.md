# 0011. The cost model, the declared budget and the ceiling

## Status

Accepted

## Date

2026-08-09

## Question

The algorithm differentiates the Riemann tensor covariantly and repeatedly, and
the live expression set grows with the order. Record 0010 named memory rather
than multiplication speed as the resource that runs out.

What happens when it runs out today is that the operating system kills the
process. There is no report, the operator does not learn which order the run
reached, and the only route to learning anything is a second run of the same
length. The information a failed run is best placed to give is exactly the
information a kill destroys.

So: in what unit is memory measured, and read how? What does a run declare
before it starts? What does the refusal say, so that the next person can tell
whether a larger machine would help? And is an entry the ceiling stopped a
publishable part of the catalogue or only a diagnostic?

Record 0013 lists this record on the shared side of the boundary with
`findbuch`, so whatever is answered here has to be answerable by a board with no
spacetime in it.

## Answer

### The unit is the number the kernel acts on

Peak resident set size of the process, read from the operating system.

The failure this record exists to prevent is the kernel ending the run. The
kernel reads resident set size. A budget declared in any other unit is a budget
against a different number from the one that ends the run, and the distance
between those two numbers is where the failure survives a budget that looked
like it was set.

That choice buys one thing and gives up another, and both are worth naming.
Resident set size counts memory the interpreter holds and has not returned, and
memory allocated by a C extension, neither of which any accounting inside Python
sees. It is also coarse: it says how much is resident and nothing about what is
in it. So the unit the budget is enforced in is resident set size, and the
attribution of where the memory went is a separate and cheaper instrument that
never decides a refusal. The trace below is that instrument.

How it is read. At each checkpoint the run asks the operating system for the
process's high-water mark. Where the platform maintains one, that value is used
rather than a value this project sampled, because a sample taken between two
checkpoints misses a peak that happened between them and a high-water mark does
not. Where the platform maintains no high-water mark, the current resident size
at the checkpoint is used, and the report names which of the two it read in its
`mechanism` field, so a peak that was sampled is never read as a peak that was
recorded.

A run on a platform where neither is available does not start. It refuses with
that as the reason, rather than running with a budget it cannot enforce. The
main suite is unaffected: nothing in it approaches the ceiling, and record 0001
already puts the runs that do into the separate harness issue #1 names.

No route to any of the three mechanisms is in the tree, so every sentence in
this section is a claim about what will be built and not a measurement:

    git grep -n 'getrusage\|VmHWM\|tracemalloc' -- src/ tests/ ; echo "exit=$?"
    exit=1

Issue #69 is where the mechanism becomes a command and where the claim that the
refusal fires before the kernel does becomes a run rather than a sentence.

### The declared budget, as two numbers

A run declares both budgets before it starts and refuses rather than exceeds
them.

The named machine class is 64 GiB of memory, 68719476736 bytes.

The default memory budget is 48 GiB, 51539607552 bytes.

The default wall-clock budget is 6 hours, 21600 seconds.

Each is one configuration value and changing one is one edit, which is what
issue #69's last line asks for.

The machine class was named in the plan and was not in the tree until this
record:

    git grep -in 'gigabyte\|GiB\|64 GB' origin/main -- docs/ ; echo "exit=$?"
    exit=1

Why the budget is below the class rather than equal to it. The budget is checked
at checkpoints, and between two checkpoints one differentiation step can
multiply the live set, so the headroom has to cover a step rather than a
rounding error. The machine also holds an operating system and everything else
resident on it, and the kernel acts on the total rather than on this process's
share. A budget equal to the machine is a budget that is first reached after the
kernel has already begun to act, which is the outcome being designed against.

Why 6 hours. It is the length of run named in issue #20 as the cost of learning
nothing, and it is the point past which a run that has not terminated is far
more likely to have met the growth wall than to be one order from finishing. A
refusal at six hours costs six hours and produces a report. A kill at nine costs
nine and produces nothing.

The wall-clock budget carries a cost the memory budget does not, and it is
stated rather than absorbed. Wall clock is the one input here that lets the
machine change the outcome: a run that completes in five hours on one machine
refuses at six on a slower one, and those two are not a disagreement about a
geometry. That is why the declared budget is a required field of every report
rather than an implicit default, so two runs that ended differently can be read
against what they were started under. Record 0012 already fixes that two runs
under different budgets are not required to agree; the field is what lets a
reader see when that clause is the explanation.

A budget may be declared absent. `none` is a legal value for either, it is
written into the report as `none`, and a reader meeting it knows the run had no
ceiling. What this record removes is a run with no ceiling and nothing saying
so; an explicit `none` is not that.

No measurement stands behind either number. Both are declared now because a
declared number can be corrected against a table and an undeclared one cannot,
and issue #70 is the table that corrects them.

### What the report carries

Record 0013 puts this record on the shared side, so the field list is generic
and this board names its instances of the generic entries. The tension is real
and it is resolved here rather than inherited: a catalogue of integrable cases
has no differentiation order and no frame, so a field list naming those two is
not a shared list. What both boards have is a progress measure, a resource
measure and a largest live object.

Shared, on both boards:

- `limit`, which budget ended the run: `memory`, `time`, or `none` for a run
  that ended for a reason that is not a budget.
- `budget_memory` and `budget_time`, the declared budgets the run was started
  under, each a number or `none`.
- `peak_memory` in bytes, and `mechanism`, naming how it was read.
- `elapsed` in seconds.
- `progress`, a monotone integer saying how far the run got, and
  `progress_unit`, naming what it counts.
- `largest_object` and `largest_object_unit`, the largest live object of the
  run's own kind and what it is measured in.
- `normalisations`, the count of full normalisations performed, which record
  0012 already names as a cost field.
- `machine`, the machine the run was made on. Its field set is issue #67's and
  is not fixed here.
- `command`, `commit` and `date`, which is the stamp record 0003 requires of a
  derived entry.
- `trace`, one entry per completed unit of progress, described below.

This board's instances:

- `progress_unit` is `differentiation_order`, and `progress` is the highest
  order completed.
- `largest_object_unit` is `subexpression_nodes`, and `largest_object` is the
  largest live expression measured in distinct nodes of the hash-consed store
  record 0010 keeps alive across orders.

One field is this board's and is not shared, and it is named as such rather than
pushed into the generic list:

- `frame_parameters_free`, the number of frame parameters not yet fixed at the
  last completed order. Issue #20 asks for it and it is worth having: together
  with the order reached it is what tells a reader whether the run was close to
  terminating or nowhere near it.

The four minimum fields issue #20 asks for are the order reached, the size of
the largest live expression, the number of frame parameters still free and the
elapsed time. They are `progress`, `largest_object`, `frame_parameters_free` and
`elapsed` above.

### The trace, and the artefact issue #52 named

Issue #52 asks the differentiation loop to report the component count, the
largest expression size and the memory in use at every order, and to report them
whether or not anybody asked. That instrumentation is right and this record
keeps it. What it lacked was a destination: it names a "run record", and no
record in `docs/decisions/` defines one.

The destination is `trace`, a field of the report above. One entry per completed
unit of progress, each carrying `unit_count`, `largest_object` and the resident
memory at the end of that unit, `normalisations` during it, and the elapsed time
at its end. `unit_count` is the shared name for the count of things the unit
produced, because a board with no differentiation order has no components; on
this board it is the number of independent curvature components at that order,
which is the count issue #52 asks for.

Two properties of the trace are load-bearing.

It is written as each order completes rather than at the end. The run that most
needs the trace is the run that does not reach the end, and a trace assembled at
the end is a trace that run never writes.

It is a measurement of a run and not a claim about a solution. So it sits with
the cost, and everything in this section is outside what record 0012 asserts
byte equality over, for the same reason the cost fields already are: two runs of
one input on one machine differ here for reasons this project does not control.
The excluded field list belongs to issue #56, per record 0012, and what this
record adds is that the list has to cover the trace as well as the timestamps.

### Where a refused run's report goes

Record 0006 fixes where the cost of a completed run is stored: on the
verification entry of the value the run produced. That works because a completed
run produced a value. A refused run produced none, writes no verification entry,
and so has no entry to hang a cost on. The report needs a home of its own and it
gets one without a new name.

The artefact issue #56 defines has two outcomes rather than one. A completed
run's record carries the discrete data, the continuous data, the report above
and the stamp. A refused run's record carries the report above and the stamp,
and carries no discrete and no continuous data, because none was produced. One
artefact, one field set for the cost, one outcome field separating them.
Issue #56 is titled for the finished run; what it owes after this record is
the refused outcome beside it.

Three field lists disagreed before this record and this is the record that
decides between them, which is what record 0006 deferred here.

Record 0006 names peak memory, wall clock and the differentiation order reached
as what a `recomputed` entry carries. That list stands unchanged and is the
stored subset: `peak_memory`, `elapsed` and `progress` above. A verification
entry carries those three; the full report and the trace live on the
classification record, where a run that produced no value can still write them.

Record 0012 names wall clock, peak memory and the count of normalisations as
measurements of a run. All three are here, `normalisations` included, and all
three are outside byte equality.

Issue #52 names the component count and the largest expression size. Both are in
the trace, per order, which is where that issue asked for them.

### A partial classification is published, and what marks it

It is published. Entry 5 of the maintainer's question issue, #2, was answered on
2026-08-09: a named machine class, and entries that exceed it stay in the
catalogue marked unfinished rather than being left out.

The reason given there is the reason this record carries. An empty slot in a
catalogue says nothing about why it is empty. A reader who does not find an
entry cannot tell whether the solution is absent from the catalogue, or was
attempted and did not fit, and those are different facts with different next
steps.

What marks it is nothing new. Record 0006's vocabulary is closed and it already
has the room.

A derived field the run did not produce has no `recomputed` verification entry.
It keeps whatever state it had. `transcribed` and `checked_against_publication`
both carry record 0006's published marker, which says that no computation in
this repository has confirmed the value, and that marker is part of the
published artefact rather than a footnote. A field that was never transcribed
either is absent, and record 0006's gate refuses a value with no verification
entry, which an absent field is not.

Beside it stands the refused run's classification record, saying which budget was
reached, at which order, with how much frame freedom left, on which machine, and
under which declared budget. That is what turns "no value here" into "attempted,
and this is how far it got and what it would take", which is the difference the
maintainer's answer is about.

No fifth verification state is added, and this record does not add one. Record
0006's four words are four epistemic positions about a value; "the run reached
its memory budget" is not a position about a value, it is a fact about a run,
and the report is where a fact about a run goes.

The consequence for issue #70 is that the cost table has one shape rather than
two. A refused row carries the same fields as a completed one, differing in
`limit` and in having no discrete data behind it, so the honest rows and the
successful rows are read the same way and counted in the same table.

### What would show this was wrong

Nothing here was measured, and the command above is the disclosure rather than
the qualification.

Three things would move it.

Peak resident set size turns out to be a poor predictor of the kill. The run
refuses at 48 GiB on a machine that would have carried it to 60, or the kernel
acts at 40 because of what else was resident beside it. Issue #70's table is the
measurement, and what moves is the distance between the class and the budget
rather than the mechanism.

The checkpoints are too far apart. One step between two checks grows the live set
past the budget and past the kernel in one go, the refusal never fires, and the
kill happens anyway with a budget declared. Issue #69's Done-when already asks
for the proof that the refusal fires first, on a real large input in the
hardware-bound harness rather than against a mocked allocator alone. If that
proof cannot be made, either the checkpoint is in the wrong place or the ceiling
has to move inside the allocator, which is the first rejected alternative below
and is available only under a different means.

The wall-clock budget refuses runs that would have finished. Then it is a knob
that cost information rather than saved it, and the repair is to raise it or to
drop it and keep the memory budget alone. The memory budget does not have this
failure mode, because a run that exceeds the memory of the machine does not
finish on that machine at any budget.

## Rejected alternatives

Allocator accounting inside the process. `tracemalloc` is in the standard
library, it attributes an allocation to the line that made it, and that
attribution is more useful than a single number. Rejected as the unit the budget
is enforced in, on two counts. It does not see memory a C extension holds, and
record 0001 deliberately keeps open the door to an algebra implementation reached
through the C ABI, so the accounting would go blind exactly where the memory
would then be. And it is not the number the kernel reads, which is the first
section's whole argument. It is not rejected as an instrument: it is the natural
way to build the attribution the trace asks for, where being approximate costs
nothing because it decides no refusal.

A bounded arena the algorithm allocates from. The most exact of the three
mechanisms issue #20 named: a ceiling that cannot be exceeded rather than one
that is checked, and no sampling gap to argue about. Rejected because the means
cannot carry it. Record 0001 chose CPython with SymPy, and a Python library does
not allocate its objects from an arena it owns; they come from the interpreter's
allocator, which nothing inside this project can bound. It becomes available if
the algebra implementation moves behind the C ABI, which record 0001 keeps open
by construction, and if that happens this record is revisited rather than worked
around, because an arena is a better answer than a sampled one and the only
reason it is not the answer today is the runtime.

Virtual size rather than resident size. Rejected because it counts address space
that was reserved and never touched, so it refuses runs that would have fitted,
and the number it refuses on is not the number the kernel acts on either.

No budget at all, and let the operating system decide. This is the state the
record ends and its cost is in the question above: the kill destroys the report
that the failed run was best placed to give. It is listed here because it is the
default that arrives by doing nothing, which makes it the alternative most likely
to be taken by accident.

A budget as a fraction of the machine's memory rather than as a number. It
adapts to the host with no configuration, which is the attraction. Rejected
because a budget that changes with the machine makes two refusals incomparable,
and comparability is what the report exists for: two runs that both refused at
"seventy-five percent" refused at two different sizes and the reader cannot see
it. The machine is recorded per run instead, which gives a reader both numbers
and lets them take the ratio if they want it.

A memory budget alone, with no budget on time. Rejected because one of the two
failure modes issue #54 names has no memory signature. A zero test that fails to
recognise zero gives a loop that never terminates, and it can fail to terminate
in bounded memory, where a memory budget never fires. The time budget is the only
thing in the design that ends that run.

A separate artefact for a refused run, beside the classification record.
Rejected because it is a second name for one field set, and a consumer would then
have to learn two shapes to read one table. The classification record already has
to carry the cost of a completed run; carrying the same fields for a refused one
costs an outcome field.

A fifth verification state meaning unfinished. Rejected because record 0006's
four words are positions about a value and this is a fact about a run. A state
that means "the machine was too small" would make the vocabulary of a catalogue
depend on the hardware it was built on, so the same record would need a different
state after being recomputed on a larger machine, and record 0006 built its
vocabulary specifically so that no such thing is a state.

Leaving an over-budget entry out of the catalogue. Rejected by the maintainer's
answer to entry 5 and for the reason given with it: an empty slot says nothing
about why it is empty. It also loses the one measurement that says what a larger
machine would need to be, which is the measurement issue #70 is written to
publish.

## What depends on this

Issue #67, which measures the cost of every classification and stores it. The
field list above is what it writes, and the machine description is the one part
of it that issue owns rather than this record.

Issue #69, the declared budget and the refusal, whose default budgets are the two
numbers above and whose proof is that the refusal fires before the kernel does.

Issue #52, whose per-order instrumentation reports into the trace above rather
than into an artefact no record defines.

Issue #54, whose last line says the run says which termination condition was met
and at which order. That is discrete data of a completed run and belongs to the
classification record's discrete block rather than to the cost report here; what
this record settles for that line is which artefact it means.

Issue #56, the classification record, which owes a refused outcome as well as a
completed one, and whose excluded field list has to cover the trace as well as
the timestamps.

Issue #70, the published cost table, whose rows are these fields and which is
where the two numbers above are corrected against measurement.

Issue #72, the one measurement-driven reduction, which reads the largest term out
of that table and therefore inherits whatever these fields fail to record.

Issue #77, the catalogue gate, which reruns a stored verification and so meets a
budget and a possible refusal on a value that previously carried one.

Record 0006, whose statement that cost belongs to the verification entry is
unchanged, and whose deferral of what a cost report contains is what this record
answers.

Record 0012, whose exclusion of the cost fields from byte equality now covers the
trace, and whose clause about two runs under different budgets is what the
declared-budget fields make readable.

Record 0013, which lists this record as shared. The split between the generic
field list and this board's instances is what that listing costs, and a change to
either half is a change `findbuch` has to be told about.

Record 0010, whose hash-consed subexpression store is what
`subexpression_nodes` counts, and whose argument that the cost is in the number
of distinct subexpressions is what makes that the right unit.

Record 0001, whose falsifying spike records peak resident memory, wall clock and
the count of normalisations per differentiation order. Those are three of the
fields above, so the spike writes a report of this shape rather than a format of
its own.

Entry 5 of the maintainer's question issue, #2, which is answered and is what
allowed the last section to be written. Entry 7 of the same issue, on which
checks become required, is untouched by this record.
