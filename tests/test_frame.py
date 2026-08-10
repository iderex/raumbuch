"""The frame group: the laws, the action, and what is left of the freedom.

Generated inputs rather than three hand-picked ones, which is what issue #48
asks for and is the difference between a group law that holds and one that holds
on the examples somebody thought of. The generator is seeded and its seed is
written here, so a failure is a fixture rather than an anecdote, which is the
same argument `tests/fuzz.py` makes for the surfaces it covers.

What the inputs are: products of the three stages record 0002 names, with
parameters drawn from the Gaussian rationals. Every such product has determinant
one by construction, so the generator cannot wander out of the group, and the
one thing it therefore cannot exercise is the refusal of an element that is not
in it. That fixture is written by hand below.
"""

from __future__ import annotations

import itertools
import random
import unittest
from fractions import Fraction

import metrics

from raumbuch import algebra, conventions, curvature, frame, refusal

#: The seed. One number, written down, so that every run reads the same inputs
#: and a failure names the case rather than the weather.
SEED = 20260811

#: How many elements the laws are checked over. The cost is arithmetic in a
#: field of rational functions, so this is chosen to be a suite that runs in
#: seconds rather than a campaign; the scheduled fuzz budget of issue #33 is
#: where a larger one would live.
HOW_MANY = 8

#: The numerators and denominators a parameter is built from. Small on purpose:
#: what these inputs are for is the algebra of the group, and a parameter with
#: forty digits tests the printer.
PARTS: tuple[int, ...] = (-3, -2, -1, 1, 2, 3)


def parameter(source: random.Random) -> algebra.Value:
    """One Gaussian rational, which is the field record 0009 fixes."""
    real = Fraction(source.choice(PARTS), source.choice(PARTS))
    imaginary = Fraction(source.choice(PARTS), source.choice(PARTS))
    return algebra.add(
        algebra.from_fraction(real),
        algebra.multiply(algebra.imaginary_unit(), algebra.from_fraction(imaginary)),
    )


def generated(how_many: int = HOW_MANY) -> list[frame.Element]:
    """Elements, each a product of the three stages with drawn parameters."""
    source = random.Random(SEED)
    elements = []
    for _ in range(how_many):
        elements.append(
            frame.compose(
                frame.compose(
                    frame.null_rotation_about_l(parameter(source)),
                    frame.null_rotation_about_n(parameter(source)),
                ),
                frame.boost_and_spin(parameter(source)),
            )
        )
    return elements


class TheGroupLaws(unittest.TestCase):
    """Identity, inverses and associativity, over generated inputs."""

    def test_the_identity_acts_as_one_on_both_sides(self) -> None:
        for subject in generated():
            with self.subTest(element=frame.written(subject)):
                self.assertTrue(
                    frame.same(frame.compose(frame.identity(), subject), subject)
                )
                self.assertTrue(
                    frame.same(frame.compose(subject, frame.identity()), subject)
                )

    def test_an_element_times_its_inverse_is_the_identity(self) -> None:
        for subject in generated():
            with self.subTest(element=frame.written(subject)):
                self.assertTrue(
                    frame.same(
                        frame.compose(subject, frame.inverse(subject)),
                        frame.identity(),
                    )
                )
                self.assertTrue(
                    frame.same(
                        frame.compose(frame.inverse(subject), subject),
                        frame.identity(),
                    )
                )

    def test_composition_is_associative(self) -> None:
        elements = generated(4)
        for left, middle, right in itertools.islice(
            itertools.product(elements, repeat=3), 0, None, 9
        ):
            with self.subTest(left=frame.written(left)):
                self.assertTrue(
                    frame.same(
                        frame.compose(frame.compose(left, middle), right),
                        frame.compose(left, frame.compose(middle, right)),
                    )
                )

    def test_every_generated_element_has_determinant_one(self) -> None:
        for subject in generated():
            with self.subTest(element=frame.written(subject)):
                frame.element(*subject.entries)

    def test_an_element_outside_the_group_is_refused(self) -> None:
        """The fixture the generator cannot produce, and the reason it names."""
        with self.assertRaises(refusal.Refused) as refused:
            metrics.REFUSED[refusal.FRAME_ELEMENT_IS_NOT_UNIMODULAR]()
        self.assertEqual(
            refused.exception.reason, refusal.FRAME_ELEMENT_IS_NOT_UNIMODULAR
        )
        self.assertIn("2", refused.exception.detail)

    def test_a_boost_by_a_parameter_that_may_vanish_is_refused(self) -> None:
        """A scale the zero test did not decide is not a transformation."""
        with self.assertRaises(refusal.Refused) as refused:
            frame.boost_and_spin(algebra.free_function("h", (algebra.symbol("u"),)))
        self.assertEqual(
            refused.exception.reason, refusal.FRAME_ELEMENT_IS_NOT_UNIMODULAR
        )


