"""The curvature, against what is published about four metrics.

The comparison is a test rather than a paragraph, which is what issue #44 asks
for. What is compared and what it rests on:

The connection is fixed by the metric alone, so a published table of Christoffel
symbols is the same table under every curvature sign convention, and comparing
against one tests the arithmetic without testing the conventions.

The Riemann components are not. Record 0002 fixes three signs and a vacuum entry
cannot detect any of them applied backwards, so the Schwarzschild table below is
not self-certifying. What pins it is the Kottler entry: with a cosmological
constant the field equations of record 0002 require ``R_ab = Lambda_cc*g_ab``,
and that equation changes sign with the convention. The Kretschmann scalar is
quadratic in the Riemann tensor and so is the same number under either
convention, which makes it a check on the arithmetic and not on the signs.

The frame components are checked against the coordinate ones they are built
from, by rebuilding the second from the first. That inherits the published
comparison rather than making a second one: a published table of frame
components is thin, and the contraction of these into the scalars the algorithm
consumes is issue #45.
"""

from __future__ import annotations

import itertools
import unittest
from pathlib import Path

import metrics

from raumbuch import algebra, conventions, curvature, refusal

ROOT = Path(__file__).resolve().parents[1]
CONVENTIONS_RECORD = ROOT / "docs" / "decisions" / "0002-frame-and-conventions.md"


def symbol(name: str) -> algebra.Value:
    return algebra.symbol(name)


def zero(value: algebra.Value) -> bool:
    return algebra.is_zero(value)


def same(left: algebra.Value, right: algebra.Value) -> bool:
    return algebra.is_zero(algebra.subtract(left, right))


def ricci(
    subject: curvature.Geometry, tensor: curvature.Rank4
) -> list[list[algebra.Value]]:
    """``R_ab = R^c_acb``, the contraction record 0002 fixes.

    Here rather than in the module: the Ricci tensor is one of the components
    the algorithm consumes and it belongs to issue #45. What it is doing here is
    reading the Riemann tensor back in the one shape a published field equation
    is written in, so that the Kottler entry can pin the sign convention.
    """
    size = len(subject.coordinates)
    slots = conventions.RICCI_SLOTS
    if slots != (0, 2):
        raise AssertionError(f"this contraction is written for (0, 2), not {slots}")
    return [
        [
            algebra.normal_form(
                _total(tensor[index][first][index][second] for index in range(size))
            )
            for second in range(size)
        ]
        for first in range(size)
    ]


def _total(values) -> algebra.Value:
    running = algebra.integer(0)
    for value in values:
        running = algebra.add(running, value)
    return running


def _raised(subject: curvature.Geometry, tensor: curvature.Rank4) -> curvature.Rank4:
    """``R^abcd`` from ``R_abcd``, one index at a time."""
    size = len(subject.coordinates)
    raised = curvature.inverse(subject)
    result = tensor
    for slot in range(4):
        current = result
        rebuilt = [
            [[[algebra.integer(0)] * size for _ in range(size)] for _ in range(size)]
            for _ in range(size)
        ]
        for position in itertools.product(range(size), repeat=4):
            total = algebra.integer(0)
            for index in range(size):
                other = list(position)
                other[slot] = index
                total = algebra.add(
                    total,
                    algebra.multiply(
                        raised[position[slot]][index],
                        current[other[0]][other[1]][other[2]][other[3]],
                    ),
                )
            rebuilt[position[0]][position[1]][position[2]][position[3]] = (
                algebra.normal_form(total)
            )
        result = rebuilt
    return result


