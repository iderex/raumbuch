"""The layer everything else is wrong through: connection, Riemann, and a frame.

From the metric components a chart declares, this produces the Levi-Civita
connection and the Riemann tensor, in the coordinate basis, and a null tetrad
satisfying the normalisation record 0002 fixes. A sign error here produces a
Petrov type that is wrong for every entry in the catalogue and looks entirely
plausible, which is why the module is small, why every convention it depends on
is read from :mod:`raumbuch.conventions`, and why the connection is derived from
its definition rather than transcribed from a published table.

**Where the coordinate index stops.** Record 0002 puts the transition to frame
indices at order zero and gives the tetrad to issue #51. That is not what the
milestone order allows: nothing at order zero can be canonicalised before a
tetrad exists, and issue #44 is a milestone earlier. So the construction is here
and issue #51 canonicalises what it produces, rather than building a second one.
There is one implementation of the tetrad conditions and one refusal for them,
which is what a second construction would have cost.

**What the frame here is not.** :func:`tetrad_from_metric` builds *a* tetrad,
not the canonical one. Any two tetrads over one metric differ by an element of
the six-parameter group of record 0002, and choosing among them is issue #51
working with issue #48's group action. What is promised of this one is that it
satisfies the conditions, that it is exact, and that a run of it twice produces
the same legs.

Every refusal goes through :func:`raumbuch.refusal.refuse`.
"""

from __future__ import annotations

import dataclasses
import itertools

from raumbuch import algebra, conventions, record, refusal

#: The index pairs the tetrad construction splits the coordinates into: the
#: first two carry the Lorentzian block and the last two the transverse one.
#: Which coordinates those are is the chart's order, and a chart writing them
#: in another order is a chart this construction refuses rather than reorders,
#: because reordering silently is how a record and a component tuple stop
#: meaning the same thing.
BOOST_PAIR = (0, 1)
TRANSVERSE_PAIR = (2, 3)

#: Half, as the definition of the connection carries it. Written once so that
#: no decimal point is ever near this arithmetic; record 0009 keeps floating
#: point out of the classification path and the ``invariants`` leg refuses the
#: route to one under ``src/``.
_HALF = algebra.rational(1, 2)

#: The shapes the arrays below carry. An array of curvature is a tuple of
#: tuples and the depth is what tells one from another, so the depth is named.
Rank2 = tuple[tuple[algebra.Value, ...], ...]
Rank3 = tuple[Rank2, ...]
Rank4 = tuple[Rank3, ...]

#: The phase the transverse leg is built with. ``m`` has to satisfy
#: ``m.mbar = 1`` and ``m.m = 0`` over an orthonormal transverse pair, which
#: fixes the modulus of its coefficient at the square root of a half and leaves
#: its phase free. The usual coefficient is that square root, which is not in
#: the field record 0009 fixes; ``(1 + i)/2`` has the same modulus and is. The
#: two differ by a spin, which is frame freedom in the sense record 0002 sets
#: out, so nothing invariant moves and the arithmetic stays exact.
_TRANSVERSE_PHASE = algebra.divide(
    algebra.add(algebra.integer(1), algebra.imaginary_unit()), algebra.integer(2)
)


@dataclasses.dataclass(frozen=True)
class Geometry:
    """A metric in one chart: the coordinate names and the components."""

    coordinates: tuple[str, ...]
    metric: tuple[tuple[algebra.Value, ...], ...]

    def component(self, first: int, second: int) -> algebra.Value:
        return self.metric[first][second]


@dataclasses.dataclass(frozen=True)
class Tetrad:
    """Four legs in the coordinate basis, in the order record 0002 fixes.

    The components are contravariant, which is the direction a leg is written
    in when it is read off a chart. ``mbar`` is not carried: it is the
    conjugate of ``m`` and a second array holding it is a second thing that can
    disagree.
    """

    legs: tuple[tuple[algebra.Value, ...], ...]

    def leg(self, name: str) -> tuple[algebra.Value, ...]:
        if name == "mbar":
            return tuple(algebra.conjugate(part) for part in self.legs[2])
        return self.legs[conventions.LEGS.index(name)]


