# Writing a solution record

This is the document for somebody writing a record by hand. What a record holds
and why it holds it is decided in the decision records, chiefly
[0003](decisions/0003-the-solution-record.md) for the shape,
[0004](decisions/0004-identifiers-and-corrections.md) for the identifier,
[0005](decisions/0005-parameters-and-charts.md) for parameters, strata and
charts, and [0006](decisions/0006-provenance-and-verification.md) for provenance
and verification, with [0015](decisions/0015-record-disagreements-resolved.md)
settling the four places those records disagreed. This document does not restate
their arguments. It says what to type and what the machine will refuse.

The schema is `schema/record-1.schema.json`. It is a JSON Schema, draft 2020-12,
applied to the parsed TOML document rather than to the file text. The `1` in the
filename is the schema version, and it is the value every record carries in
`schema_version`. A second version of the record format is a second file beside
this one and never an edit to it, so a catalogue that outlives a schema stays
readable by the schema it was written against.

## Where a record lives

One record per file, at `catalogue/<id>.toml`, where `<id>` is the record's own
`id` field. Two people adding two different solutions write two different files
and no allocator is consulted; two people adding the same solution collide on one
path, which is the direction a collision should fail in.

## Three blocks, and the separation is the point

An asserted field is something you wrote down and no machine here can check. The
metric components, the coordinate names, the parameter ranges, the citation.

A claimed field is a value you read from the literature for something this
software could compute. A Petrov type off a book page is a claimed field. It is
legitimate and it is where most entries start.

A derived field is a value a command in this repository computed. Every derived
entry carries the command, the commit and the date. Writing one by hand is the
defect this project exists to remove, and the schema refuses a derived entry with
no stamp rather than accepting it with a blank.

Claimed and derived never merge. If you have a number from a book, it goes in the
claimed block, and nothing about that is second class.

## The asserted fields

`schema_version`, the string `"1"`.

`id`, a slug matching `^[a-z0-9]+(-[a-z0-9]+)*$`, equal to the filename stem. It
is assigned once and never reused, even if the entry is withdrawn.

`version`, an integer starting at 1. It covers the asserted and claimed blocks and
nothing else, so a recomputation does not move it. Every version above 1 adds one
entry to the `correction` list, naming the version it produced, the date, one
sentence saying what was wrong, and what it affects.

`name` and `aliases`, the human names. These carry no uniqueness promise; the
`id` is what is unique.

`dimension`, an integer.

`signature`, a string of `+` and `-` characters. Which signature this project
writes is fixed by record 0002; the schema refuses anything that is not a sign
string and does not decide the convention.

`parameter`, a list of tables, each with `name`, `domain`, `range` and `meaning`.
A record with no parameters is a family of one and simply omits the list.

`stratum`, a list of tables, each with `name`, `generic` and `condition`. Exactly
one stratum has `generic = true`, and the schema refuses zero and refuses two.

`coverage_argument`, prose saying why the declared strata cover the declared
range. Required of every record, including a record with one stratum, where it is
one sentence. Nothing here can decide coverage, so this is the assertion a reader
checks instead, and record 0015 is where it was made required.

`chart`, a list of tables, each with `name`, `coordinates` in order, `region` in
one sentence, `range` as a list of conditions, optional `identifications`, and
`metric` as a list of one table per independent component with `i`, `j` and
`value`. Every chart after the first also carries a `relation` table naming
`kind`, one of `same_region`, `extends` or `overlaps`, and the `chart` it relates
to. A `same_region` relation also carries the `transformation`; an `overlaps`
relation also carries the `overlap`. The schema refuses a second chart with no
relation, which is the mistake that turns one entry into two catalogues.

`matter`, a table with `model`. Where the model is anything other than `vacuum`,
the schema requires `stress_energy` in the same shape as the metric components.

`provenance`, a table with `source_kind`, one of `primary`, `secondary` or
`derived_here`, plus `citation`, `locator` and `transcribed_on`. The locator is
where inside the source the metric is, a page, an equation or a section, and it
is required because a citation without one sends the next reader to a book rather
than to a line. `doi` and `url` are optional and present where they exist. `note`
is optional prose for what the other fields cannot carry.

`note`, prose, for anything the fields cannot carry.

## The metric

Write only the components with `i` at or before `j` in the declared coordinate
order. The metric is symmetric and a transposed duplicate is refused, so writing
both is not thoroughness, it is an error.

One table per component, flat rather than nested. That costs one line per
component and it is the answer to the one place TOML is weak, which is deeply
nested structure.

Every expression is a string in the expression sub-language: integer and rational
literals, identifiers, `+ - * / ^`, parentheses, a closed list of functions and a
closed list of named constants. An identifier must be a coordinate the chart
declares, a parameter the record declares, or a named constant. Loading a record
parses that text into a syntax tree. It does not evaluate a string in any
language and it does not hand your text to a computer algebra system's reader.

## The claimed block

A list of tables, one per value you read from the literature. Each names the
`field`, which is one of the derived field names, the `value`, the `stratum` it
holds on, and the `source` you read it from. `chart` is optional, for a value
that is only meaningful in one of them.

Every value attaches to a stratum and nothing attaches to the family as a whole.
That is record 0005, and the reason it is a list rather than a table of keys: the
same field can carry different values on different strata, which is the Kerr case
where the isometry dimension is 4 where the spin vanishes and 2 elsewhere.

