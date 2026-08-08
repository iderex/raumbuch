"""The arithmetic boundary of record 0001, with nothing behind it yet.

Record 0001 put everything record 0009 makes load-bearing behind one interface
here, and said that nothing outside this directory constructs a SymPy object or
names a SymPy type. The operations that interface carries are fixed in that
record: reduce to a normal form, answer a zero test, evaluate at a rational point
modulo a prime, differentiate with respect to a declared symbol, take a greatest
common divisor and the subresultants of two polynomials, and apply the declared
rewrites of the closed function list.

None of them is declared here. This module is a placeholder holding the boundary
open, and an interface written before the first caller exists would fix a shape
against a guess. The issues of milestones 4 and 5 are where the operations and
their implementation land.
"""

from __future__ import annotations

__all__: tuple[str, ...] = ()