class TheConnection(unittest.TestCase):
    """Christoffel symbols against published tables."""

    def test_schwarzschild_matches_the_published_symbols(self) -> None:
        subject = metrics.schwarzschild()
        mass, radius, angle = symbol("M"), symbol("r"), symbol("theta")
        profile = algebra.subtract(
            algebra.integer(1),
            algebra.divide(algebra.multiply(algebra.integer(2), mass), radius),
        )
        sine = algebra.applied("sin", angle)
        cosine = algebra.applied("cos", angle)
        published = {
            ("t", "t", "r"): algebra.divide(
                mass, algebra.multiply(algebra.power(radius, 2), profile)
            ),
            ("r", "t", "t"): algebra.divide(
                algebra.multiply(mass, profile), algebra.power(radius, 2)
            ),
            ("r", "r", "r"): algebra.negate(
                algebra.divide(
                    mass, algebra.multiply(algebra.power(radius, 2), profile)
                )
            ),
            ("r", "theta", "theta"): algebra.negate(algebra.multiply(radius, profile)),
            ("r", "phi", "phi"): algebra.negate(
                algebra.multiply(
                    algebra.multiply(radius, profile), algebra.power(sine, 2)
                )
            ),
            ("theta", "r", "theta"): algebra.divide(algebra.integer(1), radius),
            ("theta", "phi", "phi"): algebra.negate(algebra.multiply(sine, cosine)),
            ("phi", "r", "phi"): algebra.divide(algebra.integer(1), radius),
            ("phi", "theta", "phi"): algebra.divide(cosine, sine),
        }
        self._compare(subject, published)

    def test_flrw_matches_the_published_symbols(self) -> None:
        subject = metrics.flrw()
        scale = algebra.free_function("a", (symbol("t"),))
        rate = algebra.differentiate(scale, "t")
        published: dict[tuple[str, str, str], algebra.Value] = {}
        for axis in ("x", "y", "z"):
            published[("t", axis, axis)] = algebra.multiply(scale, rate)
            published[(axis, "t", axis)] = algebra.divide(rate, scale)
        self._compare(subject, published)

    def _compare(
        self,
        subject: curvature.Geometry,
        published: dict[tuple[str, str, str], algebra.Value],
    ) -> None:
        """Every symbol, against the table: the listed ones and the absent ones.

        Both directions. A table compared only where it has an entry is a table
        that cannot tell a correct connection from one carrying a component
        nobody published.
        """
        computed = curvature.connection(subject)
        names = subject.coordinates
        for upper, lower, other in itertools.product(range(len(names)), repeat=3):
            if other < lower:
                continue
            key = (names[upper], names[lower], names[other])
            wanted = published.get(key, algebra.integer(0))
            self.assertTrue(
                same(computed[upper][lower][other], wanted),
                f"Gamma^{key[0]}_{key[1]}{key[2]} is "
                f"{algebra.text(algebra.normal_form(computed[upper][lower][other]))} "
                f"and the published symbol is {algebra.text(wanted)}",
            )