def geometry(
    coordinates: tuple[str, ...], components: dict[tuple[str, str], algebra.Value]
) -> Geometry:
    """A geometry from the components written at or above the diagonal.

    Record 0003 has a record write only the components with ``i`` at or before
    ``j``, and the loader refuses the other half, so filling the symmetric part
    is this module's job and is done in one place.
    """
    size = len(coordinates)
    metric = [[algebra.integer(0) for _ in range(size)] for _ in range(size)]
    for (first, second), value in components.items():
        row, column = coordinates.index(first), coordinates.index(second)
        metric[row][column] = value
        metric[column][row] = value
    return Geometry(coordinates, tuple(tuple(row) for row in metric))


def from_chart(chart: record.Chart) -> Geometry:
    """The geometry a loaded chart declares, with its expressions as arithmetic."""
    return geometry(
        chart.coordinates,
        {pair: algebra.from_expression(node) for pair, node in chart.metric.items()},
    )


def inverse(subject: Geometry) -> Rank2:
    """``g^ab``, by cofactors, or a refusal where the metric is degenerate."""
    size = len(subject.coordinates)
    rows = [list(row) for row in subject.metric]
    determinant = _determinant(rows)
    if algebra.is_zero(determinant):
        refusal.refuse(
            refusal.METRIC_IS_DEGENERATE,
            "the determinant of the metric is zero, so there is no inverse and "
            "no connection: " + algebra.text(algebra.normal_form(determinant)),
        )
    raised = [[algebra.integer(0)] * size for _ in range(size)]
    for row, column in itertools.product(range(size), repeat=2):
        cofactor = _cofactor(rows, column, row)
        raised[row][column] = algebra.normal_form(algebra.divide(cofactor, determinant))
    return tuple(tuple(row) for row in raised)


def connection(subject: Geometry) -> Rank3:
    """``Gamma^a_bc``, from its definition and from nothing published.

    Record 0002: no set of published equations is copied into this tree. The
    Levi-Civita connection of a metric is fixed by the metric alone, so no sign
    of :mod:`raumbuch.conventions` enters here; what a convention decides is the
    Riemann tensor below.
    """
    size = len(subject.coordinates)
    raised = inverse(subject)
    derivative = _metric_derivatives(subject)
    symbols = [[[algebra.integer(0)] * size for _ in range(size)] for _ in range(size)]
    for upper, lower, other in itertools.product(range(size), repeat=3):
        if other < lower:
            continue
        total = algebra.integer(0)
        for index in range(size):
            inner = algebra.subtract(
                algebra.add(
                    derivative[lower][index][other], derivative[other][index][lower]
                ),
                derivative[index][lower][other],
            )
            total = algebra.add(total, algebra.multiply(raised[upper][index], inner))
        value = algebra.normal_form(algebra.multiply(_HALF, total))
        symbols[upper][lower][other] = value
        symbols[upper][other][lower] = value
    return tuple(tuple(tuple(row) for row in block) for block in symbols)


def riemann(subject: Geometry) -> Rank4:
    """``R^a_bcd``, under the Ricci identity :mod:`raumbuch.conventions` fixes."""
    size = len(subject.coordinates)
    symbols = connection(subject)
    tensor = [
        [[[algebra.integer(0)] * size for _ in range(size)] for _ in range(size)]
        for _ in range(size)
    ]
    sign = algebra.integer(conventions.RIEMANN_SIGN)
    for upper, lower in itertools.product(range(size), repeat=2):
        for first, second in itertools.combinations(range(size), 2):
            value = algebra.subtract(
                algebra.differentiate(
                    symbols[upper][second][lower], subject.coordinates[first]
                ),
                algebra.differentiate(
                    symbols[upper][first][lower], subject.coordinates[second]
                ),
            )
            for index in range(size):
                value = algebra.add(
                    value,
                    algebra.subtract(
                        algebra.multiply(
                            symbols[upper][first][index], symbols[index][second][lower]
                        ),
                        algebra.multiply(
                            symbols[upper][second][index], symbols[index][first][lower]
                        ),
                    ),
                )
            value = algebra.normal_form(algebra.multiply(sign, value))
            tensor[upper][lower][first][second] = value
            tensor[upper][lower][second][first] = algebra.negate(value)
    return tuple(
        tuple(tuple(tuple(row) for row in pair) for pair in block) for block in tensor
    )


