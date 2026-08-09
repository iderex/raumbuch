"""The expression sub-language of record 0003, and the parser that reads it.

The grammar, the closed function list, the closed constant list and the declared
relations are argued in ``docs/expression-language.md``. This module is the
executable half of that document, and a test compares the two so neither can
drift alone.

What this module does not do is the point of it. It builds a tree of the
dataclasses below and nothing else. It evaluates no string, it hands no text to
an algebra system's reader, and it names no algebra type: record 0001 puts every
one of those behind ``src/raumbuch/algebra/``, and turning one of these trees
into the arithmetic of record 0009 happens there. So a catalogue file is data
here, and loading one is reading rather than running.

Every refusal goes through :func:`raumbuch.refusal.refuse`.
"""

from __future__ import annotations

import dataclasses
import re
from fractions import Fraction
from typing import NoReturn

from raumbuch import refusal

#: The closed constant list. An identifier is admitted where the chart declares
#: it as a coordinate, the record declares it as a parameter, or it is here.
CONSTANTS: tuple[str, ...] = ("pi",)

#: The functions the normal form is written in, each with its derivative in the
#: same list. The derivative is what record 0009 requires of this list and the
#: table in the document is where it is shown row by row.
NORMAL_FORM_FUNCTIONS: tuple[str, ...] = (
    "cos",
    "cosh",
    "exp",
    "log",
    "sin",
    "sinh",
)

#: Admitted, and rewritten into the six above before any arithmetic happens.
#: They add a spelling and not a domain, so closure under differentiation is
#: inherited rather than argued again.
DERIVED_FUNCTIONS: dict[str, str] = {
    "cot": "cos(u)/sin(u)",
    "coth": "cosh(u)/sinh(u)",
    "tan": "sin(u)/cos(u)",
    "tanh": "sinh(u)/cosh(u)",
}

#: Every name a call may use. Anything else is refused by name.
FUNCTIONS: tuple[str, ...] = tuple(
    sorted(NORMAL_FORM_FUNCTIONS + tuple(DERIVED_FUNCTIONS))
)

#: The relations this project relies on among the admitted functions, each as a
#: rewrite to the normal form. Record 0009 requires that the set is declared and
#: that nothing outside it is relied on; the operation that applies them is on
#: the algebra interface of record 0001 and does not exist yet, so this tuple is
#: a declaration and not yet a thing any run has used.
RELATIONS: tuple[tuple[str, str], ...] = (
    ("sin(u)^2 + cos(u)^2 = 1", "sin(u)^2 becomes 1 - cos(u)^2"),
    ("cosh(u)^2 - sinh(u)^2 = 1", "sinh(u)^2 becomes cosh(u)^2 - 1"),
    ("exp(u)*exp(v) = exp(u+v)", "a product of exponentials becomes one"),
    ("exp(0) = 1", "exp of a vanishing argument becomes 1"),
    *(
        (f"{name}(u) = {body}", "the definition above")
        for name, body in sorted(DERIVED_FUNCTIONS.items())
    ),
)


@dataclasses.dataclass(frozen=True)
class Number:
    """An integer literal. A rational is a quotient of two of these."""

    value: Fraction


@dataclasses.dataclass(frozen=True)
class Name:
    """An identifier. Whether it is declared is the loader's question, #36."""

    text: str


@dataclasses.dataclass(frozen=True)
class Apply:
    """A function from :data:`FUNCTIONS`, applied to its one argument."""

    function: str
    argument: Node


@dataclasses.dataclass(frozen=True)
class Negate:
    operand: Node


@dataclasses.dataclass(frozen=True)
class Operation:
    """One of ``+ - * /`` between two operands."""

    operator: str
    left: Node
    right: Node


@dataclasses.dataclass(frozen=True)
class Power:
    """A base raised to an integer exponent. The grammar admits no other."""

    base: Node
    exponent: int


Node = Number | Name | Apply | Negate | Operation | Power


@dataclasses.dataclass(frozen=True)
class Comparison:
    """Two expressions and a relation between them.

    A coordinate range, a parameter range and a stratum condition are this, and
    a metric component is not. Both are the sub-language of record 0003; which
    of the two a field holds is fixed per field and is in the document.
    """

    relation: str
    left: Node
    right: Node


@dataclasses.dataclass(frozen=True)
class Conjunction:
    """Comparisons joined by ``and``. There is no ``or`` and no ``not``."""

    parts: tuple[Comparison, ...]


Condition = Comparison | Conjunction

#: The relational operators a condition may use. ``and`` is the one connective,
#: so a name spelled ``and`` cannot be a coordinate, and the document says so
#: where a person choosing coordinate names will read it.
COMPARISONS: tuple[str, ...] = ("!=", "<", "<=", "=", ">", ">=")

CONJUNCTION = "and"

_TOKENS = re.compile(
    r"""
    (?P<space>\s+)
    | (?P<integer>[0-9]+)
    | (?P<name>[A-Za-z_][A-Za-z0-9_]*)
    | (?P<power>\*\*)
    | (?P<relation><=|>=|!=|[<>=])
    | (?P<operator>[-+*/^()])
    """,
    re.VERBOSE,
)
_DECIMAL = re.compile(r"[0-9]*\.[0-9]+|[0-9]+\.")


