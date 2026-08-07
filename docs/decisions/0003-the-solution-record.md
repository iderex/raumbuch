# 0003. The solution record

## Status

Accepted

## Date

2026-08-07

## Question

The board promises that each solution becomes an object carrying the metric, the
coordinate range, the parameters, the stress-energy tensor, the Petrov type and
the Killing vectors. That list is not yet a record. What fields does a record
hold, which of them may a human write and which may only a machine write, what
file format is the record written in, and can loading one execute anything?

## Answer

### Three kinds of field, kept apart

A record has three blocks and the separation between them is the point of the
whole shape.

An asserted field is something a person wrote down and no machine here can
check. The metric components, the coordinate names, the parameter ranges, the
citation. These are the input.

A claimed field is a value taken from the literature for something this software
could compute. A Petrov type read off a book page is a claimed field. Claims are
legitimate, they are what most entries start life with, and they live in their
own block with the source that carried them.

A derived field is a value this software computed. It lives in its own block and
every entry in that block carries the command that produced it, the commit the
command ran at, and the date. A derived field with no such entry is refused by
the loader rather than accepted with a blank.

Claimed and derived never merge. A consumer asking for the Petrov type of an
entry gets one or the other and is told which, and no code path exists that
falls back from derived to claimed. A derived field transcribed from a book
instead of computed is the exact defect this board exists to remove, so the shape
gives a hand-written classification a legitimate place to go and no reason to
lie about where it came from.

Three things stand behind that, and only the first exists as a rule the loader
can apply on its own. The loader refuses a derived entry missing its command,
commit or date. The catalogue gate in issue #77 recomputes derived values and
refuses a mismatch, so a value that never came out of a run will not reproduce.
And the record format offers the claimed block, so the reason to write into the
derived block by hand is removed rather than merely forbidden.

### The fields

Asserted, and written by a person.

| Field | Fixed by |
| --- | --- |
| `schema_version` | issue #35 |
| `id`, `version` | record 0004, issue #9 |
| `name`, `aliases` | this record |
| `dimension` | this record |
| `signature` | record 0002, issue #7 |
| `parameter` list, with domain, range and reality conditions | record 0005, issue #10 |
| `stratum` list | record 0005, issue #10 |
| `chart` list, each with coordinates, range, identifications and metric components | record 0005, issue #10 |
| `matter.model` and, where the model is not vacuum, the stress-energy components | this record |
| `provenance` block | record 0006, issue #12 |
| `note` | this record |

Claimed, written by a person, each key carrying the source it was read from.
The keys are the same as the derived keys below.

Derived, written only by a command. Each entry names the field, the value, the
stratum and chart it holds on, the command, the commit, the date, and the cost of
the run.

| Derived field | Recomputed by | Built in |
| --- | --- | --- |
| `petrov_type` | `raumbuch classify --petrov` | issue #46 |
| `ricci_type` | `raumbuch classify --ricci` | issue #47 |
| `ricci_scalar` | `raumbuch curvature --ricci-scalar` | issue #45 |
| `field_equations_hold` | `raumbuch verify --field-equations` | issue #50 |
| `isotropy_dimension` per order | `raumbuch classify --cartan` | issue #53 |
| `independent_function_count` per order | `raumbuch classify --cartan` | issue #53 |
| `termination_order` | `raumbuch classify --cartan` | issue #54 |
| `killing_dimension` | `raumbuch classify --killing` | issue #57 |
| `cost` | recorded by every command above | issue #67 |

No code exists in this repository yet, so not one of those commands can be run
today. The column names what each command will be called and the issue that
builds it. It is a reservation, not a measurement, and nothing in this record
should be read as saying a value has been computed.

### The format

The record is TOML.

The metric is written as a list of tables, one per independent component, with
the two indices and the expression as fields. That is flat rather than nested,
which is the answer to TOML's known weakness here, and it costs one line per
component. The metric is symmetric, so only components with `i` at or before `j`
in the declared coordinate order are written, and the loader refuses a duplicate
or a transposed duplicate rather than silently taking the last one.

Validation is a published JSON Schema, issue #35, applied to the parsed document
rather than to the file text. TOML's value model maps into the JSON data model
without loss once the one TOML type with no JSON counterpart, the offset
datetime, is kept out, so dates are written as strings and the schema constrains
their format. This is what gets the record a surface a person can hand-write and
still leaves exactly one validator.

### The expression sub-language

A metric component, a stress-energy component, a coordinate range and a
parameter range are all strings in one small expression sub-language. It admits
integer and rational literals, identifiers, the operators `+ - * / ^`,
parentheses, a closed list of functions and a closed list of named constants.

An identifier must be one of the coordinates declared by the chart the
expression sits in, one of the parameters declared by the record, or one of the
named constants. Anything else is refused by name, which is what stops a record
smuggling in a symbol the reader cannot see the meaning of.

The named constants are needed by the first record written: a coordinate range
of `theta < pi` uses one, and there is no chart to declare `pi` in. Keeping them
a closed list rather than admitting free symbols is what keeps the refusal
above meaningful.

The closed function list, the closed constant list and the full grammar are
issue #40, and the arithmetic they are evaluated in is record 0009, issue #17.
What this record fixes is that both lists are closed and that the loader refuses
an identifier that is in neither list and was not declared.