def lowered(subject: Geometry, tensor: Rank4) -> Rank4:
    """``R_abcd`` from ``R^a_bcd``, which is the shape a published table states."""
    size = len(subject.coordinates)
    result = [
        [[[algebra.integer(0)] * size for _ in range(size)] for _ in range(size)]
        for _ in range(size)
    ]
    for lower, second in itertools.product(range(size), repeat=2):
        for third, fourth in itertools.combinations(range(size), 2):
            total = algebra.integer(0)
            for index in range(size):
                total = algebra.add(
                    total,
                    algebra.multiply(
                        subject.component(lower, index),
                        tensor[index][second][third][fourth],
                    ),
                )
            total = algebra.normal_form(total)
            result[lower][second][third][fourth] = total
            result[lower][second][fourth][third] = algebra.negate(total)
    return tuple(
        tuple(tuple(tuple(row) for row in pair) for pair in block) for block in result
    )


def tetrad(subject: Geometry, legs: tuple[tuple[algebra.Value, ...], ...]) -> Tetrad:
    """The legs as a tetrad, once the conditions hold. Refused where they do not.

    This is the only route to a :class:`Tetrad`, so a set of legs reaching the
    algorithm is a set the conditions were checked on rather than assumed of.
    """
    candidate = Tetrad(tuple(tuple(leg) for leg in legs))
    check(subject, candidate)
    return candidate


def check(subject: Geometry, candidate: Tetrad) -> None:
    """Refuse unless the legs satisfy the normalisation record 0002 fixes.

    Both statements that record writes are checked. The ten inner products are
    what a reader compares against a paper, and the completeness relation is
    what the record names as the thing an implementation checks a constructed
    tetrad against.

    **No fixture reddens the completeness relation on its own, and it is kept
    anyway.** Where the ten products hold, a fourth leg outside the plane the
    other three leave is already excluded by them, so the second check is a
    second reading of the same fact rather than a second fact. It is here
    because record 0002 names it, and because it is the statement written in
    the direction a reader of a paper checks. What that costs is one guard this
    suite cannot prove bites by deleting it, which is written down rather than
    left for somebody to find by deleting it and seeing nothing happen.
    """
    expected = {
        ("l", "n"): conventions.L_DOT_N,
        ("m", "mbar"): conventions.M_DOT_MBAR,
    }
    for first, second in itertools.combinations_with_replacement(conventions.LEGS, 2):
        wanted = expected.get((first, second), 0)
        product = _inner(subject, candidate.leg(first), candidate.leg(second))
        difference = algebra.subtract(product, algebra.integer(wanted))
        if not algebra.is_zero(difference):
            refusal.refuse(
                refusal.TETRAD_CONDITION_FAILS,
                f"record 0002 fixes {first}.{second} = {wanted} and these legs "
                f"give {algebra.text(algebra.normal_form(product))}",
            )
    _completeness(subject, candidate)


def tetrad_from_metric(subject: Geometry) -> Tetrad:
    """A null tetrad built from the metric, exactly, or a refusal saying why not.

    The construction is one procedure and it is declared rather than inferred.
    The chart's first two coordinates carry a Lorentzian two-block and its last
    two a transverse block; the two null directions of the first block become
    ``l`` and ``n``, and an orthonormal pair from the second becomes ``m``. A
    metric that does not split that way is refused by name, and so is one whose
    construction would need a square root the field of record 0009 does not
    hold.

    What the refusals cost is written where a reader will meet it. A metric with
    an off-block component, which is what Kerr in Boyer-Lindquist coordinates is,
    does not come through here; its tetrad is passed to :func:`tetrad` instead,
    where the same conditions judge it.
    """
    _block_paired(subject)
    first, second = _null_pair(subject)
    third = _transverse(subject)
    return tetrad(subject, (first, second, third))


