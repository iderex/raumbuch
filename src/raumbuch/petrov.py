"""The Petrov type, as a root multiplicity pattern decided exactly.

Record 0002 writes the quartic whose roots are the principal null directions,

    Psi_4*z^4 + 4*Psi_3*z^3 + 6*Psi_2*z^2 + 4*Psi_1*z + Psi_0

and the Petrov type is the multiplicity pattern of its roots. Record 0009 says
how the pattern is reached: through the greatest common divisor of the quartic
and its derivative, without isolating or representing a single root, so no
algebraic extension is entered and no branch of a radical is chosen.

**The failure mode this is designed against is a nearly repeated root.** In
floating point, a type D and a type I differ by rounding. Here they differ by
whether an expression is zero, and the expression is in the coordinates and the
parameters, so the honest answer for a family is often not one type. What comes
back is therefore a case split rather than a type: the type where the
expressions the decision rested on do not vanish, and one further case per
expression, for the locus where it does.

**The root at infinity is a root.** A quartic whose leading coefficient vanishes
has fewer than four finite roots, and the missing ones are at infinity with the
multiplicity the degree dropped by. Reading the degree off the length of a
coefficient tuple rather than off a zero test is how a type D is reported as a
type I for every entry whose frame happens to align.

Every refusal goes through :func:`raumbuch.refusal.refuse`.
"""

from __future__ import annotations

import dataclasses

from raumbuch import algebra, refusal
from raumbuch.algebra import polynomial

#: The six types, and the multiplicity pattern each one is. The pattern is
#: written in descending order and always sums to four, because a quartic has
#: four roots on the sphere the principal null directions live on and the one at
#: infinity is counted with the rest.
PATTERNS: dict[tuple[int, ...], str] = {
    (1, 1, 1, 1): "I",
    (2, 1, 1): "II",
    (2, 2): "D",
    (3, 1): "III",
    (4,): "N",
}

#: The conformally flat case, where the quartic is identically zero and there is
#: no multiplicity pattern to read.
CONFORMALLY_FLAT = "O"

#: How the quartic of record 0002 weights the scalars, lowest power of ``z``
#: first. Written once, here, because a binomial coefficient dropped from one of
#: the middle terms produces a quartic with the right roots for the fixtures
#: that have a symmetric scalar set and the wrong ones for everything else.
WEIGHTS: tuple[int, ...] = (1, 4, 6, 4, 1)


@dataclasses.dataclass(frozen=True)
class Condition:
    """One expression, and whether the case holds where it vanishes."""

    expression: algebra.Value
    vanishes: bool

    def __str__(self) -> str:
        relation = "= 0" if self.vanishes else "!= 0"
        return f"{algebra.text(algebra.normal_form(self.expression))} {relation}"


@dataclasses.dataclass(frozen=True)
class Case:
    """A type, and where it holds."""

    type: str
    conditions: tuple[Condition, ...]

    @property
    def generic(self) -> bool:
        """Whether this is the case that holds where nothing degenerates."""
        return all(not condition.vanishes for condition in self.conditions)


@dataclasses.dataclass(frozen=True)
class Classification:
    """Every case the quartic falls into, the generic one first.

    A caller wanting one answer asks for :attr:`generic_type` and is then
    reading the type of one stratum rather than of the record. Record 0005
    attaches a value to a stratum for this reason, and a classifier that
    returned a single type for a family would be answering a question nobody
    asked of it.
    """

    cases: tuple[Case, ...]

    @property
    def generic_type(self) -> str:
        for case in self.cases:
            if case.generic:
                return case.type
        raise AssertionError("a classification always holds somewhere")

    @property
    def types(self) -> tuple[str, ...]:
        return tuple(case.type for case in self.cases)


def classify(scalars: tuple[algebra.Value, ...]) -> Classification:
    """The Petrov type of a scalar set, as a case split.

    ``scalars`` is ``Psi_0`` to ``Psi_4`` in that order, which is the order
    record 0002 writes them in. What produces them is issue #45; what this does
    with them is decide a multiplicity pattern and nothing else.
    """
    if len(scalars) != len(WEIGHTS):
        raise AssertionError(f"the quartic has five scalars, not {len(scalars)}")
    quartic = tuple(
        algebra.multiply(algebra.integer(weight), scalar)
        for weight, scalar in zip(WEIGHTS, scalars, strict=True)
    )
    return Classification(tuple(_cases(quartic, ())))