@dataclasses.dataclass(frozen=True)
class Token:
    kind: str
    text: str
    where: int


def scan(text: str) -> list[Token]:
    """The tokens of ``text``, refusing the first character outside the alphabet.

    The alphabet is small on purpose. An expression reaching for the host stops
    here, at the full stop, the bracket, the quotation mark or the semicolon it
    needs, and there is no later line of defence it has to get past.
    """
    tokens: list[Token] = []
    position = 0
    while position < len(text):
        match = _TOKENS.match(text, position)
        if match is None:
            _refuse_character(text, position)
        kind = match.lastgroup
        assert kind is not None
        if kind == "power":
            refusal.refuse(
                refusal.POWER_IS_CARET,
                "the power operator is written '^' here, not '**'",
                position,
            )
        if kind == "integer":
            _refuse_a_decimal_point_after(text, match.end())
        if kind != "space":
            tokens.append(Token(kind, match.group(), position))
        position = match.end()
    return tokens


def _refuse_character(text: str, position: int) -> None:
    character = text[position]
    if not character.isascii():
        refusal.refuse(
            refusal.NON_ASCII_CHARACTER,
            f"{character!r} is outside ASCII, and a name a reader cannot "
            "tell from another name is not a name",
            position,
        )
    if _DECIMAL.match(text, position):
        refusal.refuse(
            refusal.DECIMAL_LITERAL,
            "a decimal point: write the exact quotient, 1/2 rather than 0.5",
            position,
        )
    refusal.refuse(
        refusal.UNKNOWN_CHARACTER,
        f"{character!r} is not a character of this language",
        position,
    )


def _refuse_a_decimal_point_after(text: str, end: int) -> None:
    if text[end : end + 1] == ".":
        refusal.refuse(
            refusal.DECIMAL_LITERAL,
            "a decimal point: write the exact quotient, 1/2 rather than 0.5",
            end,
        )


class _Parser:
    """Recursive descent over the grammar in ``docs/expression-language.md``.

    One method per production, so a reader with the document open can put the
    two side by side. The methods are private because the entry point is
    :func:`parse`: a caller holding a half-consumed parser is a caller who can
    accept an expression with something left over.
    """

    def __init__(self, tokens: list[Token], text: str) -> None:
        self.tokens = tokens
        self.text = text
        self.at = 0

    def look(self) -> Token | None:
        return self.tokens[self.at] if self.at < len(self.tokens) else None

    def take(self) -> Token:
        token = self.tokens[self.at]
        self.at += 1
        return token

    def expression(self) -> Node:
        node = self.term()
        while (token := self.look()) is not None and token.text in "+-":
            self.take()
            node = Operation(token.text, node, self.term())
        return node

    def term(self) -> Node:
        node = self.signed()
        while (token := self.look()) is not None and token.text in "*/":
            self.take()
            node = Operation(token.text, node, self.signed())
        return node

    def signed(self) -> Node:
        token = self.look()
        if token is not None and token.text in "+-":
            self.take()
            operand = self.factor()
            return Negate(operand) if token.text == "-" else operand
        return self.factor()

    def factor(self) -> Node:
        node = self.atom()
        token = self.look()
        if token is not None and token.text == "^":
            self.take()
            return Power(node, self.exponent())
        return node

    def exponent(self) -> int:
        """An integer, optionally signed, optionally in brackets. Nothing else.

        The refusal here is the one that keeps an expression inside the rational
        function field of record 0009, so it names what it refused rather than
        reporting an unexpected token.
        """
        token = self.look()
        if token is None:
            refusal.refuse(
                refusal.NON_INTEGER_EXPONENT,
                "'^' with nothing after it",
                len(self.text),
            )
        if token.text == "(":
            self.take()
            value = self.exponent()
            closing = self.look()
            if closing is None or closing.text != ")":
                refusal.refuse(
                    refusal.NON_INTEGER_EXPONENT,
                    "an exponent is an integer literal, and this bracket holds "
                    "more than one",
                    token.where,
                )
            self.take()
            return value
        sign = 1
        if token.text in "+-":
            self.take()
            sign = -1 if token.text == "-" else 1
            token = self.look()
        if token is None or token.kind != "integer":
            where = len(self.text) if token is None else token.where
            refusal.refuse(
                refusal.NON_INTEGER_EXPONENT,
                "an exponent is an integer literal: write exp(p*log(t)) "
                "where the exponent is not one",
                where,
            )
        self.take()
        return sign * int(token.text)

    def atom(self) -> Node:
        token = self.look()
        if token is None:
            refusal.refuse(
                refusal.UNEXPECTED_TOKEN,
                "the expression stops where a number, a name or '(' was due",
                len(self.text),
            )
        if token.kind == "integer":
            self.take()
            return Number(Fraction(int(token.text)))
        if token.kind == "name":
            return self.name_or_call()
        if token.text == "(":
            self.take()
            node = self.expression()
            self.close(token)
            return node
        self.take()
        return self.unexpected(token)

    def unexpected(self, token: Token) -> NoReturn:
        refusal.refuse(
            refusal.UNEXPECTED_TOKEN,
            f"{token.text!r} where a number, a name or '(' was due",
            token.where,
        )

    def name_or_call(self) -> Node:
        token = self.take()
        following = self.look()
        if following is None or following.text != "(":
            if token.text in FUNCTIONS:
                refusal.refuse(
                    refusal.FUNCTION_NAME_WITHOUT_ARGUMENT,
                    f"{token.text!r} is a function of this language and needs "
                    "an argument",
                    token.where,
                )
            return Name(token.text)
        if token.text not in FUNCTIONS:
            refusal.refuse(
                refusal.UNKNOWN_FUNCTION,
                f"{token.text!r} is not one of {', '.join(FUNCTIONS)}",
                token.where,
            )
        self.take()
        if (empty := self.look()) is not None and empty.text == ")":
            refusal.refuse(
                refusal.FUNCTION_TAKES_ONE_ARGUMENT,
                f"{token.text!r} takes one argument and was given none",
                empty.where,
            )
        argument = self.expression()
        self.close(following)
        return Apply(token.text, argument)

    def close(self, opened: Token) -> None:
        token = self.look()
        if token is None:
            refusal.refuse(
                refusal.UNCLOSED_PARENTHESIS,
                "a '(' that never closes",
                opened.where,
            )
        if token.text != ")":
            refusal.refuse(
                refusal.UNCLOSED_PARENTHESIS,
                f"{token.text!r} where the ')' closing this '(' was due",
                opened.where,
            )
        self.take()

    def comparison(self) -> Comparison:
        left = self.expression()
        token = self.look()
        if token is None or token.kind != "relation":
            where = len(self.text) if token is None else token.where
            refusal.refuse(
                refusal.COMPARISON_EXPECTED,
                "a condition compares two expressions with one of "
                f"{' '.join(COMPARISONS)}",
                where,
            )
        self.take()
        right = self.expression()
        if (chained := self.look()) is not None and chained.kind == "relation":
            refusal.refuse(
                refusal.CHAINED_COMPARISON,
                "two relations in one condition: write '0 < theta' and "
                "'theta < pi' as two of them",
                chained.where,
            )
        return Comparison(token.text, left, right)

    def condition(self) -> Condition:
        parts = [self.comparison()]
        while (token := self.look()) is not None and token.text == CONJUNCTION:
            self.take()
            parts.append(self.comparison())
        return parts[0] if len(parts) == 1 else Conjunction(tuple(parts))