Loading a record parses text into a syntax tree. It does not evaluate a string
in any language, it does not hand record text to a computer algebra system's
reader, and it does not deserialise a code object. Admitting arbitrary source
code of the underlying algebra system as the value of a field would turn loading
a catalogue into executing a stranger's program, and the closed grammar is what
refuses that rather than a promise not to do it.

### A worked record

Schwarzschild in the static exterior chart, complete in every asserted field,
with the literature values in the claimed block and an empty derived block
because nothing has computed anything yet. This is the first fixture the loader
in issue #36 is pointed at.

```toml
schema_version = "1"

id = "schwarzschild"
version = 1
name = "Schwarzschild exterior"
aliases = ["Schwarzschild vacuum", "Droste"]
dimension = 4
signature = "-+++"

# Geometric units, G = c = 1. The convention record, 0002 (issue #7), fixes this
# for every record and this line records which way it went.

[[parameter]]
name = "M"
domain = "real"
range = "M > 0"
meaning = "mass parameter"

[matter]
model = "vacuum"

[[stratum]]
name = "generic"
generic = true
condition = "M > 0"

[[chart]]
name = "exterior"
coordinates = ["t", "r", "theta", "phi"]
region = "the static region outside the horizon"
range = ["r > 2*M", "theta > 0", "theta < pi", "phi >= 0", "phi < 2*pi"]
identifications = ["phi ~ phi + 2*pi"]
# A coordinate carrying no condition in `range` is unrestricted. Here that is `t`.

[[chart.metric]]
i = "t"
j = "t"
value = "-(1 - 2*M/r)"

[[chart.metric]]
i = "r"
j = "r"
value = "1/(1 - 2*M/r)"

[[chart.metric]]
i = "theta"
j = "theta"
value = "r^2"

[[chart.metric]]
i = "phi"
j = "phi"
value = "r^2*sin(theta)^2"

[claimed]
petrov_type = "D"
ricci_type = "the Ricci tensor vanishes"
killing_dimension = 4
source = "provenance.source, the citation recorded below"

[provenance]
# Field names are fixed by record 0006, issue #12. The values here are a
# placeholder until the first real entry lands under issue #73.
source_kind = "secondary"
citation = "to be filled by issue #73"
transcribed_on = "2026-08-07"

# No [[derived]] entries. Nothing in this repository has computed anything yet,
# and an empty derived block is the honest state rather than a gap.
```

The coordinate range excludes `r = 2*M` and the two poles because they are
singularities of this chart and not of the spacetime. That distinction is a
chart property and record 0005, issue #10, is where it is argued.

The claimed block carries a Petrov type of D and four Killing vectors. Both are
read from the literature. Neither has been computed here and neither may be
reported by this project as though it had been.

## Rejected alternatives

One block of fields with a flag on each saying whether it was computed. Rejected
because the flag is the thing that gets wrong. A single boolean written by hand
beside a value written by hand is not a separation, and the first person in a
hurry sets it to true. Three blocks make the wrong thing require moving a value
into a block whose entries the loader refuses without a command and a commit.

Store only asserted fields and compute everything on read. Rejected because a
catalogue whose Petrov types exist only after a run of the classifier is not a
catalogue anyone can cite, and because the stored value compared against a fresh
run is what the gate in issue #77 needs in order to notice that the code changed
its mind.

JSON with a published schema. Machine-friendly and it has exactly one obvious
validator, which is why the validator was kept. Rejected as the file format
because it has no comments and no multi-line strings, and a metric hand-written
in it is at its least readable in precisely the field where a transcription slip
is the defect this project exists to remove.

YAML. Readable, and its type coercions disqualify it on the first field of the
record. A coordinate named `y` or `n` becomes a boolean under a 1.1 parser, and
the anchor, alias and tag machinery is a deserialisation surface a catalogue
that loads files from strangers should not carry.

A small format of the project's own. Fits the domain exactly and needs a parser,
a fuzzer, an error-reporting story and an editor mode nobody will write, and it
buys nothing over TOML with a flat component list.

The serialisation of whatever computer algebra system record 0001, issue #5,
chooses. Zero conversion cost, and it welds the catalogue to one tool for the
next twenty years, which is the failure this project is a response to. It also
usually means loading a record runs that tool's reader, which is the execution
this record refuses.

## What depends on this

Issue #35, the schema file, which is a JSON Schema applied to the parsed
document and versioned from the first day.

Issue #36, the loader, and its refusal vocabulary, which has to name the refusals
this record creates: a derived entry with no command, a duplicate metric
component, an undeclared identifier in an expression.

Issue #38, the fixture corpus of records that must be refused, one fixture per
reason.

Issue #40, the expression parser, whose grammar is bounded by the closed function
list this record requires.

Issue #43, the schema validation check in the gate.

Issue #50 and issue #77, which both compare a stored derived value against a
fresh computation.

Records 0004, 0005 and 0006, which fix the identifier, the parameter and chart
blocks and the provenance block respectively, and which this record leaves to
them rather than duplicating.

Revisiting the format choice means rewriting every landed record and the schema
with it, so the cost grows with the catalogue and is lowest today.
