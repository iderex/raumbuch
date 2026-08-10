"""The arithmetic boundary of record 0001, and the operations it carries.

Record 0001 put everything record 0009 makes load-bearing behind one interface
here, and said that nothing outside this directory constructs a SymPy object or
names a SymPy type. The ``invariants`` leg refuses that name everywhere else
under ``src/``, so what follows is the only door.

The operations record 0001 fixed are: reduce to a normal form, answer a zero
test, evaluate at a rational point modulo a prime, differentiate with respect to
a declared symbol, take a greatest common divisor and the subresultants of two
polynomials, and apply the declared rewrites of the closed function list. Four
of them are here, together with the field operations everything else is built
out of and one more the frame construction of issue #44 asked for, an exact
square root that answers whether the field holds one at all.

**Three are not implemented**: evaluation modulo a prime, the greatest common
divisor and the subresultants. Nothing has needed the first, and the other two
are what the root multiplicity pattern of the Petrov type is read from, which is
issue #46. They are named as absent so that a reader meeting this module does
not have to derive their absence from a list.

Nothing here evaluates a record. A tree from :mod:`raumbuch.expression` is data,
and :func:`from_expression` is where it stops being data and becomes arithmetic.
"""

from __future__ import annotations

from raumbuch import expression
from raumbuch.algebra._sympy import (
    NONZERO,
    UNDETERMINED,
    ZERO,
    Value,
    add,
    applied,
    conjugate,
    differentiate,
    divide,
    free_function,
    from_fraction,
    imaginary_unit,
    integer,
    multiply,
    negate,
    normal_form,
    power,
    rational,
    square_root,
    subtract,
    symbol,
    text,
    verdict,
)

__all__: tuple[str, ...] = (
    "NONZERO",
    "UNDETERMINED",
    "ZERO",
    "Value",
    "add",
    "applied",
    "conjugate",
    "differentiate",
    "divide",
    "free_function",
    "from_expression",
    "from_fraction",
    "imaginary_unit",
    "integer",
    "is_zero",
    "multiply",
    "negate",
    "normal_form",
    "power",
    "rational",
    "square_root",
    "subtract",
    "symbol",
    "text",
    "verdict",
)

#: The operations of the four arithmetic operators, by the spelling the grammar
#: of record 0003 writes them in.
_OPERATIONS = {"+": add, "-": subtract, "*": multiply, "/": divide}

#: The argument the derived spellings of :data:`raumbuch.expression.RELATIONS`
#: are written in. ``tan(u) = sin(u)/cos(u)`` is one string in that record, and
#: reading it here rather than re-writing its right-hand side is what keeps the
#: two from parting.
_ARGUMENT = "u"


def from_expression(node: expression.Node) -> Value:
    """The parsed tree as arithmetic, with the derived spellings rewritten.

    A derived function is not a second domain. ``tan`` is admitted by the
    grammar and is rewritten into ``sin`` over ``cos`` here, by parsing the
    right-hand side :mod:`raumbuch.expression` declares for it, so the closed
    list the normal form is written in is the six of
    :data:`raumbuch.expression.NORMAL_FORM_FUNCTIONS` and no more.
    """
    return _read(node, {})


def is_zero(value: Value) -> bool:
    """Whether the zero test **decided** zero.

    A caller that wants the three answers of record 0009 asks :func:`verdict`.
    This is for the callers that want one of them, and it answers ``False`` for
    :data:`UNDETERMINED` as well as for :data:`NONZERO`, which is the safe
    direction: a value that was not proved zero is not treated as one.
    """
    return verdict(value) == ZERO


def _read(node: expression.Node, bound: dict[str, Value]) -> Value:
    """The tree, with any bound names substituted as their values."""
    match node:
        case expression.Negate():
            return negate(_read(node.operand, bound))
        case expression.Operation():
            return _OPERATIONS[node.operator](
                _read(node.left, bound), _read(node.right, bound)
            )
        case expression.Power():
            return power(_read(node.base, bound), node.exponent)
    return _leaf(node, bound)


def _leaf(node: expression.Node, bound: dict[str, Value]) -> Value:
    """A node with no operator in it: a number, a name, or a call."""
    match node:
        case expression.Number():
            return from_fraction(node.value)
        case expression.Name():
            if node.text in bound:
                return bound[node.text]
            return _symbol_or_constant(node.text)
        case expression.Apply():
            return _apply(node, bound)
    raise AssertionError(f"not a node of the expression language: {node!r}")


def _apply(node: expression.Apply, bound: dict[str, Value]) -> Value:
    argument = _read(node.argument, bound)
    if node.function in expression.DERIVED_FUNCTIONS:
        body = expression.parse(expression.DERIVED_FUNCTIONS[node.function])
        return _read(body, {**bound, _ARGUMENT: argument})
    return applied(node.function, argument)


def _symbol_or_constant(name: str) -> Value:
    """A declared name. Which names are declared is the loader's question.

    The named constants of the closed list are symbols with no declared
    relations, which is what record 0009 says makes the field they generate a
    rational function field, so ``pi`` arrives here as a symbol like any other
    and the cost of that is written in that record.
    """
    return symbol(name)
