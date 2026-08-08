# Writing a solution record

This is the document for somebody writing a record by hand. What a record holds
and why it holds it is decided in the decision records, chiefly
[0003](decisions/0003-the-solution-record.md) for the shape,
[0004](decisions/0004-identifiers-and-corrections.md) for the identifier,
[0005](decisions/0005-parameters-and-charts.md) for parameters, strata and
charts, and [0006](decisions/0006-provenance-and-verification.md) for provenance
and verification. This document does not restate their arguments. It says what to
type and what the machine will refuse.

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
`derived_here`, plus `citation` and `transcribed_on`. `locator`, `doi`, `url` and
`note` are also part of the block. See the section below on what is not required.

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

Keys are the derived field names, plus `source` for where you read them. A value
here is what the literature says. Nothing in this project has confirmed it, and
the published entry carries a marker saying so.

## The machine-written blocks

You do not write these. They are here so you can read a record somebody else's
run produced.

`derived`, a list of tables, each naming the `field`, the `value`, the `stratum`
and `chart` it holds on, the `command`, the `commit` and the `date`, optionally
the `cost`, and optionally an `assumption` list. An assumption entry names the
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

## What the schema does not require, and why

Four places where the schema is knowingly weaker than the decision records, all of
them held by issue #107.

`coverage_argument` is not required, and record 0005 says a record carries it.

A `stratum` on the claimed block is not required, and record 0005 says every
claimed field attaches to a stratum and that nothing attaches to the family as a
whole.

`locator` in the provenance block is not required, and record 0006 lists the
provenance fields as these and no others, marking only `doi` and `url` optional.

`cost` on a derived entry is not required, because record 0003 puts the cost of
the run on the derived entry and record 0006 puts it on the verification entry.
The schema requires it on a `recomputed` verification entry and permits it on a
derived entry, which satisfies both readings and settles neither.

The reason is the same in all four: the schema is required to validate the worked
Schwarzschild record that record 0003 publishes, and that record carries none of
the first three. Making the schema faithful to records 0005 and 0006 would refuse
the example the record format itself holds up.

This is a gap, not a decision. A record with no locator is not a complete record
and the schema will not tell you so. Until #107 is settled, the sentence a reader
needs is this one rather than the absence of an error.
