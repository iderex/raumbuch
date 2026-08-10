"""One place a refusal comes from, and the closed vocabulary it speaks.

"Invalid record" is not a diagnostic, it is a shrug. Everything this project
refuses names which refusal it is, out of a list written here, so that a caller
can ask which reason fired rather than only whether something failed, and so
that a test can compare the set of reasons a fixture triggered against the set
it was written to trigger.

Every refusal goes through :func:`refuse`. Not one raise per kind of error
scattered across a parser and a loader, but one function, so that adding a
reason is one visible change and so that the grep proving it is a grep for one
name.

The vocabulary is a closed list rather than a string a caller invents at the
call site. A reason spelled two ways is two reasons to everything downstream,
and the fixture corpus of issue #38 counts them.
"""

from __future__ import annotations

from typing import NoReturn

# The parser of issue #40. Each reason says what failure it prevents, which is
# what a reader needs and is not the same as what rule of the grammar it fell
# out of. The grammar is docs/expression-language.md.

#: A field that is present and blank. Read downstream as the number zero, which
#: is a metric component somebody did not write rather than one they meant.
EMPTY_EXPRESSION = "empty-expression"

#: A character outside ASCII. A Cyrillic small a and a Latin small a are two
#: names no reader can tell apart, in a file people download.
NON_ASCII_CHARACTER = "non-ascii-character"

#: A character the grammar has no token for. This is where an expression
#: reaching for the host stops: a full stop, a bracket, a quotation mark, a
#: comma, a colon and a semicolon are all outside the alphabet.
UNKNOWN_CHARACTER = "unknown-character"

#: A number with a decimal point or an exponent marker. Record 0009 keeps
#: floating point out of the classification path, and a record's text is the
#: one door it could come in through.
DECIMAL_LITERAL = "decimal-literal"

#: ``**`` where the grammar spells the operator ``^``. The mistake somebody
#: whose last language was Python makes on the first line they write.
POWER_IS_CARET = "power-is-caret"

#: A call to a name outside the closed function list, which includes calling a
#: parameter as though it were a function.
UNKNOWN_FUNCTION = "unknown-function"

#: A call with no argument or with more than one. Every admitted function takes
#: exactly one, so a comma inside a call is this rather than a stray character.
FUNCTION_TAKES_ONE_ARGUMENT = "function-takes-one-argument"

#: A function's name standing where a coordinate would. ``sin`` alone is not a
#: value, and reading it as an undeclared identifier would send the writer
#: looking for a declaration instead of for the missing argument.
FUNCTION_NAME_WITHOUT_ARGUMENT = "function-name-without-argument"

#: An exponent that is not an integer literal. A rational exponent leaves the
#: rational function field of record 0009 for an algebraic extension that
#: record says is not entered, and a symbolic one leaves it for something
#: wider still.
NON_INTEGER_EXPONENT = "non-integer-exponent"

#: A bracket that opens and does not close.
UNCLOSED_PARENTHESIS = "unclosed-parenthesis"

#: A token where the grammar expects another one.
UNEXPECTED_TOKEN = "unexpected-token"

#: Tokens after a complete expression. Where a statement separator arrives,
#: this is what meets it.
TRAILING_INPUT = "trailing-input"

#: A relational operator in a field that holds a value. ``value = "r > 0"`` is
#: a condition written where a metric component was due, and reading it as a
#: syntax error would send the writer hunting for a bracket.
COMPARISON_IN_AN_EXPRESSION = "comparison-in-an-expression"

#: A field that holds a condition, carrying no relational operator. A
#: coordinate range of ``r`` restricts nothing and was meant to say something.
COMPARISON_EXPECTED = "comparison-expected"

#: ``0 < theta < pi``, which reads as one statement and is two. Refused rather
#: than guessed at, because the guess is right until the day it is not.
CHAINED_COMPARISON = "chained-comparison"

#: Brackets or calls nested deeper than the parser will descend. Without it the
#: descent runs out of stack on a file somebody downloaded, and an interpreter
#: error carrying no reason is exactly what this vocabulary exists to replace.
EXPRESSION_TOO_DEEP = "expression-too-deep"