def _cases(
    quartic: tuple[algebra.Value, ...], conditions: tuple[Condition, ...]
) -> list[Case]:
    """The cases the quartic falls into, this branch first.

    The recursion is over the leading coefficient. Where a zero test says a
    coefficient is not identically zero and the coefficient is not a number, the
    locus where it does vanish is a case of its own, and it is reached by
    running again with that coefficient replaced by zero. That substitution is
    exact: a quartic with its top coefficient zero is a cubic, and its remaining
    coefficients are the expressions they were.

    **What a case's conditions say, and what they do not.** They are the zero
    tests taken on the way to it. They do not say the conditions can hold at
    once, and they do not carry what one of them implies about the expressions
    in the next: deciding that is arithmetic modulo the ideal they generate,
    which record 0009 does not reach and this does not pretend to.
    """
    reduced = polynomial.degree(quartic)
    _decided(reduced, "the degree of the quartic")
    here = (*conditions, *(Condition(one, False) for one in reduced.assumed))
    if not reduced.coefficients:
        return [Case(CONFORMALLY_FLAT, here)]
    pattern, assumed = _pattern(reduced.coefficients)
    cases = [
        Case(
            PATTERNS[pattern],
            _distinct((*here, *(Condition(one, False) for one in assumed))),
        )
    ]
    for one in reduced.assumed:
        cases.extend(
            _cases(
                polynomial.without_leading(reduced.coefficients),
                (*conditions, Condition(one, True)),
            )
        )
    return cases


def _pattern(
    quartic: tuple[algebra.Value, ...],
) -> tuple[tuple[int, ...], tuple[algebra.Value, ...]]:
    """The multiplicity pattern, infinity included, and what it assumed.

    The finite roots come from the sequence of greatest common divisors: with
    ``P`` a product of ``(z - a_i)^m_i``, the gcd of ``P`` and its derivative is
    the same product with every exponent one lower, so the degrees along that
    sequence count how many roots have a multiplicity above each bound.

    **The assumptions here are named and not branched on.** A remainder in the
    sequence has a leading coefficient of its own, and where that expression
    vanishes the sequence takes a different shape. Unlike the leading
    coefficient of the quartic, that locus cannot be reached by substituting a
    zero: the expression is derived from the coefficients rather than being one
    of them, so the branch is arithmetic modulo the ideal it generates. The
    condition is carried on the case, so a reader sees what the answer rests on,
    and the type on that locus is not claimed.
    """
    assumed: list[algebra.Value] = []
    degrees = [len(quartic) - 1]
    current = quartic
    while degrees[-1] > 0:
        step = polynomial.gcd(current, polynomial.derivative(current))
        _decided(step, "the multiplicity of a root")
        assumed.extend(one for one in step.assumed if not algebra.is_constant(one))
        current = step.coefficients
        degrees.append(max(len(current) - 1, 0))
    multiplicities: list[int] = []
    for bound in range(len(degrees) - 1):
        above = degrees[bound] - degrees[bound + 1]
        further = (
            degrees[bound + 1] - degrees[bound + 2] if bound + 2 < len(degrees) else 0
        )
        multiplicities.extend([bound + 1] * (above - further))
    at_infinity = len(WEIGHTS) - 1 - (len(quartic) - 1)
    if at_infinity:
        multiplicities.append(at_infinity)
    return tuple(sorted(multiplicities, reverse=True)), tuple(assumed)


def _distinct(conditions: tuple[Condition, ...]) -> tuple[Condition, ...]:
    """The conditions with the repeats dropped, in the order they were taken.

    A remainder sequence tests the leading coefficient of the same polynomial
    more than once, and it tests the derivative's leading coefficient beside it,
    which is that coefficient times a whole number. Both say the same thing
    about where the case holds, and a case listing one condition four times is a
    case a reader stops reading.
    """
    seen: set[str] = set()
    kept: list[Condition] = []
    for condition in conditions:
        written = str(condition)
        if written in seen:
            continue
        seen.add(written)
        kept.append(condition)
    return tuple(kept)


def _decided(reduced: polynomial.Reduction, what: str) -> None:
    """Refuse where a zero test did not decide, naming the expression.

    Record 0009 gives the zero test three answers and says the software can tell
    a decision from a hope. This is where the third answer arrives: a branch
    taken on an undecided test would be a Petrov type reported with the same
    confidence as one that was decided.
    """
    if reduced.undecided is None:
        return
    refusal.refuse(
        refusal.ZERO_TEST_UNDECIDED,
        f"{what} needs to know whether this vanishes, and the zero test of "
        "record 0009 did not decide it: "
        + algebra.text(algebra.normal_form(reduced.undecided)),
    )