class TheRiemannTensor(unittest.TestCase):
    """The curvature itself, against what is published about four metrics."""

    def test_schwarzschild_matches_the_published_components(self) -> None:
        subject = metrics.schwarzschild()
        tensor = curvature.lowered(subject, curvature.riemann(subject))
        mass, radius, angle = symbol("M"), symbol("r"), symbol("theta")
        profile = algebra.subtract(
            algebra.integer(1),
            algebra.divide(algebra.multiply(algebra.integer(2), mass), radius),
        )
        squared_sine = algebra.power(algebra.applied("sin", angle), 2)
        radial = algebra.divide(
            algebra.multiply(algebra.integer(-2), mass), algebra.power(radius, 3)
        )
        crossed = algebra.divide(algebra.multiply(mass, profile), radius)
        mixed = algebra.negate(algebra.divide(mass, algebra.multiply(radius, profile)))
        published = {
            ("t", "r", "t", "r"): radial,
            ("t", "theta", "t", "theta"): crossed,
            ("t", "phi", "t", "phi"): algebra.multiply(crossed, squared_sine),
            ("r", "theta", "r", "theta"): mixed,
            ("r", "phi", "r", "phi"): algebra.multiply(mixed, squared_sine),
            ("theta", "phi", "theta", "phi"): algebra.multiply(
                algebra.multiply(algebra.integer(2), algebra.multiply(mass, radius)),
                squared_sine,
            ),
        }
        names = subject.coordinates
        for first, second in itertools.combinations(range(4), 2):
            for third, fourth in itertools.combinations(range(4), 2):
                if (first, second) > (third, fourth):
                    continue
                key = (names[first], names[second], names[third], names[fourth])
                wanted = published.get(key, algebra.integer(0))
                self.assertTrue(
                    same(tensor[first][second][third][fourth], wanted),
                    f"R_{''.join(key)} is "
                    + algebra.text(
                        algebra.normal_form(tensor[first][second][third][fourth])
                    )
                    + f" and the published component is {algebra.text(wanted)}",
                )

    def test_schwarzschild_reaches_the_published_kretschmann_scalar(self) -> None:
        """``R_abcd R^abcd = 48*M^2/r^6``, which no sign convention moves."""
        subject = metrics.schwarzschild()
        tensor = curvature.lowered(subject, curvature.riemann(subject))
        raised = _raised(subject, tensor)
        total = algebra.integer(0)
        for position in itertools.product(range(4), repeat=4):
            total = algebra.add(
                total,
                algebra.multiply(
                    tensor[position[0]][position[1]][position[2]][position[3]],
                    raised[position[0]][position[1]][position[2]][position[3]],
                ),
            )
        published = algebra.divide(
            algebra.multiply(algebra.integer(48), algebra.power(symbol("M"), 2)),
            algebra.power(symbol("r"), 6),
        )
        self.assertTrue(
            same(total, published),
            "the Kretschmann scalar came out as "
            + algebra.text(algebra.normal_form(total)),
        )

    def test_schwarzschild_is_a_vacuum(self) -> None:
        subject = metrics.schwarzschild()
        tensor = ricci(subject, curvature.riemann(subject))
        for first, second in itertools.product(range(4), repeat=2):
            self.assertTrue(
                zero(tensor[first][second]),
                f"R_{first}{second} is {algebra.text(tensor[first][second])}",
            )

    def test_kottler_solves_the_field_equations_with_a_cosmological_constant(
        self,
    ) -> None:
        """The entry a vacuum one cannot replace, and what it pins.

        Record 0002 asks for a geometry whose Ricci curvature does not vanish,
        because the sign of the Ricci scalar is what tells its convention set
        from the negatives of that set. Under the field equations that record
        writes, an empty universe with a cosmological constant has
        ``R_ab = Lambda_cc*g_ab``. Flip :data:`raumbuch.conventions.RIEMANN_SIGN`
        and this test fails while every vacuum test above it passes.
        """
        subject = metrics.kottler()
        tensor = ricci(subject, curvature.riemann(subject))
        constant = symbol("Lambda_cc")
        scalar = algebra.integer(0)
        raised = curvature.inverse(subject)
        for first, second in itertools.product(range(4), repeat=2):
            difference = algebra.subtract(
                tensor[first][second],
                algebra.multiply(constant, subject.component(first, second)),
            )
            self.assertTrue(
                zero(difference),
                f"R_{first}{second} - Lambda_cc*g_{first}{second} is "
                + algebra.text(algebra.normal_form(difference)),
            )
            scalar = algebra.add(
                scalar, algebra.multiply(raised[first][second], tensor[first][second])
            )
        self.assertTrue(
            same(scalar, algebra.multiply(algebra.integer(4), constant)),
            "the Ricci scalar came out as " + algebra.text(algebra.normal_form(scalar)),
        )

    def test_flrw_reaches_the_published_ricci_and_the_friedmann_equation(self) -> None:
        subject = metrics.flrw()
        tensor = ricci(subject, curvature.riemann(subject))
        scale = algebra.free_function("a", (symbol("t"),))
        rate = algebra.differentiate(scale, "t")
        acceleration = algebra.differentiate(rate, "t")
        published_time = algebra.negate(
            algebra.divide(algebra.multiply(algebra.integer(3), acceleration), scale)
        )
        published_space = algebra.add(
            algebra.multiply(scale, acceleration),
            algebra.multiply(algebra.integer(2), algebra.power(rate, 2)),
        )
        self.assertTrue(
            same(tensor[0][0], published_time),
            f"R_tt is {algebra.text(tensor[0][0])}",
        )
        for axis in (1, 2, 3):
            self.assertTrue(
                same(tensor[axis][axis], published_space),
                f"R_{axis}{axis} is {algebra.text(tensor[axis][axis])}",
            )
        for first, second in itertools.permutations(range(4), 2):
            self.assertTrue(zero(tensor[first][second]))
        scalar = algebra.integer(0)
        raised = curvature.inverse(subject)
        for first, second in itertools.product(range(4), repeat=2):
            scalar = algebra.add(
                scalar, algebra.multiply(raised[first][second], tensor[first][second])
            )
        einstein = algebra.subtract(
            tensor[0][0],
            algebra.multiply(
                algebra.rational(1, 2),
                algebra.multiply(scalar, subject.component(0, 0)),
            ),
        )
        friedmann = algebra.multiply(
            algebra.integer(3), algebra.power(algebra.divide(rate, scale), 2)
        )
        self.assertTrue(
            same(einstein, friedmann),
            "the tt component of the Einstein tensor came out as "
            + algebra.text(algebra.normal_form(einstein)),
        )

    def test_a_harmonic_plane_wave_is_a_vacuum(self) -> None:
        subject = metrics.plane_wave(metrics.harmonic_profile())
        tensor = ricci(subject, curvature.riemann(subject))
        for first, second in itertools.product(range(4), repeat=2):
            self.assertTrue(
                zero(tensor[first][second]),
                f"R_{first}{second} is {algebra.text(tensor[first][second])}",
            )

    def test_an_unharmonic_profile_leaves_a_null_fluid(self) -> None:
        """One component, and it is the one a published null fluid names.

        ``T_ab`` for pure radiation is proportional to ``l_a l_b`` with ``l`` the
        wave vector, so every component but ``uu`` has to vanish and ``uu`` must
        not. The profile is ``h(u)*(x^2 + y^2)``, whose transverse Laplacian is
        ``4*h(u)``, and the Ricci component is that times a half.
        """
        subject = metrics.plane_wave(metrics.unharmonic_profile())
        tensor = ricci(subject, curvature.riemann(subject))
        front = algebra.free_function("h", (symbol("u"),))
        expected = algebra.multiply(algebra.integer(-2), front)
        self.assertTrue(
            same(tensor[0][0], expected),
            f"R_uu is {algebra.text(tensor[0][0])}",
        )
        for first, second in itertools.product(range(4), repeat=2):
            if (first, second) == (0, 0):
                continue
            self.assertTrue(
                zero(tensor[first][second]),
                f"R_{first}{second} is {algebra.text(tensor[first][second])}",
            )

    def test_the_algebraic_symmetries_hold(self) -> None:
        """What a Riemann tensor is, on every fixture that has one.

        The three symmetries and the first Bianchi identity are properties of
        the tensor rather than of any one metric, so they catch an index written
        in the wrong slot on a fixture whose published table happens to be
        symmetric enough not to.
        """
        for name, subject in (
            ("schwarzschild", metrics.schwarzschild()),
            ("kottler", metrics.kottler()),
            ("flrw", metrics.flrw()),
            ("plane wave", metrics.plane_wave(metrics.harmonic_profile())),
        ):
            tensor = curvature.lowered(subject, curvature.riemann(subject))
            for a, b, c, d in itertools.product(range(4), repeat=4):
                with self.subTest(metric=name, indices=(a, b, c, d)):
                    self.assertTrue(
                        zero(algebra.add(tensor[a][b][c][d], tensor[b][a][c][d])),
                        "antisymmetry in the first pair",
                    )
                    self.assertTrue(
                        zero(algebra.subtract(tensor[a][b][c][d], tensor[c][d][a][b])),
                        "exchange of the two pairs",
                    )
                    self.assertTrue(
                        zero(
                            algebra.add(
                                algebra.add(tensor[a][b][c][d], tensor[a][c][d][b]),
                                tensor[a][d][b][c],
                            )
                        ),
                        "the first Bianchi identity",
                    )