class TheActionOnAFrame(unittest.TestCase):
    """What an element does to a tetrad, and that it is still a tetrad."""

    @classmethod
    def setUpClass(cls) -> None:
        # Once for the class rather than once per test: the curvature of a
        # geometry is the expensive thing here and none of these tests changes
        # it, so recomputing it three times would be paying for the same
        # arithmetic three times.
        cls.geometry = metrics.schwarzschild()
        cls.frame = curvature.tetrad_from_metric(cls.geometry)

    def test_the_transformed_frame_still_satisfies_the_conditions(self) -> None:
        """The whole reason the determinant is one, checked rather than argued."""
        for subject in generated(4):
            with self.subTest(element=frame.written(subject)):
                curvature.check(self.geometry, frame.act_on_tetrad(subject, self.frame))

    def test_the_identity_leaves_the_frame_where_it_was(self) -> None:
        moved = frame.act_on_tetrad(frame.identity(), self.frame)
        for name in conventions.LEGS:
            for left, right in zip(moved.leg(name), self.frame.leg(name), strict=True):
                self.assertTrue(algebra.is_zero(algebra.subtract(left, right)))

    def test_composing_two_elements_equals_acting_twice(self) -> None:
        for left, right in itertools.islice(
            itertools.product(generated(2), repeat=2), 0, None, 2
        ):
            with self.subTest(left=frame.written(left)):
                once = frame.act_on_tetrad(frame.compose(left, right), self.frame)
                twice = frame.act_on_tetrad(
                    left, frame.act_on_tetrad(right, self.frame)
                )
                for name in conventions.LEGS:
                    for one, other in zip(once.leg(name), twice.leg(name), strict=True):
                        self.assertTrue(
                            algebra.is_zero(algebra.subtract(one, other)),
                            f"{name}: {algebra.text(one)} against "
                            f"{algebra.text(other)}",
                        )


class TheActionOnCurvature(unittest.TestCase):
    """The same transformation, on the components rather than on the legs."""

    @classmethod
    def setUpClass(cls) -> None:
        # See the note above: the curvature is computed once for the class.
        cls.geometry = metrics.schwarzschild()
        cls.frame = curvature.tetrad_from_metric(cls.geometry)
        cls.tensor = curvature.lowered(cls.geometry, curvature.riemann(cls.geometry))
        cls.components = curvature.frame_components(cls.geometry, cls.tensor, cls.frame)

    def test_acting_on_the_components_is_reading_them_in_the_moved_frame(self) -> None:
        """The two routes to the same numbers, which is what ties this to #44.

        One route transforms the components by the group element. The other
        moves the frame and computes the components again from the curvature.
        They agree or one of them is wrong, and the cheap one is the one the
        algorithm will run many times per order.
        """
        for subject in generated(1):
            with self.subTest(element=frame.written(subject)):
                moved = frame.act_on_components(subject, self.components)
                recomputed = curvature.frame_components(
                    self.geometry,
                    self.tensor,
                    frame.act_on_tetrad(subject, self.frame),
                )
                for names, value in recomputed.items():
                    self.assertTrue(
                        algebra.is_zero(algebra.subtract(moved[names], value)),
                        f"{names}: {algebra.text(moved[names])} against "
                        f"{algebra.text(value)}",
                    )

    def test_composing_two_elements_equals_acting_twice(self) -> None:
        left, right = generated(2)
        once = frame.act_on_components(frame.compose(left, right), self.components)
        twice = frame.act_on_components(
            left, frame.act_on_components(right, self.components)
        )
        for names, value in once.items():
            self.assertTrue(
                algebra.is_zero(algebra.subtract(value, twice[names])),
                f"{names}: {algebra.text(value)} against {algebra.text(twice[names])}",
            )

    def test_the_boost_and_spin_leave_a_type_d_scalar_where_it_was(self) -> None:
        """Why the remaining freedom is a subgroup: this element changes nothing.

        A boost and a spin with a parameter of unit modulus is the isotropy the
        Schwarzschild exterior leaves at order zero, and the component that
        carries its curvature is unmoved by it. A null rotation about ``l`` is
        outside that subgroup, and it moves a component that was zero: the
        repeated direction stays repeated and the frame stops being aligned with
        the second one.
        """
        unmoved = frame.boost_and_spin(algebra.imaginary_unit())
        component = ("l", "m", "mbar", "n")
        after = frame.act_on_components(unmoved, self.components)
        self.assertTrue(
            algebra.is_zero(
                algebra.subtract(after[component], self.components[component])
            )
        )
        moved = frame.act_on_components(
            frame.null_rotation_about_l(algebra.integer(1)), self.components
        )
        self.assertFalse(algebra.is_zero(moved[("n", "mbar", "n", "mbar")]))


