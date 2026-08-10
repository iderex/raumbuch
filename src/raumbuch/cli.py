"""The command-line entry point, and the verbs of the program.

Record 0003 reserved ``raumbuch classify``, ``raumbuch curvature`` and
``raumbuch verify`` against the derived fields they recompute, and record 0001
made the gate one more verb of the same program. The gate and the release
artefacts exist here; the reserved three are built by their own issues and are
absent rather than stubbed, because a verb that answers nothing is worse than a
verb that is not there.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from raumbuch import gate, release


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(
        prog="raumbuch",
        description="A verified catalogue of exact solutions, and its checks.",
    )
    verbs = argument_parser.add_subparsers(dest="verb", required=True)
    gate_verb = verbs.add_parser(
        "gate",
        help="run every leg of the gate in order, stopping at the first refusal",
    )
    gate_verb.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="the checkout to judge, which defaults to the working directory",
    )
    gate_verb.add_argument(
        "--only",
        action="append",
        choices=[leg.name for leg in gate.LEGS],
        metavar="LEG",
        help=(
            "run this leg alone, repeatable. A leg nobody asked for is still "
            "reported, saying it was not asked for and what asking would cost, "
            "so a limited run cannot be read as a whole one"
        ),
    )
    gate_verb.add_argument(
        "--require",
        action="append",
        choices=[leg.name for leg in gate.LEGS],
        metavar="LEG",
        help=(
            "refuse if this leg does not run, repeatable. A run that exists to "
            "cover one leg says so, rather than reporting green over a set it "
            "did not cover"
        ),
    )
    release_verb = verbs.add_parser(
        "release",
        help=(
            "build the wheel, the sdist and the bill of materials twice, and "
            "refuse a byte that moved between the two builds"
        ),
    )
    release_verb.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="the checkout to build, which defaults to the working directory",
    )
    release_verb.add_argument(
        "--into",
        type=Path,
        default=Path("dist"),
        help=(
            "where the two builds are written, one subdirectory each. Two "
            "builds rather than one against a stored hash, which would be a "
            "number somebody has to update on every commit"
        ),
    )
    return argument_parser


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.verb == "gate":
        return gate.main(
            arguments.root, only=arguments.only, required=arguments.require
        )
    if arguments.verb == "release":
        return release.main(arguments.root, arguments.into)
    raise AssertionError(f"no such verb: {arguments.verb}")