class TheTetrad(unittest.TestCase):
    """The frame, the conditions on it, and what the construction refuses."""

    def test_every_fixture_gets_a_tetrad_that_satisfies_the_conditions(self) -> None:
        for name, subject in (
            ("schwarzschild", metrics.schwarzschild()),
            ("kottler", metrics.kottler()),
            ("flrw", metrics.flrw()),
            ("plane wave", metrics.plane_wave(metrics.harmonic_profile())),
        ):
            with self.subTest(metric=name):
                frame = curvature.tetrad_from_metric(subject)
                curvature.check(subject, frame)

    def test_the_construction_is_deterministic(self) -> None:
        """Two runs, the same legs. Record 0012, read at this layer."""
        subject = metrics.schwarzschild()
        first = curvature.tetrad_from_metric(subject)
        second = curvature.tetrad_from_metric(subject)
        for name in conventions.LEGS:
            for left, right in zip(first.leg(name), second.leg(name), strict=True):
                self.assertTrue(same(left, right))

    def test_every_curvature_reason_is_reached_by_its_own_fixture(self) -> None:
        """The third corpus, driven from the vocabulary rather than from a list.

        `tests/test_corpus.py` compares the union of the three corpora against
        the enumeration in :mod:`raumbuch.refusal`, so a reason added without a
        fixture fails there. This is the other half: each fixture reaches the
        reason it is filed under and not some other refusal on the way.
        """
        for reason, fixture in metrics.REFUSED.items():
            with self.subTest(reason=reason):
                with self.assertRaises(refusal.Refused) as refused:
                    fixture()
                self.assertEqual(refused.exception.reason, reason)

    def test_the_refusal_names_the_product_that_failed(self) -> None:
        """A refusal that says which condition, because "wrong tetrad" is a shrug."""
        subject = metrics.schwarzschild()
        frame = curvature.tetrad_from_metric(subject)
        scaled = tuple(
            algebra.multiply(algebra.integer(2), part) for part in frame.leg("m")
        )
        with self.assertRaises(refusal.Refused) as refused:
            curvature.tetrad(subject, (frame.leg("l"), frame.leg("n"), scaled))
        self.assertIn("m.mbar", refused.exception.detail)

    def test_a_transverse_leg_in_the_wrong_plane_is_refused(self) -> None:
        """The other mistake: a leg that is not transverse at all.

        The third leg is replaced by a combination of the first two, which is
        the shape a construction that lost track of the block split would
        produce. It fails on the products before the completeness relation is
        reached, and the refusal names which product it failed.
        """
        subject = metrics.schwarzschild()
        frame = curvature.tetrad_from_metric(subject)
        flattened = tuple(
            algebra.add(first, second)
            for first, second in zip(frame.leg("l"), frame.leg("n"), strict=True)
        )
        with self.assertRaises(refusal.Refused) as refused:
            curvature.tetrad(subject, (frame.leg("l"), frame.leg("n"), flattened))
        self.assertEqual(refused.exception.reason, refusal.TETRAD_CONDITION_FAILS)

    def test_the_refusal_names_the_component_off_the_blocks(self) -> None:
        with self.assertRaises(refusal.Refused) as refused:
            curvature.tetrad_from_metric(metrics.kerr_shape())
        self.assertIn("tphi", refused.exception.detail)

    def test_the_refusal_names_the_root_the_field_does_not_hold(self) -> None:
        with self.assertRaises(refusal.Refused) as refused:
            curvature.tetrad_from_metric(metrics.unrooted())
        self.assertIn("square root of r", refused.exception.detail)

    def test_legs_may_be_given_rather_than_built(self) -> None:
        """The route a metric off the two blocks takes, on one that is not.

        The legs here are the ones the construction produces, handed back to the
        checking route. What that proves is that the two routes reach the same
        judgement, which is what stops a second construction elsewhere having a
        second opinion about the conditions.
        """
        subject = metrics.schwarzschild()
        built = curvature.tetrad_from_metric(subject)
        given = curvature.tetrad(
            subject, (built.leg("l"), built.leg("n"), built.leg("m"))
        )
        for name in conventions.LEGS:
            for left, right in zip(built.leg(name), given.leg(name), strict=True):
                self.assertTrue(same(left, right))