class TheRemainingFreedom(unittest.TestCase):
    """A subgroup, with a dimension read off it rather than standing in for it."""

    def test_two_subgroups_of_the_same_dimension_are_not_the_same(self) -> None:
        """The test issue #48 asks for by name.

        A boost and a spin are each one direction, and so is each half of a null
        rotation. A termination test that compared dimensions would call these
        the same freedom and stop an order early.
        """
        boost = frame.Freedom(frozenset({"boost"}))
        spin = frame.Freedom(frozenset({"spin"}))
        self.assertEqual(boost.dimension, spin.dimension)
        self.assertNotEqual(boost, spin)
        self.assertTrue(boost.holds("boost"))
        self.assertFalse(boost.holds("spin"))

    def test_the_dimension_is_read_off_the_generators(self) -> None:
        self.assertEqual(frame.EVERYTHING.dimension, frame.DIMENSION)
        self.assertEqual(frame.EVERYTHING.dimension, 6)
        self.assertEqual(frame.BOOST_AND_SPIN.dimension, 2)

    def test_the_six_directions_are_the_three_stages_record_0002_names(self) -> None:
        self.assertEqual(len(frame.GENERATORS), 6)
        for stage, how_many in (
            ("null-rotation-about-l", 2),
            ("null-rotation-about-n", 2),
            ("boost", 1),
            ("spin", 1),
        ):
            self.assertEqual(
                len([one for one in frame.GENERATORS if one.startswith(stage)]),
                how_many,
            )

    def test_a_direction_outside_the_group_is_not_a_freedom(self) -> None:
        with self.assertRaises(AssertionError):
            frame.Freedom(frozenset({"translation"}))


class TheTieBreak(unittest.TestCase):
    """Record 0012, at the point where several frames are equally canonical."""

    def test_the_same_element_comes_back_whatever_order_they_arrive_in(self) -> None:
        candidates = tuple(generated(5))
        first = frame.preferred(candidates)
        second = frame.preferred(tuple(reversed(candidates)))
        self.assertEqual(frame.written(first), frame.written(second))

    def test_two_runs_agree(self) -> None:
        self.assertEqual(
            frame.written(frame.preferred(tuple(generated(5)))),
            frame.written(frame.preferred(tuple(generated(5)))),
        )

    def test_the_order_is_on_the_values_and_not_on_the_arrival(self) -> None:
        """A tie between two elements that differ only in one entry.

        The break is the written normal form, so the answer is a property of the
        elements. Nothing about how the candidates were scheduled reaches it,
        which is what record 0012 asks of anything the classification reads.
        """
        one = frame.null_rotation_about_l(algebra.integer(1))
        other = frame.null_rotation_about_l(algebra.integer(2))
        self.assertEqual(
            frame.written(frame.preferred((one, other))),
            frame.written(frame.preferred((other, one))),
        )


if __name__ == "__main__":
    unittest.main()
