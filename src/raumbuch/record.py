"""The loader: a record becomes an object, or it is refused by name.

"Invalid record" is a shrug. Every refusal here names which refusal it is, out
of the closed vocabulary in :mod:`raumbuch.refusal`, and every one of them goes
through :func:`raumbuch.refusal.refuse`, so a test can ask which reason a
fixture triggered rather than only whether it failed.

Loading executes nothing from the record. It reads TOML into data, and every
string of the sub-language goes through the parser of issue #40, which builds a
tree and never evaluates. Nothing here reaches the algebra layer, so a record is
data from the moment it is read until something in ``src/raumbuch/algebra/``
asks for arithmetic, and that directory declares no operations.

What is not here is as fixed as what is. The schema in ``schema/`` sees one
document and sees no other file; this sees the document and the shape around it.
Where the two overlap the loader still refuses, because a loader that trusted a
check it does not run is a loader that accepts whatever reaches it.

The refusals of record 0004 that need the catalogue rather than the record - a
`supersedes` naming an id that is not in the index, a half-written link between
two records, a `correction` list with a gap in it - are :mod:`raumbuch.catalogue`
and are not here. The three fields those refusals read are carried by the record
below, because a field nothing parses is a field the index would have to reach
back into the raw document for.
"""

from __future__ import annotations

import dataclasses
import tomllib
from pathlib import Path
from typing import Any

from raumbuch import expression, refusal

#: Record 0002 fixes four dimensions, and issue #35 and issue #36 are named
#: there as the two that refuse anything else rather than accept a record
#: nothing can classify.
DIMENSION = 4

#: The value of ``schema_version`` this loader reads. A second version of the
#: record format is a second schema file and a second loader path, per record
#: 0003, and never a widening of this one.
SCHEMA_VERSION = "1"

#: Record 0005. A relation outside this is a fifth kind of chart relationship
#: nobody has argued for.
CHART_RELATIONS: tuple[str, ...] = ("extends", "overlaps", "same_region")

#: Record 0006, closed.
SOURCE_KINDS: tuple[str, ...] = ("derived_here", "primary", "secondary")

#: Record 0006, closed. Four words for four epistemic positions.
VERIFICATION_STATES: tuple[str, ...] = (
    "checked_against_publication",
    "cross_checked",
    "recomputed",
    "transcribed",
)


@dataclasses.dataclass(frozen=True)
class Chart:
    """One chart, with its metric keyed by the index pair as written."""

    name: str
    coordinates: tuple[str, ...]
    region: str
    ranges: tuple[expression.Condition, ...]
    identifications: tuple[str, ...]
    metric: dict[tuple[str, str], expression.Node]
    relation: dict[str, Any] | None


@dataclasses.dataclass(frozen=True)
class Parameter:
    name: str
    domain: str
    meaning: str
    range: expression.Condition


@dataclasses.dataclass(frozen=True)
class Stratum:
    name: str
    generic: bool
    condition: expression.Condition


@dataclasses.dataclass(frozen=True)
class Record:
    """A loaded record. The asserted fields are parsed; the rest is carried.

    The claimed, derived and verification blocks stay as the data they were,
    because nothing here computes and a value read from the literature is not
    the loader's to interpret. What the loader does to them is refuse the ones
    that point at a stratum, a chart or an evidence shape the record does not
    have.
    """

    id: str
    version: int
    supersedes: tuple[str, ...]
    superseded_by: str | None
    corrections: tuple[dict[str, Any], ...]
    name: str
    aliases: tuple[str, ...]
    dimension: int
    signature: str
    coverage_argument: str
    parameters: tuple[Parameter, ...]
    strata: tuple[Stratum, ...]
    charts: tuple[Chart, ...]
    matter: dict[str, Any]
    provenance: dict[str, Any]
    claimed: tuple[dict[str, Any], ...]
    derived: tuple[dict[str, Any], ...]
    verification: tuple[dict[str, Any], ...]

    @property
    def parameter_names(self) -> frozenset[str]:
        return frozenset(parameter.name for parameter in self.parameters)

    @property
    def stratum_names(self) -> frozenset[str]:
        return frozenset(stratum.name for stratum in self.strata)

    @property
    def chart_names(self) -> frozenset[str]:
        return frozenset(chart.name for chart in self.charts)