#: An integer literal with more digits than the interpreter will convert. The
#: conversion refuses it below this parser, in a language about digit limits
#: rather than about records, so the parser refuses it first and by name.
NUMBER_TOO_LONG = "number-too-long"

PARSER_REASONS: tuple[str, ...] = (
    EMPTY_EXPRESSION,
    NON_ASCII_CHARACTER,
    UNKNOWN_CHARACTER,
    DECIMAL_LITERAL,
    POWER_IS_CARET,
    UNKNOWN_FUNCTION,
    FUNCTION_TAKES_ONE_ARGUMENT,
    FUNCTION_NAME_WITHOUT_ARGUMENT,
    NON_INTEGER_EXPONENT,
    UNCLOSED_PARENTHESIS,
    UNEXPECTED_TOKEN,
    TRAILING_INPUT,
    COMPARISON_IN_AN_EXPRESSION,
    COMPARISON_EXPECTED,
    CHAINED_COMPARISON,
    EXPRESSION_TOO_DEEP,
    NUMBER_TOO_LONG,
)

# The loader of issue #36. Each reason names a failure that a schema cannot
# see, because a schema reads one document and the loader reads the shape
# around it. Where the two overlap the loader refuses anyway: a loader that
# trusts a check it does not run accepts whatever reaches it.

#: Bytes that are not a TOML document at all.
NOT_A_DOCUMENT = "not-a-document"

#: A required field absent. The detail names which, because "invalid record" is
#: what this vocabulary exists to replace.
FIELD_MISSING = "field-missing"

#: A field present and of the wrong kind, which is where a loader that read it
#: anyway would fail somewhere else with a message about neither.
FIELD_OF_THE_WRONG_KIND = "field-of-the-wrong-kind"

#: A ``schema_version`` this loader does not read. Record 0003 makes a second
#: format a second file, so a record from the future is refused rather than
#: read with the fields that happen to match.
UNKNOWN_SCHEMA_VERSION = "unknown-schema-version"

#: An ``id`` that is not the filename stem. Record 0004: two people adding the
#: same solution collide on one path, and that only holds while the id and the
#: path are the same fact.
ID_IS_NOT_THE_FILENAME = "id-is-not-the-filename"

#: An ``id`` outside the slug grammar of record 0004. The schema refuses the
#: same thing, and the loader refuses it too rather than trusting a check it
#: does not run: nothing in the gate applies the schema until issue #43 lands,
#: and a consumer loading a downloaded record applies neither.
ID_OUTSIDE_THE_GRAMMAR = "id-outside-the-grammar"

#: A ``dimension`` other than four. Record 0002 names the loader as what
#: refuses a record nothing in this project can classify.
DIMENSION_IS_NOT_FOUR = "dimension-is-not-four"

#: No stratum marked generic. Record 0005: without one, nothing says what the
#: family is away from its special cases.
NO_GENERIC_STRATUM = "no-generic-stratum"

#: More than one generic stratum, which is two answers to that question.
TWO_GENERIC_STRATA = "two-generic-strata"

#: An identifier in a metric component or a coordinate range that is neither a
#: coordinate of that chart, nor a parameter of the record, nor a named
#: constant. This is what stops a record smuggling in a symbol whose meaning a
#: reader cannot see.
UNDECLARED_IDENTIFIER = "undeclared-identifier"

#: The same, in a stratum condition or a parameter range, where there is no
#: chart and so no coordinate is in scope either.
STRATUM_NAMES_AN_UNDECLARED_PARAMETER = "stratum-names-an-undeclared-parameter"

#: A metric component indexed by something the chart does not declare as a
#: coordinate.
METRIC_INDEX_IS_NOT_A_COORDINATE = "metric-index-is-not-a-coordinate"

#: One index pair written twice. Taking the last one silently is how the other
#: is lost without anybody seeing it go.
METRIC_COMPONENT_DECLARED_TWICE = "metric-component-declared-twice"

