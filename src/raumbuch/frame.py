"""The frame freedom the algorithm spends, and what is left of it at each order.

The Cartan-Karlhede algorithm works by using up frame freedom. At each order it
fixes as much of the frame as the curvature at that order allows, and what
remains is the isotropy group at that order. This module holds the
transformations, their composition, their action on the frame components, and
what is left as a **subgroup** rather than as a number.

**Why a subgroup and not a dimension.** Reducing the remaining freedom to a
dimension too early loses what the termination test in issue #54 reads: two
orders can leave freedom of the same dimension and different shape, and a
comparison that sees only the dimension calls those the same and stops early. So
:class:`Freedom` names which generators are still free and reports its dimension
as a consequence.

**How an element is held.** As a two by two matrix of unit determinant acting on
the spinor dyad, not as the six real parameters of the three stages record 0002
names. The reason is composition: in the staged parametrisation the product of
two elements has to be decomposed back into stages before it can be written
down, and that decomposition is where a group law stops holding exactly. As
matrices, composition is multiplication, the inverse is the adjugate, and both
are exact in the field record 0009 fixes. The three stages are the generators
below, so nothing of record 0002's decomposition is lost: an element is built
from them and the parameters are what a caller passes.

The matrix and its negative act identically on a tetrad, which is the standard
two to one cover and is not a defect here. :func:`same` compares the action
rather than the matrix, and that is what every group law below is checked with.

Every refusal goes through :func:`raumbuch.refusal.refuse`.
"""

from __future__ import annotations

import dataclasses

from raumbuch import algebra, conventions, curvature, refusal

#: The six real directions of freedom, in the three stages record 0002 names: a
#: null rotation about ``l`` with one complex parameter, a null rotation about
#: ``n`` with one complex parameter, and a boost in the ``l``, ``n`` plane with
#: a spin in the ``m`` plane. Two plus two plus two is the six, and a generator
#: here is one real direction rather than one complex parameter, because the
#: dimension of an isotropy group is counted over the reals.
GENERATORS: tuple[str, ...] = (
    "null-rotation-about-l-real",
    "null-rotation-about-l-imaginary",
    "null-rotation-about-n-real",
    "null-rotation-about-n-imaginary",
    "boost",
    "spin",
)

#: The dimension of the whole group, which is what a frame carries before any
#: curvature has been looked at.
DIMENSION = len(GENERATORS)


@dataclasses.dataclass(frozen=True)
class Element:
    """One Lorentz transformation, as a dyad matrix, by rows.

    The rows are ``(first, second)`` and ``(third, fourth)``.

    The determinant is one. Nothing here constructs an element whose determinant
    is not one, and :func:`element` refuses one that is handed in.
    """

    first: algebra.Value
    second: algebra.Value
    third: algebra.Value
    fourth: algebra.Value

    @property
    def entries(self) -> tuple[algebra.Value, ...]:
        return (self.first, self.second, self.third, self.fourth)


@dataclasses.dataclass(frozen=True)
class Freedom:
    """What is left of the frame freedom: which generators, and how many.

    The set is the answer and the dimension is read off it. A caller that wants
    the number asks for :attr:`dimension`; a caller that wants to know whether
    two orders left the same freedom compares the sets, which is the comparison
    the termination test needs and the one a dimension cannot make.
    """

    generators: frozenset[str]

    def __post_init__(self) -> None:
        outside = self.generators - set(GENERATORS)
        if outside:
            raise AssertionError(
                f"not directions of the frame group: {sorted(outside)}"
            )

    @property
    def dimension(self) -> int:
        return len(self.generators)

    def holds(self, generator: str) -> bool:
        return generator in self.generators

    def __str__(self) -> str:
        return ", ".join(sorted(self.generators)) or "nothing"


#: The whole group, before any curvature has been read.
EVERYTHING = Freedom(frozenset(GENERATORS))

#: What a type D geometry leaves at order zero: the boost and the spin, which is
#: the two-dimensional isotropy of a frame aligned with two repeated principal
#: null directions. It is here as a name rather than as the number two, which is
#: the whole argument of this module.
BOOST_AND_SPIN = Freedom(frozenset({"boost", "spin"}))


def element(
    first: algebra.Value,
    second: algebra.Value,
    third: algebra.Value,
    fourth: algebra.Value,
) -> Element:
    """An element, once its determinant is one. Refused where it is not."""
    determinant = algebra.subtract(
        algebra.multiply(first, fourth), algebra.multiply(second, third)
    )
    difference = algebra.subtract(determinant, algebra.integer(1))
    if not algebra.is_zero(difference):
        refusal.refuse(
            refusal.FRAME_ELEMENT_IS_NOT_UNIMODULAR,
            "a frame transformation has determinant one and this one has "
            + algebra.text(algebra.normal_form(determinant)),
        )
    return Element(first, second, third, fourth)