def load(path: Path) -> Record:
    """The record at ``path``, or a refusal naming what is wrong with it."""
    return loads(path.read_bytes(), path.stem)


def loads(data: bytes, stem: str) -> Record:
    """The record in ``data``, judged as though it sat at ``<stem>.toml``."""
    try:
        document = tomllib.loads(data.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as broken:
        refusal.refuse(refusal.NOT_A_DOCUMENT, f"not readable as TOML: {broken}")
    return _build(document, stem)


def _build(document: dict[str, Any], stem: str) -> Record:
    _identity(document, stem)
    parameters = _parameters(document)
    declared = frozenset(parameter.name for parameter in parameters)
    strata = _strata(document, declared)
    charts = _charts(document, declared)
    record = Record(
        id=_text(document, "id"),
        version=_whole(document, "version"),
        supersedes=tuple(_names(document, "supersedes")),
        superseded_by=(
            None
            if "superseded_by" not in document
            else _text(document, "superseded_by")
        ),
        corrections=tuple(_entries(document, "correction")),
        name=_text(document, "name"),
        aliases=tuple(_listing(document, "aliases")),
        dimension=_whole(document, "dimension"),
        signature=_text(document, "signature"),
        coverage_argument=_text(document, "coverage_argument"),
        parameters=parameters,
        strata=strata,
        charts=charts,
        matter=_table(document, "matter"),
        provenance=_table(document, "provenance"),
        claimed=tuple(_entries(document, "claimed")),
        derived=tuple(_entries(document, "derived")),
        verification=tuple(_entries(document, "verification")),
    )
    _provenance(record)
    _values_point_somewhere(record)
    _derived_entries(record)
    _verification_entries(record)
    return record


def _identity(document: dict[str, Any], stem: str) -> None:
    version = _text(document, "schema_version")
    if version != SCHEMA_VERSION:
        refusal.refuse(
            refusal.UNKNOWN_SCHEMA_VERSION,
            f"schema_version is {version!r} and this loader reads {SCHEMA_VERSION!r}",
        )
    identifier = _text(document, "id")
    if identifier != stem:
        refusal.refuse(
            refusal.ID_IS_NOT_THE_FILENAME,
            f"the id is {identifier!r} and the file is {stem!r}.toml",
        )
    dimension = _whole(document, "dimension")
    if dimension != DIMENSION:
        refusal.refuse(
            refusal.DIMENSION_IS_NOT_FOUR,
            f"dimension is {dimension} and record 0002 fixes {DIMENSION}",
        )


def _parameters(document: dict[str, Any]) -> tuple[Parameter, ...]:
    declared = [_text(entry, "name") for entry in _listing(document, "parameter")]
    parameters = []
    for entry in _listing(document, "parameter"):
        condition = expression.parse_condition(_text(entry, "range"))
        _only_parameters(condition, frozenset(declared), "a parameter range")
        parameters.append(
            Parameter(
                name=_text(entry, "name"),
                domain=_text(entry, "domain"),
                meaning=_text(entry, "meaning"),
                range=condition,
            )
        )
    return tuple(parameters)


def _strata(document: dict[str, Any], declared: frozenset[str]) -> tuple[Stratum, ...]:
    strata = []
    for entry in _listing(document, "stratum"):
        condition = expression.parse_condition(_text(entry, "condition"))
        _only_parameters(condition, declared, "a stratum condition")
        strata.append(
            Stratum(
                name=_text(entry, "name"),
                generic=bool(entry.get("generic", False)),
                condition=condition,
            )
        )
    generic = [stratum.name for stratum in strata if stratum.generic]
    if not generic:
        refusal.refuse(
            refusal.NO_GENERIC_STRATUM,
            "no stratum is marked generic, so nothing says what the family is "
            "away from its special cases",
        )
    if len(generic) > 1:
        refusal.refuse(
            refusal.TWO_GENERIC_STRATA,
            f"more than one generic stratum: {', '.join(sorted(generic))}",
        )
    return tuple(strata)


def _only_parameters(
    condition: expression.Condition, declared: frozenset[str], where: str
) -> None:
    """A condition outside a chart may name a parameter or a constant, nothing else.

    There is no chart here, so a coordinate name is undeclared in this position
    rather than merely out of place, and reading it as an identifier the record
    forgot to declare is the diagnosis that sends the writer to the right line.
    """
    unknown = expression.names(condition) - declared - frozenset(expression.CONSTANTS)
    if unknown:
        refusal.refuse(
            refusal.STRATUM_NAMES_AN_UNDECLARED_PARAMETER,
            f"{where} names {', '.join(sorted(unknown))}, which the record "
            "does not declare as a parameter",
        )


def _charts(document: dict[str, Any], declared: frozenset[str]) -> tuple[Chart, ...]:
    entries = _listing(document, "chart")
    names = [_text(entry, "name") for entry in entries]
    charts = [_chart(entry, declared) for entry in entries]
    for position, chart in enumerate(charts):
        if position == 0:
            continue
        _relation(chart, names)
    return tuple(charts)


def _chart(entry: dict[str, Any], declared: frozenset[str]) -> Chart:
    coordinates = tuple(_listing(entry, "coordinates"))
    scope = declared | frozenset(coordinates) | frozenset(expression.CONSTANTS)
    ranges = tuple(
        _in_scope(expression.parse_condition(text), scope, "a coordinate range")
        for text in _listing(entry, "range")
    )
    return Chart(
        name=_text(entry, "name"),
        coordinates=coordinates,
        region=_text(entry, "region"),
        ranges=ranges,
        identifications=tuple(_listing(entry, "identifications")),
        metric=_metric(entry, coordinates, scope),
        relation=entry.get("relation"),
    )


def _in_scope(node: Any, scope: frozenset[str], where: str) -> Any:
    unknown = expression.names(node) - scope
    if unknown:
        refusal.refuse(
            refusal.UNDECLARED_IDENTIFIER,
            f"{where} names {', '.join(sorted(unknown))}, which is neither a "
            "coordinate of this chart, nor a parameter of this record, nor a "
            "named constant",
        )
    return node


def _metric(
    entry: dict[str, Any], coordinates: tuple[str, ...], scope: frozenset[str]
) -> dict[tuple[str, str], expression.Node]:
    order = {name: position for position, name in enumerate(coordinates)}
    components: dict[tuple[str, str], expression.Node] = {}
    for component in _listing(entry, "metric"):
        pair = (_text(component, "i"), _text(component, "j"))
        _index_pair(pair, order, components)
        components[pair] = _in_scope(
            expression.parse(_text(component, "value")), scope, "a metric component"
        )
    return components


def _index_pair(
    pair: tuple[str, str],
    order: dict[str, int],
    seen: dict[tuple[str, str], expression.Node],
) -> None:
    for index in pair:
        if index not in order:
            refusal.refuse(
                refusal.METRIC_INDEX_IS_NOT_A_COORDINATE,
                f"a metric component is indexed by {index!r}, which this "
                "chart does not declare as a coordinate",
            )
    if pair in seen:
        refusal.refuse(
            refusal.METRIC_COMPONENT_DECLARED_TWICE,
            f"the component {pair[0]}{pair[1]} is written twice, and taking "
            "the last one silently is how one of them is lost",
        )
    if pair[::-1] in seen:
        refusal.refuse(
            refusal.METRIC_COMPONENT_TRANSPOSED,
            f"the component {pair[0]}{pair[1]} is the transpose of one already "
            "written, and the metric is symmetric, so this is the same "
            "component twice rather than a second one",
        )
    if order[pair[0]] > order[pair[1]]:
        refusal.refuse(
            refusal.METRIC_COMPONENT_OUT_OF_ORDER,
            f"the component {pair[0]}{pair[1]} is below the diagonal in the "
            f"declared coordinate order: write {pair[1]}{pair[0]}",
        )


def _relation(chart: Chart, names: list[str]) -> None:
    if chart.relation is None:
        refusal.refuse(
            refusal.CHART_WITHOUT_A_RELATION,
            f"the chart {chart.name!r} is not the first and names no relation "
            "to another, which is what turns one entry into two catalogues",
        )
    kind = _text(chart.relation, "kind")
    if kind not in CHART_RELATIONS:
        refusal.refuse(
            refusal.CHART_RELATION_OUTSIDE_THE_VOCABULARY,
            f"{kind!r} is not one of {', '.join(CHART_RELATIONS)}",
        )
    related = _text(chart.relation, "chart")
    if related not in names:
        refusal.refuse(
            refusal.CHART_RELATION_NAMES_NO_CHART,
            f"the chart {chart.name!r} relates to {related!r}, which this "
            "record does not declare",
        )


def _provenance(record: Record) -> None:
    kind = _text(record.provenance, "source_kind")
    if kind not in SOURCE_KINDS:
        refusal.refuse(
            refusal.SOURCE_KIND_OUTSIDE_THE_VOCABULARY,
            f"{kind!r} is not one of {', '.join(SOURCE_KINDS)}",
        )


def _values_point_somewhere(record: Record) -> None:
    """Every claimed, derived and verification entry names a stratum that exists.

    Record 0005 attaches every value to a stratum and nothing to the family as a
    whole, so a value pointing at a stratum the record does not declare is a
    value nobody can say where it holds.
    """
    for block, entries in (
        ("claimed", record.claimed),
        ("derived", record.derived),
        ("verification", record.verification),
    ):
        for entry in entries:
            _points_at(block, entry, "stratum", record.stratum_names)
            _points_at(block, entry, "chart", record.chart_names)


def _points_at(
    block: str, entry: dict[str, Any], key: str, declared: frozenset[str]
) -> None:
    named = entry.get(key)
    if named is None or named in declared:
        return
    reason = (
        refusal.VALUE_NAMES_NO_STRATUM
        if key == "stratum"
        else refusal.VALUE_NAMES_NO_CHART
    )
    refusal.refuse(
        reason,
        f"a {block} entry names the {key} {named!r}, which this record does "
        "not declare",
    )


def _derived_entries(record: Record) -> None:
    """A derived value carries its stamp, and something that verified it.

    Record 0003 puts the command, the commit and the date on every derived
    entry, because a derived field transcribed from a book instead of computed
    is the defect this project exists to remove. Record 0006 adds that a derived
    value with no verification entry is refused, which is the half a schema
    cannot see: it needs the other block.
    """
    verified = {
        (entry.get("subject"), entry.get("stratum"), entry.get("chart"))
        for entry in record.verification
    }
    for entry in record.derived:
        for stamp in ("command", "commit", "date"):
            if not entry.get(stamp):
                refusal.refuse(
                    refusal.DERIVED_ENTRY_WITHOUT_ITS_STAMP,
                    f"a derived {entry.get('field')!r} carries no {stamp}, and "
                    "a derived value with a blank where its run should be is "
                    "a value nobody can reproduce",
                )
        key = (entry.get("field"), entry.get("stratum"), entry.get("chart"))
        if key not in verified:
            refusal.refuse(
                refusal.DERIVED_VALUE_WITH_NO_VERIFICATION,
                f"the derived {entry.get('field')!r} on stratum "
                f"{entry.get('stratum')!r} carries no verification entry",
            )


def _verification_entries(record: Record) -> None:
    """The evidence a verification entry carries matches the state it claims.

    Record 0006's four states are four different epistemic positions, and an
    entry claiming one while carrying the evidence of another collapses two of
    them. Three states each need something, and the fourth needs nothing
    because nothing here has checked it.
    """
    needed = {
        "recomputed": ("command", refusal.RECOMPUTATION_WITH_NO_COMMAND),
        "checked_against_publication": (
            "publication",
            refusal.PUBLICATION_CHECK_WITH_NO_PUBLICATION,
        ),
        "cross_checked": (
            "implementation",
            refusal.CROSS_CHECK_WITH_NO_IMPLEMENTATION,
        ),
    }
    for entry in record.verification:
        state = _text(entry, "state")
        if state not in VERIFICATION_STATES:
            refusal.refuse(
                refusal.VERIFICATION_STATE_OUTSIDE_THE_VOCABULARY,
                f"{state!r} is not one of {', '.join(VERIFICATION_STATES)}",
            )
        if state not in needed:
            continue
        field, reason = needed[state]
        if not entry.get(field):
            refusal.refuse(
                reason,
                f"a verification entry says {state!r} and carries no {field}",
            )


def _text(table: Any, key: str) -> str:
    value = _present(table, key)
    if not isinstance(value, str):
        refusal.refuse(
            refusal.FIELD_OF_THE_WRONG_KIND,
            f"{key} is {type(value).__name__} and this field is text",
        )
    return value


def _whole(table: Any, key: str) -> int:
    value = _present(table, key)
    if not isinstance(value, int) or isinstance(value, bool):
        refusal.refuse(
            refusal.FIELD_OF_THE_WRONG_KIND,
            f"{key} is {type(value).__name__} and this field is a whole number",
        )
    return value


def _listing(table: Any, key: str) -> list[Any]:
    value = table.get(key, [])
    if not isinstance(value, list):
        refusal.refuse(
            refusal.FIELD_OF_THE_WRONG_KIND,
            f"{key} is {type(value).__name__} and this field is a list",
        )
    return value


def _names(table: Any, key: str) -> list[str]:
    """A list whose every element is text.

    ``supersedes`` holds ids, and an id is compared against the index by
    equality. A number in that list compares equal to nothing and would read
    downstream as an id the catalogue does not hold, which is a different
    refusal from the one the record earned.
    """
    listed = _listing(table, key)
    for element in listed:
        if not isinstance(element, str):
            refusal.refuse(
                refusal.FIELD_OF_THE_WRONG_KIND,
                f"an entry of {key} is {type(element).__name__} and every entry "
                "of that list is text",
            )
    return listed


def _entries(document: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """A list whose every element is a table.

    The parameter, stratum and chart blocks each read a required text field out
    of an entry first, so a string where a table was due meets :func:`_present`
    and is refused there. The claimed, derived and verification blocks are
    carried rather than read, and the first thing that touches one of their
    entries asks it for a key. A string has no keys, and an AttributeError
    about ``get`` is the shape this vocabulary exists to replace.
    """
    entries = _listing(document, key)
    for entry in entries:
        if not isinstance(entry, dict):
            refusal.refuse(
                refusal.FIELD_OF_THE_WRONG_KIND,
                f"an entry of {key} is {type(entry).__name__} and every entry "
                "of that block is a table",
            )
    return entries


def _table(document: dict[str, Any], key: str) -> dict[str, Any]:
    value = _present(document, key)
    if not isinstance(value, dict):
        refusal.refuse(
            refusal.FIELD_OF_THE_WRONG_KIND,
            f"{key} is {type(value).__name__} and this field is a table",
        )
    return value


def _present(table: Any, key: str) -> Any:
    if not isinstance(table, dict) or key not in table:
        refusal.refuse(
            refusal.FIELD_MISSING,
            f"no {key}, and this record cannot be read without one",
        )
    return table[key]