#: An index pair and its transpose. The metric is symmetric, so this is the
#: same component twice rather than two components.
METRIC_COMPONENT_TRANSPOSED = "metric-component-transposed"

#: A component below the diagonal in the declared coordinate order. Record 0003
#: says write only the components with ``i`` at or before ``j``, and a record
#: half in one convention is a record whose symmetry nobody checked.
METRIC_COMPONENT_OUT_OF_ORDER = "metric-component-out-of-order"

#: A chart after the first with no relation to another. Record 0005: this is
#: the mistake that turns one entry into two catalogues.
CHART_WITHOUT_A_RELATION = "chart-without-a-relation"

#: A chart relation outside the closed vocabulary of record 0005.
CHART_RELATION_OUTSIDE_THE_VOCABULARY = "chart-relation-outside-the-vocabulary"

#: A chart relation naming a chart the record does not declare.
CHART_RELATION_NAMES_NO_CHART = "chart-relation-names-no-chart"

#: A claimed, derived or verification entry naming a stratum that does not
#: exist. Record 0005 attaches every value to a stratum, so this is a value
#: nobody can say where it holds.
VALUE_NAMES_NO_STRATUM = "value-names-no-stratum"

#: The same, for a chart.
VALUE_NAMES_NO_CHART = "value-names-no-chart"

#: A ``source_kind`` outside the closed vocabulary of record 0006.
SOURCE_KIND_OUTSIDE_THE_VOCABULARY = "source-kind-outside-the-vocabulary"

#: A verification state outside record 0006's four words. A fifth word is an
#: amendment to that record and not a value written into a file.
VERIFICATION_STATE_OUTSIDE_THE_VOCABULARY = "verification-state-outside-the-vocabulary"

#: A verification entry that says it recomputed and names no command.
RECOMPUTATION_WITH_NO_COMMAND = "recomputation-with-no-command"

#: One that says it was checked against a publication and names none.
PUBLICATION_CHECK_WITH_NO_PUBLICATION = "publication-check-with-no-publication"

#: One that says it was cross-checked and names no implementation.
CROSS_CHECK_WITH_NO_IMPLEMENTATION = "cross-check-with-no-implementation"

#: A derived entry with no command, commit or date. Record 0003: a derived
#: field transcribed from a book instead of computed is the defect this project
#: exists to remove, and a blank where the run should be is how it arrives.
DERIVED_ENTRY_WITHOUT_ITS_STAMP = "derived-entry-without-its-stamp"

#: A derived value carrying no verification entry at all, which record 0006
#: refuses and which needs both blocks to see.
DERIVED_VALUE_WITH_NO_VERIFICATION = "derived-value-with-no-verification"

LOADER_REASONS: tuple[str, ...] = (
    NOT_A_DOCUMENT,
    FIELD_MISSING,
    FIELD_OF_THE_WRONG_KIND,
    UNKNOWN_SCHEMA_VERSION,
    ID_IS_NOT_THE_FILENAME,
    ID_OUTSIDE_THE_GRAMMAR,
    DIMENSION_IS_NOT_FOUR,
    NO_GENERIC_STRATUM,
    TWO_GENERIC_STRATA,
    UNDECLARED_IDENTIFIER,
    STRATUM_NAMES_AN_UNDECLARED_PARAMETER,
    METRIC_INDEX_IS_NOT_A_COORDINATE,
    METRIC_COMPONENT_DECLARED_TWICE,
    METRIC_COMPONENT_TRANSPOSED,
    METRIC_COMPONENT_OUT_OF_ORDER,
    CHART_WITHOUT_A_RELATION,
    CHART_RELATION_OUTSIDE_THE_VOCABULARY,
    CHART_RELATION_NAMES_NO_CHART,
    VALUE_NAMES_NO_STRATUM,
    VALUE_NAMES_NO_CHART,
    SOURCE_KIND_OUTSIDE_THE_VOCABULARY,
    VERIFICATION_STATE_OUTSIDE_THE_VOCABULARY,
    RECOMPUTATION_WITH_NO_COMMAND,
    PUBLICATION_CHECK_WITH_NO_PUBLICATION,
    CROSS_CHECK_WITH_NO_IMPLEMENTATION,
    DERIVED_ENTRY_WITHOUT_ITS_STAMP,
    DERIVED_VALUE_WITH_NO_VERIFICATION,
)