def frame_components(
    subject: Geometry, tensor: Rank4, frame: Tetrad
) -> dict[tuple[str, ...], algebra.Value]:
    """``R_abcd`` in frame indices, keyed by the leg names of record 0002.

    This is where the coordinate index stops. Everything the algorithm carries
    from here on is frame indexed, and the contraction of these into the scalars
    the algorithm consumes is issue #45.
    """
    size = len(subject.coordinates)
    partial: dict[tuple[str, ...], object] = {(): tensor}
    for depth in (4, 3, 2, 1):
        stage: dict[tuple[str, ...], object] = {}
        for names, block in partial.items():
            for name in conventions.LEGS:
                stage[(*names, name)] = _contract_first(
                    block, frame.leg(name), depth, size
                )
        partial = stage
    return {names: algebra.normal_form(value) for names, value in partial.items()}


def _contract_first(block, leg: tuple[algebra.Value, ...], depth: int, size: int):
    """The first index of a ``depth``-index array, contracted with one leg.

    One index at a time rather than four at once. The four-index array has
    ``size**4`` entries and a tetrad has four legs, so contracting all four
    indices for every combination of legs at once costs the fourth power of the
    size for each of the ``4**4`` combinations, and this costs the sum of four
    stages instead.
    """
    if depth == 1:
        return algebra.normal_form(
            _sum(algebra.multiply(block[index], leg[index]) for index in range(size))
        )
    return [
        _contract_first(
            [block[index][position] for index in range(size)], leg, depth - 1, size
        )
        for position in range(size)
    ]


def _inner(
    subject: Geometry,
    first: tuple[algebra.Value, ...],
    second: tuple[algebra.Value, ...],
) -> algebra.Value:
    total = algebra.integer(0)
    for row, column in itertools.product(range(len(subject.coordinates)), repeat=2):
        total = algebra.add(
            total,
            algebra.multiply(
                subject.component(row, column),
                algebra.multiply(first[row], second[column]),
            ),
        )
    return algebra.normal_form(total)


def _completeness(subject: Geometry, candidate: Tetrad) -> None:
    """``g_ab`` rebuilt from the legs, against the metric it was built from."""
    size = len(subject.coordinates)
    lower = {
        name: tuple(
            algebra.normal_form(
                _sum(
                    algebra.multiply(subject.component(index, other), leg[other])
                    for other in range(size)
                )
            )
            for index in range(size)
        )
        for name, leg in ((name, candidate.leg(name)) for name in conventions.LEGS)
    }
    for row, column in itertools.product(range(size), repeat=2):
        rebuilt = algebra.add(
            algebra.multiply(
                algebra.integer(conventions.L_DOT_N),
                algebra.add(
                    algebra.multiply(lower["l"][row], lower["n"][column]),
                    algebra.multiply(lower["n"][row], lower["l"][column]),
                ),
            ),
            algebra.multiply(
                algebra.integer(conventions.M_DOT_MBAR),
                algebra.add(
                    algebra.multiply(lower["m"][row], lower["mbar"][column]),
                    algebra.multiply(lower["mbar"][row], lower["m"][column]),
                ),
            ),
        )
        difference = algebra.subtract(rebuilt, subject.component(row, column))
        if not algebra.is_zero(difference):
            refusal.refuse(
                refusal.TETRAD_CONDITION_FAILS,
                "the legs do not rebuild the metric: at "
                f"{subject.coordinates[row]}{subject.coordinates[column]} record "
                "0002's completeness relation gives "
                f"{algebra.text(algebra.normal_form(rebuilt))} against "
                f"{algebra.text(algebra.normal_form(subject.component(row, column)))}",
            )


