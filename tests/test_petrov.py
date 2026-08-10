"""The Petrov type, against published classifications and against the patterns.

Two kinds of fixture, and each answers something the other cannot.

A scalar set written down here is a multiplicity pattern chosen in advance: the
quartic is built from roots whose multiplicities are known before anything runs,
so the six types are all reachable and each one is exercised by a polynomial
somebody can check by eye. What such a fixture cannot say is whether the scalars
of a real geometry ever reach the classifier in the shape it expects.

A geometry, classified through the curvature of issue #44, answers that and
carries a published type: the Schwarzschild exterior is type D and a pp-wave is
type N, and both are in the literature rather than in this file.
"""

from __future__ import annotations

import unittest
from fractions import Fraction

import metrics

from raumbuch import algebra, petrov, refusal


def value(number: Fraction | int) -> algebra.Value:
    return algebra.from_fraction(Fraction(number))


def scalars(*numbers: Fraction | int) -> tuple[algebra.Value, ...]:
    """``Psi_0`` to ``Psi_4`` as rationals, which is a quartic written by hand."""
    return tuple(value(number) for number in numbers)


class ThePublishedTypes(unittest.TestCase):
    """Two geometries whose type is in the literature, through the curvature."""

    def test_the_schwarzschild_exterior_is_type_d(self) -> None:
        classification = petrov.classify(metrics.weyl_scalars(metrics.schwarzschild()))
        self.assertEqual(classification.generic_type, "D")

    def test_a_plane_wave_is_type_n(self) -> None:
        subject = metrics.plane_wave(metrics.standing_profile())
        classification = petrov.classify(metrics.weyl_scalars(subject))
        self.assertEqual(classification.generic_type, "N")

    def test_the_schwarzschild_case_split_is_the_mass(self) -> None:
        """The type depends on a parameter, and the answer says so.

        Away from a vanishing mass the exterior is type D; where the mass
        vanishes there is no curvature and the type is O. Whether that locus is
        inside the record's declared range is not this module's question:
        record 0005 attaches a value to a stratum, and the caller is what
        intersects a case with the range a parameter declares.
        """
        classification = petrov.classify(metrics.weyl_scalars(metrics.schwarzschild()))
        self.assertEqual(classification.types, ("D", "O"))
        degenerate = classification.cases[1]
        self.assertFalse(degenerate.generic)
        self.assertEqual(len(degenerate.conditions), 1)
        self.assertIn("M", str(degenerate.conditions[0]))
        self.assertTrue(degenerate.conditions[0].vanishes)


class TheSixTypes(unittest.TestCase):
    """One quartic per pattern, written from its roots."""

    def test_four_distinct_roots_are_type_one(self) -> None:
        # z^4 + 1, whose four roots are distinct.
        self.assertEqual(petrov.classify(scalars(1, 0, 0, 0, 1)).generic_type, "I")

    def test_one_double_root_and_two_simple_ones_are_type_two(self) -> None:
        # z^2 * (z - 1) * (z - 2) = z^4 - 3z^3 + 2z^2.
        pattern = scalars(0, 0, Fraction(1, 3), Fraction(-3, 4), 1)
        self.assertEqual(petrov.classify(pattern).generic_type, "II")

    def test_two_double_roots_are_type_d(self) -> None:
        # z^2 * (z - 1)^2 = z^4 - 2z^3 + z^2.
        pattern = scalars(0, 0, Fraction(1, 6), Fraction(-1, 2), 1)
        self.assertEqual(petrov.classify(pattern).generic_type, "D")

    def test_a_triple_root_and_a_simple_one_are_type_three(self) -> None:
        # z^3 * (z - 1) = z^4 - z^3.
        self.assertEqual(
            petrov.classify(scalars(0, 0, 0, Fraction(-1, 4), 1)).generic_type, "III"
        )

    def test_a_quadruple_root_is_type_n(self) -> None:
        # z^4.
        self.assertEqual(petrov.classify(scalars(0, 0, 0, 0, 1)).generic_type, "N")

    def test_a_vanishing_quartic_is_type_o(self) -> None:
        self.assertEqual(petrov.classify(scalars(0, 0, 0, 0, 0)).generic_type, "O")


class TheRootAtInfinity(unittest.TestCase):
    """A degree that dropped is roots that went somewhere, not roots that went."""

    def test_a_quartic_with_no_leading_term_keeps_its_four_roots(self) -> None:
        """Only ``Psi_0``, so every root is at infinity and the type is N.

        Reading the degree off the length of a coefficient tuple would make this
        a constant with no roots at all, and a classifier with nothing to
        classify answers whatever its first branch says.
        """
        self.assertEqual(petrov.classify(scalars(1, 0, 0, 0, 0)).generic_type, "N")

    def test_two_roots_at_infinity_and_a_double_one_is_type_d(self) -> None:
        """Only ``Psi_2``, which is the shape a static black hole arrives in."""
        self.assertEqual(petrov.classify(scalars(0, 0, 1, 0, 0)).generic_type, "D")

    def test_one_root_at_infinity_is_counted_with_the_rest(self) -> None:
        # z^3 - z^2 = z^2 * (z - 1), with one root at infinity: pattern (2, 1, 1).
        pattern = scalars(0, 0, Fraction(-1, 6), Fraction(1, 4), 0)
        self.assertEqual(petrov.classify(pattern).generic_type, "II")


