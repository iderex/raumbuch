"""The implementation behind the interface, and the one file that names SymPy.

Record 0001 put every operation record 0009 makes load-bearing behind one
interface and said that nothing outside ``src/raumbuch/algebra/`` constructs a
symbolic object or names a symbolic type. The ``invariants`` leg refuses the
name everywhere else under ``src/``, so the boundary is a rule rather than a
habit. This module is the inside of it: :mod:`raumbuch.algebra` declares what
the operations are, and this one is how they are answered today.

What is implemented is what the curvature of issue #44 needs: the field
operations, differentiation with respect to a declared symbol, the declared
rewrites, a normal form, the zero test, and the exact square root a frame
construction asks for. Three operations record 0001 names are **not**
implemented, and they are named here rather than left to be discovered:
evaluation at a rational point modulo a prime, the greatest common divisor, and
the subresultants. The first is a filter nothing has needed yet; the other two
are what the root multiplicity pattern of issue #46 is read from.

Every declared symbol is real. A coordinate, a parameter and a named constant
are real-valued under record 0003, and a free function of them is a real
function, so the symbols are built that way once, here, rather than carrying an
assumption at each call site. Conjugation then acts on ``i`` and on nothing
else, which is what the fourth leg of the tetrad needs of it.
"""

from __future__ import annotations

import dataclasses
from fractions import Fraction

import sympy

#: The three answers of record 0009. A zero test says which of them it reached
#: rather than returning a boolean, because "not proved zero" and "proved not
#: zero" are the two states that record exists to keep apart.
ZERO = "zero"
NONZERO = "nonzero"
UNDETERMINED = "undetermined"

#: The functions the normal form of record 0009 is written in, after the
#: derived spellings have been rewritten into them. The names are the closed
#: list of :mod:`raumbuch.expression`; the mapping is here because what sits on
#: the right of it is a symbolic object.
_FUNCTIONS = {
    "cos": sympy.cos,
    "cosh": sympy.cosh,
    "exp": sympy.exp,
    "log": sympy.log,
    "sin": sympy.sin,
    "sinh": sympy.sinh,
}


@dataclasses.dataclass(frozen=True)
class Value:
    """One element of the field record 0009 fixes, held opaquely.

    What a caller may do with a value is the operations of
    :mod:`raumbuch.algebra` and nothing else, which is what keeps the
    implementation replaceable: a second backend changes this file and the
    operations, and no call site.
    """

    held: sympy.Expr

    def __str__(self) -> str:
        return str(self.held)


def integer(number: int) -> Value:
    """The integer, as an element of the ground field."""
    return Value(sympy.Integer(number))


def rational(numerator: int, denominator: int) -> Value:
    """The rational ``numerator/denominator``, exactly."""
    return Value(sympy.Rational(numerator, denominator))


def from_fraction(number: Fraction) -> Value:
    """The rational a parsed number literal holds."""
    return Value(sympy.Rational(number.numerator, number.denominator))


def imaginary_unit() -> Value:
    """``i``. Record 0009 extends the rationals by it and calls it not optional."""
    return Value(sympy.I)


def symbol(name: str) -> Value:
    """A declared symbol: a coordinate, a parameter, or a named constant."""
    return Value(_symbol(name))


def applied(name: str, argument: Value) -> Value:
    """One function of the closed list, applied to its one argument."""
    if name not in _FUNCTIONS:
        raise AssertionError(f"not a function of the normal form list: {name!r}")
    return Value(_FUNCTIONS[name](argument.held))


def free_function(name: str, arguments: tuple[Value, ...]) -> Value:
    """A free function symbol of the coordinates it is applied to.

    Record 0009 admits these because large parts of the reference literature are
    families carrying one. Its derivatives enter as further independent symbols,
    which is what :func:`differentiate` produces of one and is why the normal
    form below is a normal form rather than a canonical one.
    """
    held = sympy.Function(name, real=True)(*(argument.held for argument in arguments))
    return Value(held)


def add(left: Value, right: Value) -> Value:
    return Value(left.held + right.held)


def subtract(left: Value, right: Value) -> Value:
    return Value(left.held - right.held)


def multiply(left: Value, right: Value) -> Value:
    return Value(left.held * right.held)


def divide(left: Value, right: Value) -> Value:
    return Value(left.held / right.held)


def negate(value: Value) -> Value:
    return Value(-value.held)


def power(base: Value, exponent: int) -> Value:
    """An integer power. The grammar of record 0003 admits no other."""
    return Value(base.held**exponent)


def conjugate(value: Value) -> Value:
    """The Gaussian conjugate, which is what the fourth leg of the tetrad is."""
    return Value(sympy.conjugate(value.held))


def differentiate(value: Value, name: str) -> Value:
    """The derivative with respect to one declared symbol."""
    return Value(sympy.diff(value.held, _symbol(name)))


