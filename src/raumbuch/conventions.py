"""Record 0002 in one place, so that flipping a convention is one edit.

The last line of issue #44's Done-when asks that every convention the curvature
module depends on is read from one place. This is that place. A sign here is not
a preference and not a default: each one is fixed by record 0002, and the
paragraph of that record it comes from is named beside it.

Why one module rather than a constant at each site. A sign convention applied in
two places and changed in one is a defect with no symptom, because the
components still look like curvature components and the classification they
produce is confidently wrong. Record 0002 says the same thing about transcribed
field equations and answers it by deriving them; this is the same answer for the
handful of signs that cannot be derived because they are choices.

What is here is what record 0002 fixes and what a module reads. What is not here
is anything a computation produces. There is no convention about the value of a
curvature component, only about which arrangement of indices and which sign the
definition carries.
"""

from __future__ import annotations

#: The metric signature, ``-+++``: one timelike direction with a minus sign,
#: three spacelike with a plus. Record 0002, under "Signature and
#: normalisation", and already in the ``signature`` field of every record.
SIGNATURE = "-+++"

#: The dimension this board supports, and the only one. Record 0002, under
#: "Four dimensions, and only four". The loader refuses a record declaring
#: another, which is :data:`raumbuch.record.DIMENSION`, and this is the same
#: number read by the arithmetic rather than by the loader.
DIMENSION = 4

#: The frame legs, in the order every stored component tuple is read in. Record
#: 0002 makes the order part of the decision rather than a detail of an
#: implementation: a component tuple written in one order and read in another is
#: a defect that survives every test whose fixture is symmetric.
LEGS: tuple[str, ...] = ("l", "n", "m", "mbar")

#: The one non-vanishing inner product among ``l`` and ``n``, and the one among
#: ``m`` and ``mbar``. Record 0002: ``l.n = -1`` and ``m.mbar = 1``, with every
#: other product among the four legs vanishing. This normalisation is **not**
#: the one the formalism was first published in, which is why the record writes
#: it twice and why the connection is derived here rather than transcribed.
L_DOT_N = -1
M_DOT_MBAR = 1

#: The sign of the Riemann tensor, as the Ricci identity of record 0002 fixes
#: it::
#:
#:     (Nabla_c Nabla_d - Nabla_d Nabla_c) V^a = R^a_bcd * V^b
#:
#: which gives, for the Levi-Civita connection,
#:
#:     R^a_bcd = d_c Gamma^a_db - d_d Gamma^a_cb
#:               + Gamma^a_ce Gamma^e_db - Gamma^a_de Gamma^e_cb
#:
#: The factor is written rather than folded into the formula so that the other
#: convention, which several published sources work in, is one edit here and no
#: edit anywhere else. A vacuum entry cannot tell the two apart, which is why
#: record 0002 asks issue #49 for an entry whose Ricci curvature does not
#: vanish and asks it to write down the sign it expects.
RIEMANN_SIGN = 1

#: Which two slots of ``R^a_bcd`` the Ricci tensor contracts: the first and the
#: third, so ``R_ab = R^c_acb``. Record 0002, under "Curvature signs". The
#: contraction itself is issue #45, which computes the components the algorithm
#: consumes; the convention it contracts under is here because a second copy of
#: it is the thing this module exists against.
RICCI_SLOTS: tuple[int, int] = (0, 2)