def _block_paired(subject: Geometry) -> None:
    for row in BOOST_PAIR:
        for column in TRANSVERSE_PAIR:
            if not algebra.is_zero(subject.component(row, column)):
                refusal.refuse(
                    refusal.FRAME_IS_NOT_BLOCK_PAIRED,
                    "this construction splits the chart into the first two "
                    "coordinates and the last two, and "
                    f"{subject.coordinates[row]}{subject.coordinates[column]} is "
                    "not zero across that split: "
                    + algebra.text(algebra.normal_form(subject.component(row, column))),
                )


def _null_pair(
    subject: Geometry,
) -> tuple[tuple[algebra.Value, ...], tuple[algebra.Value, ...]]:
    """``l`` and ``n``, as the two null directions of the Lorentzian two-block."""
    size = len(subject.coordinates)
    first, second = BOOST_PAIR
    head = subject.component(first, first)
    cross = subject.component(first, second)
    tail = subject.component(second, second)
    if algebra.is_zero(head):
        legs = _null_pair_from_a_null_axis(first, second, cross, tail, size)
    elif algebra.is_zero(tail):
        legs = _null_pair_from_a_null_axis(second, first, cross, head, size)
    elif algebra.verdict(head) == algebra.NONZERO:
        legs = _null_pair_from_a_root(subject, head, cross, tail, size)
    else:
        refusal.refuse(
            refusal.FRAME_CONSTRUCTION_LEAVES_THE_FIELD,
            "the null directions of the two-block are read off a diagonal "
            "component that is zero or off a root of the discriminant, and "
            f"whether {subject.coordinates[first]}{subject.coordinates[first]} "
            "is zero was not decided: " + algebra.text(algebra.normal_form(head)),
        )
    return legs


def _null_pair_from_a_null_axis(
    axis: int, other: int, cross: algebra.Value, opposite: algebra.Value, size: int
) -> tuple[tuple[algebra.Value, ...], tuple[algebra.Value, ...]]:
    """Where one axis of the block is already null, as a plane wave's is."""
    if algebra.verdict(cross) != algebra.NONZERO:
        refusal.refuse(
            refusal.FRAME_CONSTRUCTION_LEAVES_THE_FIELD,
            "one axis of the two-block is null and the off-diagonal component "
            "that would normalise against it is not decidably non-zero: "
            + algebra.text(algebra.normal_form(cross)),
        )
    first = [algebra.integer(0)] * size
    first[axis] = algebra.integer(1)
    slope = algebra.negate(
        algebra.divide(opposite, algebra.multiply(algebra.integer(2), cross))
    )
    scale = algebra.divide(algebra.integer(conventions.L_DOT_N), cross)
    second = [algebra.integer(0)] * size
    second[other] = algebra.normal_form(scale)
    second[axis] = algebra.normal_form(algebra.multiply(scale, slope))
    return tuple(first), tuple(second)


def _null_pair_from_a_root(
    subject: Geometry,
    head: algebra.Value,
    cross: algebra.Value,
    tail: algebra.Value,
    size: int,
) -> tuple[tuple[algebra.Value, ...], tuple[algebra.Value, ...]]:
    """The generic case: both null directions carry a root of the discriminant."""
    first, second = BOOST_PAIR
    discriminant = algebra.subtract(
        algebra.power(cross, 2), algebra.multiply(head, tail)
    )
    root = algebra.square_root(discriminant)
    if root is None:
        refusal.refuse(
            refusal.FRAME_CONSTRUCTION_LEAVES_THE_FIELD,
            "the null directions of the two-block on "
            f"{subject.coordinates[first]} and {subject.coordinates[second]} "
            "need the square root of "
            + algebra.text(algebra.normal_form(discriminant))
            + ", and the field of record 0009 does not hold one",
        )
    outgoing = [algebra.integer(0)] * size
    ingoing = [algebra.integer(0)] * size
    outgoing[first] = algebra.normal_form(algebra.add(algebra.negate(cross), root))
    outgoing[second] = head
    determinant = algebra.subtract(
        algebra.multiply(head, tail), algebra.power(cross, 2)
    )
    scale = algebra.divide(
        algebra.integer(conventions.L_DOT_N),
        algebra.multiply(algebra.multiply(algebra.integer(2), head), determinant),
    )
    ingoing[first] = algebra.normal_form(
        algebra.multiply(scale, algebra.subtract(algebra.negate(cross), root))
    )
    ingoing[second] = algebra.normal_form(algebra.multiply(scale, head))
    return tuple(outgoing), tuple(ingoing)