def identity() -> Element:
    return Element(
        algebra.integer(1), algebra.integer(0), algebra.integer(0), algebra.integer(1)
    )


def null_rotation_about_l(parameter: algebra.Value) -> Element:
    """The first stage of record 0002, with one complex parameter.

    It fixes ``l`` and moves ``m`` along it. In the dyad this is the lower
    triangular matrix, and its determinant is one for every parameter, so no
    zero test stands between a caller and an element.
    """
    return Element(
        algebra.integer(1), algebra.integer(0), parameter, algebra.integer(1)
    )


def null_rotation_about_n(parameter: algebra.Value) -> Element:
    """The second stage: fixes ``n`` and moves ``m`` along it."""
    return Element(
        algebra.integer(1), parameter, algebra.integer(0), algebra.integer(1)
    )


def boost_and_spin(parameter: algebra.Value) -> Element:
    """The third stage: a boost in the ``l``, ``n`` plane and a spin in ``m``.

    One non-zero complex parameter carries both. The dyad scales by it, so ``l``
    scales by its squared modulus, ``n`` by the inverse of that, and ``m`` turns
    by its phase. Writing it this way is what keeps the stage exact: the boost
    and the spin written separately need a positive real scale and a number of
    unit modulus, and neither is in the field record 0009 fixes unless it is
    built as a modulus and a phase of one element of it.
    """
    if algebra.verdict(parameter) != algebra.NONZERO:
        refusal.refuse(
            refusal.FRAME_ELEMENT_IS_NOT_UNIMODULAR,
            "a boost and spin scales the dyad by a parameter that has to be "
            "non-zero, and this one is " + algebra.text(algebra.normal_form(parameter)),
        )
    return Element(
        parameter,
        algebra.integer(0),
        algebra.integer(0),
        algebra.divide(algebra.integer(1), parameter),
    )


def compose(left: Element, right: Element) -> Element:
    """``left`` after ``right``, which is the matrix product in that order."""
    return Element(
        algebra.normal_form(
            algebra.add(
                algebra.multiply(left.first, right.first),
                algebra.multiply(left.second, right.third),
            )
        ),
        algebra.normal_form(
            algebra.add(
                algebra.multiply(left.first, right.second),
                algebra.multiply(left.second, right.fourth),
            )
        ),
        algebra.normal_form(
            algebra.add(
                algebra.multiply(left.third, right.first),
                algebra.multiply(left.fourth, right.third),
            )
        ),
        algebra.normal_form(
            algebra.add(
                algebra.multiply(left.third, right.second),
                algebra.multiply(left.fourth, right.fourth),
            )
        ),
    )


def inverse(subject: Element) -> Element:
    """The inverse, which for determinant one is the adjugate and needs no division."""
    return Element(
        subject.fourth,
        algebra.negate(subject.second),
        algebra.negate(subject.third),
        subject.first,
    )


def act_on_tetrad(subject: Element, frame: curvature.Tetrad) -> curvature.Tetrad:
    """The tetrad the element takes this one to.

    The legs are quadratic in the dyad, so each transformed leg is a combination
    of all four with coefficients built from the matrix and its conjugate. What
    comes back is a tetrad in the same coordinate basis, and it satisfies the
    conditions of record 0002 because the determinant is one; that is a claim
    the suite checks rather than one this docstring settles.
    """
    combination = _combination(subject)
    legs = []
    for name in ("l", "n", "m"):
        legs.append(
            tuple(
                algebra.normal_form(
                    _total(
                        algebra.multiply(
                            combination[(name, other)], frame.leg(other)[index]
                        )
                        for other in conventions.LEGS
                    )
                )
                for index in range(len(frame.leg("l")))
            )
        )
    return curvature.Tetrad(tuple(legs))


def act_on_components(
    subject: Element, components: dict[tuple[str, ...], algebra.Value]
) -> dict[tuple[str, ...], algebra.Value]:
    """The frame components of the same tensor, read in the transformed frame.

    A component with four frame indices transforms once per index, so this is
    the same combination as :func:`act_on_tetrad` applied four times. Doing it
    here rather than by recomputing the curvature is the point of the module:
    the algorithm moves the frame many times per order and the curvature is what
    it costs to compute once.
    """
    combination = _combination(subject)
    depth = len(next(iter(components)))
    current = components
    for slot in range(depth):
        stage: dict[tuple[str, ...], algebra.Value] = {}
        for names in current:
            total = algebra.integer(0)
            for leg in conventions.LEGS:
                others = (*names[:slot], leg, *names[slot + 1 :])
                total = algebra.add(
                    total,
                    algebra.multiply(combination[(names[slot], leg)], current[others]),
                )
            stage[names] = algebra.normal_form(total)
        current = stage
    return current


