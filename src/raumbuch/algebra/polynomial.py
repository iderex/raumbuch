"""Polynomials over the field of record 0009, and the gcd the Petrov type reads.

Record 0001 puts the greatest common divisor of two polynomials on the
arithmetic interface, and record 0009 says what it is for: the root multiplicity
pattern of a quartic is obtainable from the coefficients alone, through that gcd,
without isolating or representing a single root.

A polynomial here is a tuple of :class:`raumbuch.algebra.Value` coefficients,
lowest power first. It is not a symbolic object with a variable in it: the
variable would have to be a name, and a name can collide with a coordinate a
chart declares, which is a defect that appears only for the record whose chart
uses that letter.

**Every zero test this module takes is reported rather than assumed.** The
coefficients live in a field, so the Euclidean algorithm needs no pseudo-division
and the only thing it has to decide is which leading coefficient is zero. Each
such decision is a branch: an expression that is not identically zero still
vanishes somewhere, and a classifier that took the generic branch in silence
would answer for one region of a manifold and say nothing about the rest. So a
:class:`Reduction` carries what was assumed non-zero and what a zero test did not
decide, and the caller is where a branch becomes a case or a refusal.

The subresultants record 0001 also names are not implemented. They are the way
to reach the same multiplicity pattern without dividing by a leading coefficient
at all, which matters where the coefficient domain is not a field. Here it is
one, per record 0009, and the polynomial is a quartic, so the remainder sequence
is three steps long and the coefficient growth the subresultant chain exists to
control does not arise.
"""

from __future__ import annotations

import dataclasses

from raumbuch import algebra

#: A polynomial with every coefficient zero. Its degree is not defined and the
#: functions below say so by returning ``None`` for it rather than a number
#: nobody can act on.
EMPTY: tuple[algebra.Value, ...] = ()


@dataclasses.dataclass(frozen=True)
class Reduction:
    """What a division or a gcd produced, and what it had to decide to get there.

    ``assumed`` holds the expressions a zero test answered ``nonzero`` for, in
    the order they were tested. Each of them is a branch the caller may take:
    the result below holds where they are all non-zero, and where one of them
    vanishes the caller runs again with that coefficient replaced by zero.

    ``undecided`` holds the expression a zero test did not decide, where one
    did not. The result is then meaningless and the caller refuses.
    """

    coefficients: tuple[algebra.Value, ...]
    assumed: tuple[algebra.Value, ...] = ()
    undecided: algebra.Value | None = None


def degree(coefficients: tuple[algebra.Value, ...]) -> Reduction:
    """The polynomial cut down to its true degree, top coefficient first tested.

    The length of ``coefficients`` is what somebody wrote down; the degree is
    what the arithmetic says. The two differ exactly when a leading coefficient
    is zero, which for a Weyl scalar is the ordinary case rather than the
    exceptional one.
    """
    assumed: list[algebra.Value] = []
    remaining = list(coefficients)
    while remaining:
        verdict = algebra.verdict(remaining[-1])
        if verdict == algebra.UNDETERMINED:
            return Reduction((), tuple(assumed), remaining[-1])
        if verdict == algebra.NONZERO:
            if not algebra.is_constant(remaining[-1]):
                assumed.append(remaining[-1])
            return Reduction(tuple(remaining), tuple(assumed))
        remaining.pop()
    return Reduction(EMPTY, tuple(assumed))


def derivative(coefficients: tuple[algebra.Value, ...]) -> tuple[algebra.Value, ...]:
    """The formal derivative, which needs no zero test and takes no branch."""
    return tuple(
        algebra.multiply(algebra.integer(power), coefficient)
        for power, coefficient in enumerate(coefficients)
        if power
    )


def gcd(left: tuple[algebra.Value, ...], right: tuple[algebra.Value, ...]) -> Reduction:
    """The monic greatest common divisor, by the Euclidean algorithm.

    Monic because the coefficients are a field and the gcd is defined up to one
    of its elements, so a normalised answer is the one two runs agree on, which
    is what record 0012 asks of anything the classification reads.
    """
    assumed: list[algebra.Value] = []
    first, second = left, right
    while True:
        reduced = degree(second)
        assumed.extend(reduced.assumed)
        if reduced.undecided is not None:
            return Reduction((), tuple(assumed), reduced.undecided)
        second = reduced.coefficients
        if not second:
            break
        step = _remainder(first, second)
        assumed.extend(step.assumed)
        if step.undecided is not None:
            return Reduction((), tuple(assumed), step.undecided)
        first, second = second, step.coefficients
    top = degree(first)
    assumed.extend(top.assumed)
    if top.undecided is not None:
        return Reduction((), tuple(assumed), top.undecided)
    return Reduction(_monic(top.coefficients), tuple(assumed))


def without_leading(
    coefficients: tuple[algebra.Value, ...],
) -> tuple[algebra.Value, ...]:
    """The same polynomial with its top coefficient replaced by zero.

    This is what a caller runs again with when it takes the branch where the
    coefficient it assumed non-zero vanishes. Only that one coefficient moves:
    the others are the expressions they were, and whether they are constrained
    on that locus as well is not something this module decides.
    """
    if not coefficients:
        return EMPTY
    return (*coefficients[:-1], algebra.integer(0))


def _remainder(
    left: tuple[algebra.Value, ...], right: tuple[algebra.Value, ...]
) -> Reduction:
    """``left`` modulo ``right``, in a field, so with exact division."""
    assumed: list[algebra.Value] = []
    running = list(left)
    divisor = list(right)
    while True:
        reduced = degree(tuple(running))
        assumed.extend(reduced.assumed)
        if reduced.undecided is not None:
            return Reduction((), tuple(assumed), reduced.undecided)
        running = list(reduced.coefficients)
        if len(running) < len(divisor):
            return Reduction(tuple(running), tuple(assumed))
        factor = algebra.divide(running[-1], divisor[-1])
        shift = len(running) - len(divisor)
        for index, coefficient in enumerate(divisor):
            running[index + shift] = algebra.normal_form(
                algebra.subtract(
                    running[index + shift], algebra.multiply(factor, coefficient)
                )
            )
        running.pop()


def _monic(coefficients: tuple[algebra.Value, ...]) -> tuple[algebra.Value, ...]:
    if not coefficients:
        return EMPTY
    leading = coefficients[-1]
    return tuple(
        algebra.normal_form(algebra.divide(coefficient, leading))
        for coefficient in coefficients
    )