def _transverse(subject: Geometry) -> tuple[algebra.Value, ...]:
    """``m``, from an orthonormal pair in the transverse two-block."""
    size = len(subject.coordinates)
    first, second = TRANSVERSE_PAIR
    head = subject.component(first, first)
    cross = subject.component(first, second)
    tail = subject.component(second, second)
    length = _root_or_refusal(subject, head, "the first transverse direction")
    remaining = algebra.subtract(tail, algebra.divide(algebra.power(cross, 2), head))
    other = _root_or_refusal(subject, remaining, "the second transverse direction")
    forward = [algebra.integer(0)] * size
    forward[first] = algebra.divide(algebra.integer(1), length)
    sideways = [algebra.integer(0)] * size
    sideways[second] = algebra.divide(algebra.integer(1), other)
    sideways[first] = algebra.normal_form(
        algebra.negate(
            algebra.divide(algebra.divide(cross, head), other),
        )
    )
    return tuple(
        algebra.normal_form(
            algebra.multiply(
                _TRANSVERSE_PHASE,
                algebra.add(
                    forward[index],
                    algebra.multiply(algebra.imaginary_unit(), sideways[index]),
                ),
            )
        )
        for index in range(size)
    )


def _root_or_refusal(
    subject: Geometry, value: algebra.Value, which: str
) -> algebra.Value:
    root = algebra.square_root(value)
    if root is None:
        refusal.refuse(
            refusal.FRAME_CONSTRUCTION_LEAVES_THE_FIELD,
            f"normalising {which} of the transverse block on "
            f"{subject.coordinates[TRANSVERSE_PAIR[0]]} and "
            f"{subject.coordinates[TRANSVERSE_PAIR[1]]} needs the square root "
            "of " + algebra.text(algebra.normal_form(value)) + ", and the field "
            "of record 0009 does not hold one",
        )
    return root


def _metric_derivatives(
    subject: Geometry,
) -> tuple[tuple[tuple[algebra.Value, ...], ...], ...]:
    """``d_c g_ab``, computed once and read many times."""
    size = len(subject.coordinates)
    return tuple(
        tuple(
            tuple(
                algebra.differentiate(
                    subject.component(row, column), subject.coordinates[direction]
                )
                for column in range(size)
            )
            for row in range(size)
        )
        for direction in range(size)
    )


def _determinant(rows: list[list[algebra.Value]]) -> algebra.Value:
    if len(rows) == 1:
        return rows[0][0]
    total = algebra.integer(0)
    for column in range(len(rows)):
        term = algebra.multiply(rows[0][column], _minor(rows, 0, column))
        total = (
            algebra.add(total, term)
            if column % 2 == 0
            else algebra.subtract(total, term)
        )
    return algebra.normal_form(total)


def _minor(rows: list[list[algebra.Value]], row: int, column: int) -> algebra.Value:
    smaller = [
        [value for index, value in enumerate(other) if index != column]
        for position, other in enumerate(rows)
        if position != row
    ]
    return _determinant(smaller)


def _cofactor(rows: list[list[algebra.Value]], row: int, column: int) -> algebra.Value:
    signed = _minor(rows, row, column)
    return signed if (row + column) % 2 == 0 else algebra.negate(signed)


def _sum(values) -> algebra.Value:
    total = algebra.integer(0)
    for value in values:
        total = algebra.add(total, value)
    return total