class TheCaseSplit(unittest.TestCase):
    """Where the type depends on a parameter, both cases come back."""

    def test_a_leading_coefficient_that_can_vanish_opens_a_case(self) -> None:
        """``Psi_0 = 1`` and ``Psi_4 = M``: four distinct roots, or none finite.

        Away from a vanishing ``M`` the quartic has four distinct roots and the
        type is I. Where ``M`` vanishes the quartic is a constant, every root is
        at infinity, and the type is N. Picking the first branch in silence is
        what this exists against.
        """
        given = (
            value(1),
            value(0),
            value(0),
            value(0),
            algebra.symbol("M"),
        )
        classification = petrov.classify(given)
        self.assertEqual(classification.types, ("I", "N"))
        self.assertTrue(classification.cases[0].generic)
        self.assertEqual(str(classification.cases[1].conditions[0]), "M = 0")

    def test_a_case_carries_the_conditions_it_rests_on(self) -> None:
        classification = petrov.classify(metrics.weyl_scalars(metrics.schwarzschild()))
        generic = classification.cases[0]
        self.assertTrue(generic.conditions)
        for condition in generic.conditions:
            self.assertFalse(condition.vanishes)

    def test_a_constant_coefficient_opens_no_case(self) -> None:
        """A number that is not zero vanishes nowhere, so there is nothing to split."""
        self.assertEqual(petrov.classify(scalars(0, 0, 0, 0, 1)).types, ("N",))


class TheUndecidedZeroTest(unittest.TestCase):
    """The third answer of record 0009, where a branch depends on it."""

    def test_a_free_function_is_refused_rather_than_guessed(self) -> None:
        given = (
            value(0),
            value(0),
            value(0),
            value(0),
            algebra.free_function("h", (algebra.symbol("u"),)),
        )
        with self.assertRaises(refusal.Refused) as refused:
            petrov.classify(given)
        self.assertEqual(refused.exception.reason, refusal.ZERO_TEST_UNDECIDED)

    def test_the_refusal_names_the_expression_it_could_not_decide(self) -> None:
        given = (
            value(0),
            value(0),
            value(0),
            value(0),
            algebra.free_function("h", (algebra.symbol("u"),)),
        )
        with self.assertRaises(refusal.Refused) as refused:
            petrov.classify(given)
        self.assertIn("h(u)", refused.exception.detail)

    def test_a_wave_carrying_a_free_amplitude_is_refused(self) -> None:
        """The same, reached through a geometry rather than through a scalar set.

        Whether a free function is the zero function is not decidable in the
        alphabet record 0009 declares, and it is the difference between a plane
        wave and flat space. So the wave with a free amplitude is refused where
        the one with a written amplitude is type N.
        """
        subject = metrics.plane_wave(metrics.harmonic_profile())
        with self.assertRaises(refusal.Refused) as refused:
            petrov.classify(metrics.weyl_scalars(subject))
        self.assertEqual(refused.exception.reason, refusal.ZERO_TEST_UNDECIDED)


class TheQuartic(unittest.TestCase):
    """The weights record 0002 writes, and what a dropped one would do."""

    def test_the_binomial_weights_are_the_ones_record_0002_writes(self) -> None:
        self.assertEqual(petrov.WEIGHTS, (1, 4, 6, 4, 1))

    def test_dropping_the_weights_changes_the_answer(self) -> None:
        """The mistake this catches is writing the polynomial's coefficients in.

        ``z^2*(z - 1)^2`` has coefficients ``1, -2, 1`` on ``z^2, z^3, z^4``, and
        the scalars that produce it are those divided by the weights: ``1/6``,
        ``-1/2``, ``1``. Somebody who passes the coefficients themselves gets a
        different polynomial, ``z^4 - 8*z^3 + 6*z^2``, whose roots are a double
        one and two simple ones. So the first is type D and the second is not,
        and a dropped weight is a type that is wrong and looks ordinary.
        """
        weighted = petrov.classify(scalars(0, 0, Fraction(1, 6), Fraction(-1, 2), 1))
        self.assertEqual(weighted.generic_type, "D")
        coefficients = petrov.classify(scalars(0, 0, 1, -2, 1))
        self.assertEqual(coefficients.generic_type, "II")


if __name__ == "__main__":
    unittest.main()