class TheFrameComponents(unittest.TestCase):
    """Where the coordinate index stops."""

    def test_the_frame_components_rebuild_the_coordinate_ones(self) -> None:
        """The transition, checked in the direction that has an answer already.

        Record 0002's completeness relation writes the metric out of the legs,
        and the same relation writes any tensor's coordinate components out of
        its frame ones. So the frame components are checked against the
        coordinate table that was compared against a publication, rather than
        against a published frame table, which for these metrics is thin.
        """
        subject = metrics.schwarzschild()
        tensor = curvature.lowered(subject, curvature.riemann(subject))
        frame = curvature.tetrad_from_metric(subject)
        components = curvature.frame_components(subject, tensor, frame)
        lower = {
            name: _lowered_leg(subject, frame.leg(name)) for name in conventions.LEGS
        }
        dual = {"l": "n", "n": "l", "m": "mbar", "mbar": "m"}
        weight = {
            "l": conventions.L_DOT_N,
            "n": conventions.L_DOT_N,
            "m": conventions.M_DOT_MBAR,
            "mbar": conventions.M_DOT_MBAR,
        }
        for position in itertools.product(range(4), repeat=4):
            rebuilt = algebra.integer(0)
            for names in itertools.product(conventions.LEGS, repeat=4):
                term = components[names]
                for slot, name in enumerate(names):
                    term = algebra.multiply(term, lower[dual[name]][position[slot]])
                    term = algebra.multiply(term, algebra.integer(weight[name]))
                rebuilt = algebra.add(rebuilt, term)
            self.assertTrue(
                same(
                    rebuilt,
                    tensor[position[0]][position[1]][position[2]][position[3]],
                ),
                f"the frame components rebuild R_{position} as "
                + algebra.text(algebra.normal_form(rebuilt)),
            )


