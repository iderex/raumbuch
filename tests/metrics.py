"""The metrics the curvature is checked against, and what is published about them.

Four of different character, which is what issue #44 asks for: the Schwarzschild
exterior, one with a cosmological constant, one that is not static, and one
carrying a plane wave. The first is read from the worked record this repository
already holds, so the route a real entry takes is the route the first fixture
takes. The other three are built through the arithmetic interface directly,
because two of them carry a free function of the coordinates and the sub-language
of record 0003 has no syntax for one, which `docs/expression-language.md` already
says of itself.

Each entry carries what is published about it, in the comment above it, and the
test beside this file is where the comparison happens. A metric written here
with no published statement about it would be a fixture proving that the code
agrees with itself.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from raumbuch import algebra, curvature, petrov, record, refusal

ROOT = Path(__file__).resolve().parents[1]
RECORD_FORMAT = ROOT / "docs" / "record-format.md"


def schwarzschild() -> curvature.Geometry:
    """The worked record of `docs/record-format.md`, through the loader.

    ``ds^2 = -(1 - 2M/r) dt^2 + dr^2/(1 - 2M/r) + r^2 dtheta^2
    + r^2 sin(theta)^2 dphi^2``
    """
    loaded = record.loads(_worked_record(), "schwarzschild")
    return curvature.from_chart(loaded.charts[0])


def kottler() -> curvature.Geometry:
    """Schwarzschild with a cosmological constant, also called Kottler.

    ``f = 1 - 2M/r - Lambda_cc*r^2/3``, and the rest of the line element as
    Schwarzschild's. Published: it solves the field equations of record 0002
    with ``T_ab = 0`` and a non-zero ``Lambda_cc``, which makes ``R_ab =
    Lambda_cc*g_ab`` and ``R = 4*Lambda_cc``. That is the statement a vacuum
    entry cannot make, and record 0002 asks for one because a vacuum entry
    cannot detect a curvature sign convention applied backwards.

    The name of the constant is record 0002's. ``Lambda`` is already the trace
    part of the Ricci scalars in the Newman-Penrose formalism, so the record
    spells the cosmological constant out and so does this.
    """
    mass, radius, constant = (algebra.symbol(name) for name in ("M", "r", "Lambda_cc"))
    profile = algebra.subtract(
        algebra.subtract(
            algebra.integer(1),
            algebra.divide(algebra.multiply(algebra.integer(2), mass), radius),
        ),
        algebra.divide(
            algebra.multiply(constant, algebra.power(radius, 2)), algebra.integer(3)
        ),
    )
    return _spherical(profile)


def flrw() -> curvature.Geometry:
    """A flat Friedmann geometry with a free scale factor, which is not static.

    ``ds^2 = -dt^2 + a(t)^2 (dx^2 + dy^2 + dz^2)``. Published, and what the test
    compares against: the connection has ``Gamma^t_ij = a*a'`` on the diagonal
    and ``Gamma^i_tj = a'/a``, and nothing else; the Ricci tensor has
    ``R_tt = -3*a''/a`` and ``R_ij = (a*a'' + 2*a'^2)`` on the diagonal; and the
    Einstein tensor's ``tt`` component is ``3*(a'/a)^2``, which is the first
    Friedmann equation with ``8*pi*rho`` on the other side.
    """
    time = algebra.symbol("t")
    scale = algebra.free_function("a", (time,))
    squared = algebra.power(scale, 2)
    return curvature.geometry(
        ("t", "x", "y", "z"),
        {
            ("t", "t"): algebra.integer(-1),
            ("x", "x"): squared,
            ("y", "y"): squared,
            ("z", "z"): squared,
        },
    )


def plane_wave(profile: algebra.Value) -> curvature.Geometry:
    """A pp-wave in Brinkmann coordinates, carrying the profile it is given.

    ``ds^2 = H(u,x,y) du^2 - 2 du dv + dx^2 + dy^2``. Published: the only
    non-vanishing Ricci component is ``R_uu``, and it vanishes exactly when the
    profile is harmonic in the two transverse coordinates. So a profile with
    ``H_xx + H_yy = 0`` is a vacuum plane wave and one without it is a null
    fluid, and which of the two a fixture is can be read off the profile before
    anything is computed.
    """
    return curvature.geometry(
        ("u", "v", "x", "y"),
        {
            ("u", "u"): profile,
            ("u", "v"): algebra.integer(-1),
            ("x", "x"): algebra.integer(1),
            ("y", "y"): algebra.integer(1),
        },
    )


def harmonic_profile() -> algebra.Value:
    """``h(u)*(x^2 - y^2)``, which is harmonic across the wave front."""
    return _profile(algebra.subtract)


def unharmonic_profile() -> algebra.Value:
    """``h(u)*(x^2 + y^2)``, which is not, so the wave carries a null fluid."""
    return _profile(algebra.add)


def standing_profile() -> algebra.Value:
    """``x^2 - y^2``, harmonic and carrying no free function.

    The two profiles above carry ``h(u)``, and whether a free function is the
    zero function is not decidable in the alphabet record 0009 declares, so a
    classification of a wave carrying one is refused rather than guessed. This
    profile is the same geometry with the amplitude written down, which is what
    a fixture about the type rather than about the refusal needs.
    """
    return algebra.subtract(
        algebra.power(algebra.symbol("x"), 2), algebra.power(algebra.symbol("y"), 2)
    )


def weyl_scalars(subject: curvature.Geometry) -> tuple[algebra.Value, ...]:
    """``Psi_0`` to ``Psi_4`` for a **vacuum** geometry, read off the frame Riemann.

    In vacuum the Weyl tensor is the Riemann tensor, so the five scalars are
    five frame components and no trace has to be removed. That is the whole
    reason this is here rather than in the module: the general extraction needs
    the Ricci part, which is issue #45, and a second implementation of it inside
    a test would be the thing that disagrees with the first.

    **Nothing here checks that the geometry is a vacuum.** The caller passes one
    that is, and the tests beside this file are where that is established.
    """
    tensor = curvature.lowered(subject, curvature.riemann(subject))
    frame = curvature.tetrad_from_metric(subject)
    components = curvature.frame_components(subject, tensor, frame)
    return (
        components[("l", "m", "l", "m")],
        components[("l", "n", "l", "m")],
        components[("l", "m", "mbar", "n")],
        components[("l", "n", "mbar", "n")],
        components[("n", "mbar", "n", "mbar")],
    )


def kerr_shape() -> curvature.Geometry:
    """The shape Boyer-Lindquist coordinates give Kerr: a metric off the blocks.

    Only the shape is needed, so the components are the ones that decide it and
    the rest are as Schwarzschild's. What this fixture is for is the boundary of
    the tetrad construction: a ``t phi`` component is outside the two-block
    split, so the construction refuses it and the legs have to be given rather
    than built. Nothing here claims to be the Kerr metric, and no curvature of
    it is compared against anything.
    """
    spin, radius, angle = (algebra.symbol(name) for name in ("a", "r", "theta"))
    base = _spherical(
        algebra.subtract(
            algebra.integer(1),
            algebra.divide(
                algebra.multiply(algebra.integer(2), algebra.symbol("M")), radius
            ),
        )
    )
    components = {
        ("t", "t"): base.component(0, 0),
        ("r", "r"): base.component(1, 1),
        ("theta", "theta"): base.component(2, 2),
        ("phi", "phi"): base.component(3, 3),
        ("t", "phi"): algebra.multiply(spin, algebra.applied("sin", angle)),
    }
    return curvature.geometry(("t", "r", "theta", "phi"), components)


def unrooted() -> curvature.Geometry:
    """A metric whose transverse block has no square root in the field.

    ``r`` in place of ``r^2`` on the transverse diagonal. It is a metric, it is
    not degenerate, and normalising a transverse leg needs the square root of
    ``r``, which record 0009's field does not hold. The one-character distance
    from the fixture above it is the point: this is the mistake somebody makes
    while writing a metric out, not a pathological object.
    """
    radius = algebra.symbol("r")
    angle = algebra.symbol("theta")
    return curvature.geometry(
        ("t", "r", "theta", "phi"),
        {
            ("t", "t"): algebra.integer(-1),
            ("r", "r"): algebra.integer(1),
            ("theta", "theta"): radius,
            ("phi", "phi"): algebra.multiply(
                radius, algebra.power(algebra.applied("sin", angle), 2)
            ),
        },
    )


def degenerate() -> curvature.Geometry:
    """A metric with a vanishing determinant, which has no inverse."""
    return curvature.geometry(
        ("t", "r", "theta", "phi"),
        {
            ("t", "t"): algebra.integer(-1),
            ("r", "r"): algebra.integer(1),
            ("theta", "theta"): algebra.integer(0),
            ("phi", "phi"): algebra.integer(1),
        },
    )


def _broken_tetrad() -> None:
    """The Schwarzschild legs with the transverse one scaled, which breaks it.

    One factor, and every other condition still holds. That is what makes it
    the mistake somebody makes rather than a pathological set of legs: a leg
    normalised against the wrong convention is off by a factor and by nothing
    else.
    """
    subject = schwarzschild()
    frame = curvature.tetrad_from_metric(subject)
    scaled = tuple(
        algebra.multiply(algebra.integer(2), part) for part in frame.leg("m")
    )
    curvature.tetrad(subject, (frame.leg("l"), frame.leg("n"), scaled))


#: One fixture per reason the arithmetic raises, which is the third corpus
#: beside the two that hold records. Every reason in the vocabulary of
#: :mod:`raumbuch.refusal` has a fixture in exactly one of the three, and
#: `tests/test_corpus.py` is where that union is compared against the
#: vocabulary so a reason cannot be added without one.
REFUSED: dict[str, Callable[[], None]] = {
    refusal.METRIC_IS_DEGENERATE: lambda: curvature.connection(degenerate()),
    refusal.FRAME_IS_NOT_BLOCK_PAIRED: lambda: curvature.tetrad_from_metric(
        kerr_shape()
    ),
    refusal.FRAME_CONSTRUCTION_LEAVES_THE_FIELD: lambda: curvature.tetrad_from_metric(
        unrooted()
    ),
    refusal.TETRAD_CONDITION_FAILS: _broken_tetrad,
    refusal.ZERO_TEST_UNDECIDED: lambda: petrov.classify(_free_amplitude()),
}


def _free_amplitude() -> tuple[algebra.Value, ...]:
    """A scalar set whose top scalar is a free function of one coordinate.

    Whether a free function is the zero function is not decidable in the
    alphabet record 0009 declares, and here it is the difference between a
    plane wave and flat space, so the classification refuses rather than
    branching on a test it did not decide.
    """
    return (
        algebra.integer(0),
        algebra.integer(0),
        algebra.integer(0),
        algebra.integer(0),
        algebra.free_function("h", (algebra.symbol("u"),)),
    )


def _spherical(profile: algebra.Value) -> curvature.Geometry:
    """The static spherically symmetric line element around one profile."""
    radius, angle = algebra.symbol("r"), algebra.symbol("theta")
    return curvature.geometry(
        ("t", "r", "theta", "phi"),
        {
            ("t", "t"): algebra.negate(profile),
            ("r", "r"): algebra.divide(algebra.integer(1), profile),
            ("theta", "theta"): algebra.power(radius, 2),
            ("phi", "phi"): algebra.multiply(
                algebra.power(radius, 2),
                algebra.power(algebra.applied("sin", angle), 2),
            ),
        },
    )


def _profile(combine) -> algebra.Value:
    front = algebra.free_function("h", (algebra.symbol("u"),))
    across = combine(
        algebra.power(algebra.symbol("x"), 2), algebra.power(algebra.symbol("y"), 2)
    )
    return algebra.multiply(front, across)


def _worked_record() -> bytes:
    """The record in `docs/record-format.md`, as its own bytes.

    Read out of the document rather than copied here, which is the same rule
    `tests/test_record.py` follows: a fixture copied out of a document is a
    second copy of it, and the two part on the day the document is corrected.
    """
    text = RECORD_FORMAT.read_text(encoding="utf-8")
    opened = text.index("```toml")
    body = text[text.index("\n", opened) + 1 :]
    return body[: body.index("```")].encode("utf-8")
