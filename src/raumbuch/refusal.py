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
)

#: Every reason anything here may be refused for. Issue #36 adds the loader's
#: reasons to this tuple beside the parser's, and nothing outside it is a
#: reason :func:`refuse` will accept.
REASONS: tuple[str, ...] = PARSER_REASONS


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