def same(left: Element, right: Element) -> bool:
    """Whether two elements act identically, which is up to an overall sign.

    The dyad matrix covers the transformation two to one: an element and its
    negative scale every leg by the same squared modulus and turn ``m`` by the
    same phase. Comparing the matrices would call those two elements different
    and every group law below would fail on half its inputs for a reason that is
    not about the group.
    """
    return _entries_agree(left, right) or _entries_agree(left, _negated(right))


def preferred(candidates: tuple[Element, ...]) -> Element:
    """One element out of several, chosen the same way on every run.

    Record 0012 fixes that nothing about how the work was scheduled may reach
    the output, and a canonical frame fixing reaches several equally canonical
    frames often: a type D geometry leaves a boost and a spin free at every
    order, so every choice among them is a tie. The tie-break is a total order
    on the written normal form of the entries, which is a property of the values
    and not of the order the candidates arrived in.
    """
    if not candidates:
        raise AssertionError("there is no preferred element among none")
    return min(candidates, key=_written)


def written(subject: Element) -> tuple[str, ...]:
    """The element as text, which is what the tie-break orders on."""
    return _written(subject)


def _written(subject: Element) -> tuple[str, ...]:
    return tuple(algebra.text(algebra.normal_form(entry)) for entry in subject.entries)


def _entries_agree(left: Element, right: Element) -> bool:
    return all(
        algebra.is_zero(algebra.subtract(one, other))
        for one, other in zip(left.entries, right.entries, strict=True)
    )


def _negated(subject: Element) -> Element:
    return Element(*(algebra.negate(entry) for entry in subject.entries))


def _combination(subject: Element) -> dict[tuple[str, str], algebra.Value]:
    """How each leg of the new frame is written in the legs of the old one.

    The dyad goes to ``(alpha*o + beta*i, gamma*o + delta*i)``, by rows of the
    matrix rather than by columns, and each leg is a product of one dyad element
    with the conjugate of another, so the table below is that product expanded.
    It is written out rather than looped because every entry is a different pair
    and a loop over them would need the same four lines to say which.

    **Rows and not columns, and the difference is the composition law.** With
    the columns, acting with one element and then another is the product of the
    two matrices in the other order, so ``compose`` would have to reverse its
    arguments to keep meaning what it says. The suite says which convention is
    in force here: it composes two elements, acts once, acts twice, and compares.
    """
    alpha, beta, gamma, delta = subject.entries
    conjugates = {
        name: algebra.conjugate(value)
        for name, value in (
            ("alpha", alpha),
            ("beta", beta),
            ("gamma", gamma),
            ("delta", delta),
        )
    }
    return {
        ("l", "l"): algebra.multiply(alpha, conjugates["alpha"]),
        ("l", "n"): algebra.multiply(beta, conjugates["beta"]),
        ("l", "m"): algebra.multiply(alpha, conjugates["beta"]),
        ("l", "mbar"): algebra.multiply(beta, conjugates["alpha"]),
        ("n", "l"): algebra.multiply(gamma, conjugates["gamma"]),
        ("n", "n"): algebra.multiply(delta, conjugates["delta"]),
        ("n", "m"): algebra.multiply(gamma, conjugates["delta"]),
        ("n", "mbar"): algebra.multiply(delta, conjugates["gamma"]),
        ("m", "l"): algebra.multiply(alpha, conjugates["gamma"]),
        ("m", "n"): algebra.multiply(beta, conjugates["delta"]),
        ("m", "m"): algebra.multiply(alpha, conjugates["delta"]),
        ("m", "mbar"): algebra.multiply(beta, conjugates["gamma"]),
        ("mbar", "l"): algebra.multiply(gamma, conjugates["alpha"]),
        ("mbar", "n"): algebra.multiply(delta, conjugates["beta"]),
        ("mbar", "m"): algebra.multiply(gamma, conjugates["beta"]),
        ("mbar", "mbar"): algebra.multiply(delta, conjugates["alpha"]),
    }


def _total(values) -> algebra.Value:
    running = algebra.integer(0)
    for value in values:
        running = algebra.add(running, value)
    return running