class TheConventions(unittest.TestCase):
    """One place, and what changes when it is edited."""

    def test_flipping_the_riemann_sign_flips_every_component(self) -> None:
        """The last line of the Done-when, proved by making the edit.

        A convention read from one place is a claim about the code, and the way
        to test it is to change that place and watch every component move. If a
        second copy of the sign existed anywhere, the components carrying it
        would not move and this would fail.
        """
        subject = metrics.schwarzschild()
        before = curvature.riemann(subject)
        original = conventions.RIEMANN_SIGN
        try:
            conventions.RIEMANN_SIGN = -original
            after = curvature.riemann(subject)
        finally:
            conventions.RIEMANN_SIGN = original
        moved = 0
        for position in itertools.product(range(4), repeat=4):
            left = before[position[0]][position[1]][position[2]][position[3]]
            right = after[position[0]][position[1]][position[2]][position[3]]
            self.assertTrue(zero(algebra.add(left, right)))
            if not zero(left):
                moved += 1
        self.assertGreater(moved, 0)

    def test_the_signature_is_the_one_record_0002_writes(self) -> None:
        """The constant against the record, so the two cannot part in silence."""
        text = CONVENTIONS_RECORD.read_text(encoding="utf-8")
        self.assertIn(f"The signature is `{conventions.SIGNATURE}`", text)

    def test_the_normalisation_is_the_one_record_0002_writes(self) -> None:
        text = CONVENTIONS_RECORD.read_text(encoding="utf-8")
        first = "l.n = " + ("-1" if conventions.L_DOT_N == -1 else "1")
        second = "m.mbar = " + ("-1" if conventions.M_DOT_MBAR == -1 else "1")
        self.assertIn(first, text)
        self.assertIn(second, text)

    def test_the_legs_are_in_the_order_record_0002_fixes(self) -> None:
        text = CONVENTIONS_RECORD.read_text(encoding="utf-8")
        self.assertIn("`(" + ", ".join(conventions.LEGS) + ")`", text)


class TheArithmeticBoundary(unittest.TestCase):
    """The operations issue #44 added behind record 0001's interface."""

    def test_the_zero_test_gives_the_three_answers_of_record_0009(self) -> None:
        radius = symbol("r")
        self.assertEqual(
            algebra.verdict(algebra.subtract(radius, radius)), algebra.ZERO
        )
        self.assertEqual(algebra.verdict(radius), algebra.NONZERO)
        self.assertEqual(
            algebra.verdict(algebra.free_function("h", (radius,))),
            algebra.UNDETERMINED,
        )

    def test_an_undetermined_value_is_not_treated_as_zero(self) -> None:
        """The safe direction, and the one a wrong branch would be taken in."""
        self.assertFalse(algebra.is_zero(algebra.free_function("h", (symbol("u"),))))

    def test_the_declared_relation_decides_the_pythagorean_case(self) -> None:
        angle = symbol("theta")
        total = algebra.subtract(
            algebra.add(
                algebra.power(algebra.applied("sin", angle), 2),
                algebra.power(algebra.applied("cos", angle), 2),
            ),
            algebra.integer(1),
        )
        self.assertTrue(algebra.is_zero(total))

    def test_a_root_outside_the_field_comes_back_as_none(self) -> None:
        radius = symbol("r")
        self.assertIsNone(algebra.square_root(radius))
        self.assertIsNone(algebra.square_root(algebra.integer(2)))
        root = algebra.square_root(algebra.power(radius, 2))
        self.assertIsNotNone(root)
        self.assertTrue(same(root, radius))

    def test_a_derived_spelling_is_rewritten_into_the_closed_list(self) -> None:
        """``tan`` is admitted by the grammar and is not a seventh function."""
        from raumbuch import expression

        angle = symbol("theta")
        wanted = algebra.divide(
            algebra.applied("sin", angle), algebra.applied("cos", angle)
        )
        self.assertTrue(
            same(algebra.from_expression(expression.parse("tan(theta)")), wanted)
        )


def _lowered_leg(
    subject: curvature.Geometry, leg: tuple[algebra.Value, ...]
) -> tuple[algebra.Value, ...]:
    size = len(subject.coordinates)
    return tuple(
        algebra.normal_form(
            _total(
                algebra.multiply(subject.component(index, other), leg[other])
                for other in range(size)
            )
        )
        for index in range(size)
    )


if __name__ == "__main__":
    unittest.main()