A value here is what the literature says. Nothing in this project has confirmed
it, and the published entry carries a marker saying so.

## The machine-written blocks

You do not write these. They are here so you can read a record somebody else's
run produced.

`derived`, a list of tables, each naming the `field`, the `value`, the `stratum`
and `chart` it holds on, the `command`, the `commit` and the `date`, and
optionally an `assumption` list. It carries no cost: the cost of a run sits on
the verification entry, per records 0006 and 0015. An assumption entry names the
expression, which side of a zero test was assumed, where it came from, and the
order it was applied at. A value computed under an assumption is a weaker claim
than one proved outright, and the list is what stops the two being read as the
same claim.

`verification`, a list of tables, each naming its `subject`, `stratum`, `chart`
and `state`. The state is one of four words and the evidence the schema requires
depends on which: `recomputed` needs the command, the commit, the date, the cost
and the two staleness anchors; `checked_against_publication` needs the publication
and the locator; `cross_checked` needs the implementation and its version;
`transcribed` needs nothing, because nothing here has checked it.

There is no `stale` field and there never will be. Staleness is computed on load
by comparing the anchors against the tree the record is loaded in, so the same
entry is fresh in the tree it was written in and stale in a later one.

## The Schwarzschild record in full

This is the worked record from record 0003, in the static exterior chart,
complete in every asserted field, with the literature values in the claimed block
and no derived block because nothing here has computed anything yet. It is the
record the schema is checked against, and it validates.

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

coverage_argument = "One stratum, marked generic, whose condition is the declared range M > 0 of the one parameter. Nothing lies outside it, so the strata cover the range."

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

[[claimed]]
field = "petrov_type"
value = "D"
stratum = "generic"
source = "the citation in the provenance block below"

[[claimed]]
field = "ricci_type"
value = "the Ricci tensor vanishes"
stratum = "generic"
source = "the citation in the provenance block below"

[[claimed]]
field = "killing_dimension"
value = 4
stratum = "generic"
source = "the citation in the provenance block below"

[provenance]
# Field names are fixed by record 0006, issue #12. The values here are a
# placeholder until the first real entry lands under issue #73.
source_kind = "secondary"
citation = "to be filled by issue #73"
locator = "to be filled by issue #73"
transcribed_on = "2026-08-07"

# No [[derived]] entries. Nothing in this repository has computed anything yet,
# and an empty derived block is the honest state rather than a gap.
```

The coordinate range excludes `r = 2*M` and the two poles because they are
singularities of this chart and not of the spacetime. Record 0005 is where that
distinction is argued.

This is now the second copy of that record in the tree, and nothing compares the
two. It is here because a document explaining a record format without a record in
it is a document nobody can follow. The copy stops when issue #73 lands the entry
as `catalogue/schwarzschild.toml`, at which point this section points at the file
instead of holding it. Until then the two can drift and no check will say so.

## Validating a record

    python -c "
    import json, sys, tomllib
    from jsonschema import Draft202012Validator
    schema = json.load(open('schema/record-1.schema.json', encoding='utf-8'))
    doc = tomllib.load(open(sys.argv[1], 'rb'))
    errs = list(Draft202012Validator(schema).iter_errors(doc))
    print('valid' if not errs else '\n'.join('/'.join(str(p) for p in e.path) + ': ' + e.message for e in errs))
    " catalogue/schwarzschild.toml

That is the schema applied by hand. It is not the gate. Issue #43 is the check
that runs it over every record, issue #36 is the loader that refuses the things a
schema cannot see, and neither exists yet.

## What the schema cannot check

A schema sees one document and it sees no other file, so these are all loader
refusals, issue #36, and not shape errors:

Whether the `id` equals the filename stem, and whether two records share an `id`.

Whether an identifier in an expression is a coordinate the chart declares, a
parameter the record declares, or a named constant. The closed grammar and the two
closed lists are issue #40.

Whether a metric component is a duplicate or a transposed duplicate of another,
which needs the coordinate order.

Whether the `stratum` and `chart` a derived or claimed value names exist on the
record.

Whether a `supersedes` or `superseded_by` names an id that exists.

Two more are not decidable by anything, and record 0005 says so rather than
promising them. Whether the declared strata cover the declared range, which is why
`coverage_argument` is prose a reader checks. And whether a chart relation's
stated transformation does what it says, which nothing here verifies.

## Where the schema was weaker than the records, and is not any more

This section held four places where the schema permitted what records 0005 and
0006 required, because it had to validate a worked record carrying none of them.
Record 0015 resolved all four and issue #107 is where they were found. What
changed, so that a reader who met the old text knows which way each went:

`coverage_argument` is required of every record.

Every claimed value names the stratum it holds on, and the claimed block is a
list of entries rather than a table of keys, because a table cannot carry two
values of one field on two strata.

`locator` is required in the provenance block. `doi`, `url` and `note` stay
optional, which is what record 0006 says of the first two and what its own
definition of the third amounts to.

`cost` sits on the verification entry and nowhere else. A derived entry carrying
one is refused, and `cost` is not one of the derived field names.

One looseness is still here and it is a different one. The shape of a cost report
is record 0011, issue #20, which has not landed, so `cost` is an object with no
required fields. What a cost report holds is open; where it is stored is not.