def parse(text: str) -> Node:
    """The syntax tree of ``text``, or a :class:`raumbuch.refusal.Refused`.

    Whether the names in the tree are declared is not decided here. Ask
    :func:`names` and answer it against the record, which is issue #36.
    """
    parser = _start(text)
    node = parser.expression()
    _nothing_left(parser)
    return node


def parse_condition(text: str) -> Condition:
    """The tree of a coordinate range, a parameter range or a stratum condition.

    The same expressions, with a relation between two of them, because a range
    that carries no relation restricts nothing. Which record field is a
    condition and which is an expression is in the document.
    """
    parser = _start(text)
    node = parser.condition()
    _nothing_left(parser)
    return node


def _start(text: str) -> _Parser:
    if not text.strip():
        refusal.refuse(
            refusal.EMPTY_EXPRESSION,
            "a field of the sub-language with nothing in it",
        )
    return _Parser(scan(text), text)


def _nothing_left(parser: _Parser) -> None:
    left = parser.look()
    if left is None:
        return
    if left.kind == "relation":
        refusal.refuse(
            refusal.COMPARISON_IN_AN_EXPRESSION,
            f"{left.text!r} in a field that holds a value rather than a condition",
            left.where,
        )
    refusal.refuse(
        refusal.TRAILING_INPUT,
        f"{left.text!r} after a complete expression",
        left.where,
    )


def names(node: Node | Condition) -> frozenset[str]:
    """Every identifier the expression used, constants included.

    The loader subtracts the coordinates the chart declares, the parameters the
    record declares and :data:`CONSTANTS`, and refuses whatever is left.
    """
    if isinstance(node, Name):
        return frozenset({node.text})
    return frozenset().union(*(names(child) for child in _children(node)))


def functions(node: Node | Condition) -> frozenset[str]:
    """Every function the expression applied."""
    applied = frozenset({node.function}) if isinstance(node, Apply) else frozenset()
    return applied.union(*(functions(child) for child in _children(node)), frozenset())


def _children(node: Node | Condition) -> tuple[Node | Condition, ...]:
    if isinstance(node, Apply):
        return (node.argument,)
    if isinstance(node, Negate):
        return (node.operand,)
    if isinstance(node, Operation | Comparison):
        return (node.left, node.right)
    if isinstance(node, Power):
        return (node.base,)
    if isinstance(node, Conjunction):
        return node.parts
    return ()