def rewritten(value: Value) -> Value:
    """The declared rewrites of :data:`raumbuch.expression.RELATIONS`, applied.

    Record 0009 requires that every relation this project relies on among the
    admitted functions is declared as a rewrite to a normal form, and that
    nothing outside the declared set is relied on. Two of them do the work here:
    an even power of ``sin``, positive or negative, becomes a polynomial in
    ``cos``, and the same for ``sinh`` in ``cosh``. That is the Pythagorean
    relation the worked Schwarzschild record needs, applied rather than left for
    the zero test to discover. The exponential rewrites are what SymPy's own
    power collection already does and are not re-implemented.
    """
    held = value.held
    for function, into, sign in (
        (sympy.sin, sympy.cos, -1),
        (sympy.sinh, sympy.cosh, 1),
    ):
        for part in sorted(held.atoms(sympy.Pow), key=sympy.default_sort_key):
            base, exponent = part.as_base_exp()
            if base.func is not function or not exponent.is_Integer:
                continue
            half, rest = divmod(int(exponent), 2)
            if half == 0:
                continue
            squared = sign * (into(*base.args) ** 2 - 1)
            held = held.subs(part, squared**half * base**rest)
    return Value(sympy.powsimp(held, combine="exp"))


def normal_form(value: Value) -> Value:
    """A quotient of two expanded polynomials in the alphabet of record 0009.

    The declared rewrites first, then one cancellation, then the numerator and
    the denominator expanded. What comes back is a normal form and not a
    canonical one, which is what record 0010 chose and what record 0009 sits
    underneath.
    """
    numerator, denominator = sympy.fraction(_reduced(value.held))
    return Value(sympy.expand(numerator) / sympy.expand(denominator))


def verdict(value: Value) -> str:
    """:data:`ZERO`, :data:`NONZERO` or :data:`UNDETERMINED` for the value.

    The numerator of the normal form is zero or it is not. Where the alphabet
    carries a free function symbol the normal form is not canonical, so a
    numerator that did not reduce to zero is not evidence that the value is
    non-zero, and the answer is :data:`UNDETERMINED` rather than
    :data:`NONZERO`.

    **This is narrower than the decision procedure record 0009 describes**, and
    the difference is in one direction only. Zero is decided soundly, which is
    what a curvature component and a comparison against a published one ask of
    it. Where the wider procedure would go on to decide non-zero over the free
    function symbols and their derivatives, this says it did not decide.
    """
    numerator, _ = sympy.fraction(_reduced(value.held))
    reduced = sympy.expand(numerator)
    if reduced.is_zero:
        return ZERO
    if reduced.atoms(sympy.core.function.AppliedUndef, sympy.Derivative):
        return UNDETERMINED
    return NONZERO


def square_root(value: Value) -> Value | None:
    """The square root where the field holds one, and ``None`` where it does not.

    A frame construction needs the square root of a metric component, and record
    0009 says algebraic extensions are entered as late as possible and, for the
    steps this board takes, not at all. So the question asked here is not what
    the square root is but whether the field holds one: the expression is
    factored, and it has a root here exactly when every exponent is even and the
    rational coefficient is a square. ``r^2*sin(theta)^2`` has one and ``r`` has
    none, and a caller meeting ``None`` refuses rather than reaching for an
    extension nobody declared.

    The positive branch is taken, in each factor. The other branch is a
    reflection of the frame, which is frame freedom rather than a different
    geometry, and the canonical frame fixing of issue #51 is where a frame is
    chosen among the ones that satisfy the conditions.

    Both spellings are tried, and that is not a fallback. The declared rewrite
    turns ``sin(u)^2`` into ``1 - cos(u)^2``, which is what the zero test needs
    and is a product of two distinct factors rather than a square, so a metric
    component that is a square as written would have no root after it. The
    question is whether the field holds a root, and a spelling in which it
    visibly does answers it.
    """
    for candidate in (value.held, rewritten(value).held):
        root = _square_root(candidate)
        if root is not None:
            return Value(root)
    return None


def _square_root(held: sympy.Expr) -> sympy.Expr | None:
    """The root of one spelling: every exponent even and the coefficient square."""
    coefficient, factors = sympy.factor_list(sympy.cancel(held))
    root = sympy.sqrt(coefficient)
    if not root.is_Rational:
        return None
    for factor, exponent in factors:
        if int(exponent) % 2:
            return None
        root = root * factor ** (int(exponent) // 2)
    return root


def text(value: Value) -> str:
    """The value as a string, for the detail of a refusal and for nothing else."""
    return str(value.held)


def _reduced(held: sympy.Expr) -> sympy.Expr:
    """One quotient, with the declared rewrites applied to it and cancelled again.

    The cancellation comes first and that ordering is the whole of this
    function. A sum of quotients carries no ``sin(u)^2`` until it is over one
    denominator, so rewriting before cancelling leaves the Pythagorean relation
    unapplied on exactly the expressions that need it: a metric rebuilt from
    four tetrad legs is a sum of quotients, and its components were reported as
    disagreeing with the metric they came from.
    """
    return sympy.cancel(rewritten(Value(sympy.cancel(sympy.together(held)))).held)


def _symbol(name: str) -> sympy.Symbol:
    """One symbol per name, real, so that two spellings of it are one symbol.

    Differentiation looks the symbol up by name, and a symbol carrying different
    assumptions is a different symbol to SymPy, so a coordinate built one way
    and differentiated another would silently differentiate to zero.
    """
    return sympy.Symbol(name, real=True)