# The catalogue index of issue #41. Each reason names a failure that needs the
# set of records rather than one of them. The schema reads one document, the
# loader reads one document and the shape around it, and these read every
# record at once: which of them exist, and which ids they spend. Record 0004
# writes the list they come from.

#: One ``id`` on two records. Record 0004 makes the id the primary key of the
#: catalogue and the thing a citation names, so two records answering to it is
#: two answers to a citation.
ID_CARRIED_BY_TWO_RECORDS = "id-carried-by-two-records"

#: A ``supersedes`` or ``superseded_by`` naming an id the catalogue does not
#: hold. A reader following it arrives nowhere, which is worse than a record
#: that never claimed a successor.
SUPERSESSION_NAMES_NO_RECORD = "supersession-names-no-record"

#: A supersession written from one end only. Record 0004 requires both ends
#: because a reader arriving at the old id has to be sent forward and a reader
#: arriving at the new one has to know what it displaced, and a link with one
#: end serves whichever of the two arrived from the wrong side.
HALF_WRITTEN_SUPERSESSION = "half-written-supersession"

#: A ``correction`` list that is not exactly the versions from 2 up to the
#: record's own. Record 0004 makes the list the history a consumer reads
#: instead of the old copy, so a gap in it is a correction nobody is told about
#: and a repeat is one told twice.
CORRECTION_LIST_DOES_NOT_RUN_TO_THE_VERSION = (
    "correction-list-does-not-run-to-the-version"
)

#: A pin naming an id the catalogue does not hold. Record 0004: this is a
#: refusal rather than an empty result, because an id this release never had
#: and an id it took away are opposite statements and a caller receiving
#: nothing back cannot tell them apart.
UNKNOWN_IDENTIFIER = "unknown-identifier"

CATALOGUE_REASONS: tuple[str, ...] = (
    ID_CARRIED_BY_TWO_RECORDS,
    SUPERSESSION_NAMES_NO_RECORD,
    HALF_WRITTEN_SUPERSESSION,
    CORRECTION_LIST_DOES_NOT_RUN_TO_THE_VERSION,
    UNKNOWN_IDENTIFIER,
)

#: Every reason anything here may be refused for, and nothing outside it is a
#: reason :func:`refuse` will accept. The three groups are the three things
#: that read a record: the parser reads one string, the loader reads one
#: document, the index reads the set. The tuple is written to be added to.
REASONS: tuple[str, ...] = PARSER_REASONS + LOADER_REASONS + CATALOGUE_REASONS


class Refused(Exception):
    """What was refused, why, and where.

    ``reason`` is one of :data:`REASONS` and is what a test compares. ``detail``
    is the sentence a person reads. ``where`` is the position in the text, or
    ``None`` where the refusal is not about a position.
    """

    def __init__(self, reason: str, detail: str, where: int | None = None) -> None:
        self.reason = reason
        self.detail = detail
        self.where = where
        super().__init__(str(self))

    def __str__(self) -> str:
        position = "" if self.where is None else f" at character {self.where + 1}"
        return f"{self.reason}{position}: {self.detail}"


def refuse(reason: str, detail: str, where: int | None = None) -> NoReturn:
    """Refuse, naming the reason. The only route to a :class:`Refused`.

    A reason outside the closed vocabulary is itself refused, here, with an
    assertion rather than with a :class:`Refused`. The difference is deliberate:
    a record carrying bad bytes is a refusal a caller handles, and a call site
    inventing a reason is a defect in this repository that no caller can do
    anything about.
    """
    if reason not in REASONS:
        raise AssertionError(f"not a declared refusal reason: {reason!r}")
    raise Refused(reason, detail, where)
