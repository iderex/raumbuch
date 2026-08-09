"""The expression sub-language: what it reads, and what it refuses.

Three kinds of test are here and they answer three different questions.

What it reads. Every expression of the worked Schwarzschild record, taken out of
`docs/record-format.md` rather than copied, plus a corpus of metrics chosen for
the shapes an entry that exercises the classification would take. That is the
nearest available answer to the first bullet of issue #40, whose own subject,
the entries of milestones 8, does not exist yet.

What it refuses. One fixture per refusal reason, each asserting the reason
rather than only the fact of a refusal, because a parser refusing for the wrong
reason passes a test that only counts refusals. The escape shapes are here, and
each one stays in the tree as the proof.

What the document says. The closed lists, the declared relations and the refusal
vocabulary are in `docs/expression-language.md` and in
`src/raumbuch/expression.py`, and a test comparing the two is what stops one
moving without the other.
"""

from __future__ import annotations

import json
import re
import tomllib
import unittest
from pathlib import Path

from raumbuch import expression, refusal

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "expression-language.md"
RECORD_FORMAT = ROOT / "docs" / "record-format.md"

# Six metrics beside the worked record, written in this language. Each is here
# for a shape rather than for its own sake: rotation and a mixed component,
# charge, a cosmological constant, a hyperbolic slice, exponents that are
# parameters, and a wave whose profile is quadratic in two coordinates.
CORPUS: dict[str, tuple[str, ...]] = {
    "rotating vacuum, Boyer-Lindquist": (
        "-(1 - 2*M*r/(r^2 + a^2*cos(theta)^2))",
        "-2*M*a*r*sin(theta)^2/(r^2 + a^2*cos(theta)^2)",
        "(r^2 + a^2*cos(theta)^2)/(r^2 - 2*M*r + a^2)",
        "r^2 + a^2*cos(theta)^2",
        "(r^2 + a^2 + 2*M*a^2*r*sin(theta)^2/(r^2 + a^2*cos(theta)^2))*sin(theta)^2",
    ),
    "charged static": (
        "-(1 - 2*M/r + Q^2/r^2)",
        "1/(1 - 2*M/r + Q^2/r^2)",
        "r^2",
        "r^2*sin(theta)^2",
    ),
    "static with a cosmological constant": (
        "-(1 - 2*M/r - L*r^2/3)",
        "1/(1 - 2*M/r - L*r^2/3)",
        "r^2",
        "r^2*sin(theta)^2",
    ),
    "hyperbolic slicing": (
        "-1",
        "t^2",
        "t^2*sinh(chi)^2",
        "t^2*sinh(chi)^2*sin(theta)^2",
    ),
    "homogeneous anisotropic, exponents as parameters": (
        "-1",
        "exp(2*p1*log(t))",
        "exp(2*p2*log(t))",
        "exp(2*p3*log(t))",
    ),
    "plane wave": (
        "(x^2 - y^2)*cos(u)",
        "-1",
        "1",
        "1",
    ),
}

# Conditions, in the fields that hold one.
CONDITIONS: tuple[str, ...] = (
    "M > 0",
    "r > 2*M",
    "theta > 0",
    "theta < pi",
    "phi >= 0",
    "phi < 2*pi",
    "a != 0",
    "Q = 0",
    "M > 0 and Q^2 < M^2",
    "L <= 0",
)

# The shapes somebody worried about a downloaded catalogue asks about first.
# Every one of them is refused, and each stays here as the proof.
ESCAPES: dict[str, str] = {
    "r.__class__": refusal.UNKNOWN_CHARACTER,
    "sin(r)[0]": refusal.UNKNOWN_CHARACTER,
    'eval("1")': refusal.UNKNOWN_CHARACTER,
    "sin(r); import os": refusal.UNKNOWN_CHARACTER,
    "lambda: r": refusal.UNKNOWN_CHARACTER,
    '__import__("os")': refusal.UNKNOWN_CHARACTER,
    "__import__(r)": refusal.UNKNOWN_FUNCTION,
    "open(r)": refusal.UNKNOWN_FUNCTION,
}

# One fixture per reason, and the reason it must trigger. Nothing is asserted
# here about the message; the reason is what a caller branches on.
ONE_PER_REASON: dict[str, str] = {
    "   ": refusal.EMPTY_EXPRESSION,
    "r + \u0440": refusal.NON_ASCII_CHARACTER,
    "r @ 2": refusal.UNKNOWN_CHARACTER,
    "0.5*r": refusal.DECIMAL_LITERAL,
    "r**2": refusal.POWER_IS_CARET,
    "tanh2(r)": refusal.UNKNOWN_FUNCTION,
    "sin()": refusal.FUNCTION_TAKES_ONE_ARGUMENT,
    "r*sin": refusal.FUNCTION_NAME_WITHOUT_ARGUMENT,
    "r^(1/2)": refusal.NON_INTEGER_EXPONENT,
    "(1 - 2*M/r": refusal.UNCLOSED_PARENTHESIS,
    "r * / 2": refusal.UNEXPECTED_TOKEN,
    "r 2": refusal.TRAILING_INPUT,
    "r > 2*M": refusal.COMPARISON_IN_AN_EXPRESSION,
    # One bracket past the bound, and one digit past it. Both are written from
    # the constants rather than as literals, so the fixture follows the bound
    # if the bound ever moves and does not quietly stop testing it.
    "(" * (expression.MAX_NESTING + 1)
    + "1"
    + ")" * (expression.MAX_NESTING + 1): refusal.EXPRESSION_TOO_DEEP,
    "1" * (expression.MAX_DIGITS + 1): refusal.NUMBER_TOO_LONG,
}

# The same, for the two reasons that only a condition field can reach.
ONE_PER_REASON_IN_A_CONDITION: dict[str, str] = {
    "r": refusal.COMPARISON_EXPECTED,
    "0 < theta < pi": refusal.CHAINED_COMPARISON,
}

# A near miss for each: one plausible change away from the refused fixture, and
# accepted. A fixture that could not have been written correctly proves nothing
# about the rule that refused it.
NEAR_MISS: dict[str, str] = {
    "   ": "0",
    "r + \u0440": "r + p",
    "r @ 2": "r * 2",
    "0.5*r": "1/2*r",
    "r**2": "r^2",
    "tanh2(r)": "tanh(r)",
    "sin()": "sin(r)",
    "r*sin": "r*sin(r)",
    "r^(1/2)": "r^(2)",
    "(1 - 2*M/r": "(1 - 2*M/r)",
    "r * / 2": "r / 2",
    "r 2": "r*2",
    "r > 2*M": "r - 2*M",
    # The near miss of each bound is the bound itself, which is the strongest
    # one available: the refused fixture and the accepted one are a single
    # bracket and a single digit apart, so an off-by-one in either direction
    # reddens one of the two.
    "(" * (expression.MAX_NESTING + 1) + "1" + ")" * (expression.MAX_NESTING + 1): "("
    * expression.MAX_NESTING
    + "1"
    + ")" * expression.MAX_NESTING,
    "1" * (expression.MAX_DIGITS + 1): "1" * expression.MAX_DIGITS,
}

NEAR_MISS_IN_A_CONDITION: dict[str, str] = {
    "r": "r > 0",
    "0 < theta < pi": "0 < theta",
}


def cells(heading: str, column: int = 0) -> list[str]:
    """The backticked cell of every table row under a heading of the document.

    The section runs to the next heading at the same level, so a subsection
    inside it is read and the section after it is not.
    """
    text = DOCUMENT.read_text(encoding="utf-8")
    start = text.index(f"\n## {heading}\n")
    rest = text[start + 1 :]
    following = rest.find("\n## ")
    section = rest if following == -1 else rest[:following]
    found = []
    for line in section.splitlines():
        if not line.startswith("|") or set(line) <= set("| -"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        matched = re.fullmatch(r"`(.+)`", parts[column])
        if matched is not None:
            found.append(matched.group(1))
    return found


def schwarzschild() -> dict:
    """The worked record, read out of the document that carries it.

    Copying it here would make this suite pass against a record nobody has
    written, and the point of the first bullet of issue #40 is that the grammar
    reads the records this project actually holds.
    """
    text = RECORD_FORMAT.read_text(encoding="utf-8")
    start = text.index("```toml")
    return tomllib.loads(text[start + len("```toml") : text.index("```", start + 3)])


class WhatItReads(unittest.TestCase):
    def test_every_metric_component_of_the_worked_record(self) -> None:
        components = [
            component["value"]
            for chart in schwarzschild()["chart"]
            for component in chart["metric"]
        ]
        self.assertEqual(len(components), 4)
        for value in components:
            with self.subTest(value=value):
                self.assertIsNotNone(expression.parse(value))

    def test_every_condition_of_the_worked_record(self) -> None:
        record = schwarzschild()
        conditions = [
            *(condition for chart in record["chart"] for condition in chart["range"]),
            *(stratum["condition"] for stratum in record["stratum"]),
            *(parameter["range"] for parameter in record["parameter"]),
        ]
        self.assertEqual(len(conditions), 7)
        for condition in conditions:
            with self.subTest(condition=condition):
                self.assertIsNotNone(expression.parse_condition(condition))

    def test_the_corpus_of_metrics_chosen_for_their_shapes(self) -> None:
        for name, components in CORPUS.items():
            for value in components:
                with self.subTest(metric=name, value=value):
                    self.assertIsNotNone(expression.parse(value))

    def test_the_conditions_a_stratum_and_a_range_are_written_with(self) -> None:
        for condition in CONDITIONS:
            with self.subTest(condition=condition):
                self.assertIsNotNone(expression.parse_condition(condition))

    def test_a_rational_literal_is_a_quotient_and_is_exact(self) -> None:
        node = expression.parse("1/2")
        self.assertEqual(node.operator, "/")
        self.assertEqual(node.left.value, 1)
        self.assertEqual(node.right.value, 2)

    def test_a_power_binds_tighter_than_a_product(self) -> None:
        node = expression.parse("r^2*sin(theta)^2")
        self.assertEqual(node.operator, "*")
        self.assertEqual(node.left, expression.Power(expression.Name("r"), 2))

    def test_a_negative_exponent_is_admitted(self) -> None:
        self.assertEqual(
            expression.parse("r^(-1)"), expression.Power(expression.Name("r"), -1)
        )

    def test_the_names_used_are_handed_up_for_the_loader_to_judge(self) -> None:
        node = expression.parse("r^2*sin(theta)^2 + M/pi")
        self.assertEqual(expression.names(node), frozenset({"r", "theta", "M", "pi"}))

    def test_the_names_of_a_condition_are_handed_up_too(self) -> None:
        node = expression.parse_condition("M > 0 and Q^2 < M^2")
        self.assertEqual(expression.names(node), frozenset({"M", "Q"}))

    def test_the_functions_applied_are_handed_up(self) -> None:
        node = expression.parse("exp(2*p*log(t))")
        self.assertEqual(expression.functions(node), frozenset({"exp", "log"}))


class WhatItRefuses(unittest.TestCase):
    def test_one_fixture_per_reason_triggers_exactly_that_reason(self) -> None:
        for text, reason in ONE_PER_REASON.items():
            with self.subTest(text=text):
                with self.assertRaises(refusal.Refused) as refused:
                    expression.parse(text)
                self.assertEqual(refused.exception.reason, reason)

    def test_the_two_reasons_only_a_condition_can_reach(self) -> None:
        for text, reason in ONE_PER_REASON_IN_A_CONDITION.items():
            with self.subTest(text=text):
                with self.assertRaises(refusal.Refused) as refused:
                    expression.parse_condition(text)
                self.assertEqual(refused.exception.reason, reason)

    def test_every_declared_reason_has_a_fixture(self) -> None:
        covered = set(ONE_PER_REASON.values()) | set(
            ONE_PER_REASON_IN_A_CONDITION.values()
        )
        self.assertEqual(covered, set(refusal.PARSER_REASONS))

    def test_each_refused_fixture_has_a_near_miss_that_is_accepted(self) -> None:
        self.assertEqual(set(NEAR_MISS), set(ONE_PER_REASON))
        for refused_text, accepted in NEAR_MISS.items():
            with self.subTest(refused=refused_text, accepted=accepted):
                self.assertIsNotNone(expression.parse(accepted))

    def test_the_near_miss_of_each_condition_fixture_is_accepted(self) -> None:
        self.assertEqual(
            set(NEAR_MISS_IN_A_CONDITION), set(ONE_PER_REASON_IN_A_CONDITION)
        )
        for accepted in NEAR_MISS_IN_A_CONDITION.values():
            with self.subTest(accepted=accepted):
                self.assertIsNotNone(expression.parse_condition(accepted))

    def test_every_escape_shape_is_refused(self) -> None:
        for text, reason in ESCAPES.items():
            with self.subTest(text=text):
                with self.assertRaises(refusal.Refused) as refused:
                    expression.parse(text)
                self.assertEqual(refused.exception.reason, reason)

    def test_a_condition_field_refuses_an_escape_too(self) -> None:
        with self.assertRaises(refusal.Refused) as refused:
            expression.parse_condition('eval("1") > 0')
        self.assertEqual(refused.exception.reason, refusal.UNKNOWN_CHARACTER)

    def test_a_refusal_says_where_it_happened(self) -> None:
        with self.assertRaises(refusal.Refused) as refused:
            expression.parse("r + 0.5")
        self.assertEqual(refused.exception.where, 5)
        self.assertIn("decimal-literal", str(refused.exception))

    def test_a_reason_outside_the_vocabulary_is_a_defect_and_not_a_refusal(
        self,
    ) -> None:
        with self.assertRaises(AssertionError):
            refusal.refuse("not-a-declared-reason", "invented at a call site")


class TheDocumentAndTheCodeSayTheSameThing(unittest.TestCase):
    def test_the_constant_list(self) -> None:
        self.assertEqual(cells("The closed constant list"), list(expression.CONSTANTS))

    def test_the_function_list(self) -> None:
        written = cells("The closed function list")
        self.assertEqual(
            sorted(name.removesuffix("(u)") for name in written),
            sorted(expression.FUNCTIONS),
        )
        self.assertEqual(len(written), len(expression.FUNCTIONS))

    def test_the_normal_form_functions_are_the_first_table(self) -> None:
        written = [
            name.removesuffix("(u)") for name in cells("The closed function list")
        ]
        first = written[: len(expression.NORMAL_FORM_FUNCTIONS)]
        self.assertEqual(sorted(first), sorted(expression.NORMAL_FORM_FUNCTIONS))
        self.assertEqual(
            sorted(written[len(first) :]), sorted(expression.DERIVED_FUNCTIONS)
        )

    def test_every_derivative_names_only_admitted_functions(self) -> None:
        """Closure under differentiation, as record 0009 requires it.

        The derivative column of the document is the argument. This asserts what
        a reader would otherwise have to check by eye: that no derivative
        reaches for a function the list does not carry, which is the one way the
        list stops being closed.
        """
        derivatives = cells("The closed function list", column=1)
        self.assertEqual(len(derivatives), len(expression.FUNCTIONS))
        for derivative in derivatives:
            with self.subTest(derivative=derivative):
                applied = set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\(", derivative))
                self.assertLessEqual(applied, set(expression.FUNCTIONS))

    def test_the_declared_relations(self) -> None:
        self.assertEqual(
            cells("The declared relations"),
            [statement for statement, _ in expression.RELATIONS],
        )

    def test_the_refusal_vocabulary(self) -> None:
        self.assertEqual(
            sorted(cells("What the parser refuses, by name")),
            sorted(refusal.PARSER_REASONS),
        )

    def test_the_escape_table(self) -> None:
        written = cells("Escapes, and what refuses each one")
        self.assertEqual(sorted(written), sorted(ESCAPES))

    def test_the_name_production_is_the_pattern_the_schema_fixes(self) -> None:
        """One pattern for a declaration and a use, and this is where it is one.

        The document says the name production is the schema's identifier
        pattern character for character. If the schema moves, this reddens
        rather than the two quietly diverging.
        """
        schema = json.loads(
            (ROOT / "schema" / "record-1.schema.json").read_text(encoding="utf-8")
        )
        pattern = schema["$defs"]["identifier"]["pattern"]
        self.assertEqual(pattern, "^[A-Za-z_][A-Za-z0-9_]*$")
        for name in ("M", "_x", "theta", "x2"):
            with self.subTest(name=name):
                self.assertIsNotNone(re.fullmatch(pattern[1:-1], name))
                self.assertEqual(expression.parse(name), expression.Name(name))


class NothingHereReachesAnAlgebraSystem(unittest.TestCase):
    """The negative record 0001 asks for, at the granularity a test can hold.

    This is the weaker half of the proof and it says so. It shows that the two
    modules of this milestone name no algebra layer today. That nothing may be
    added tomorrow is the module boundary of record 0001, and the grep over the
    whole tree is in the pull request body where a reader sees the command.
    """

    def test_neither_module_names_the_algebra_layer_or_an_evaluator(self) -> None:
        forbidden = ("sympy", "eval(", "exec(", "__import__", "pickle")
        for module in ("expression.py", "refusal.py"):
            source = (ROOT / "src" / "raumbuch" / module).read_text(encoding="utf-8")
            for name in forbidden:
                with self.subTest(module=module, name=name):
                    self.assertNotIn(name, source)


if __name__ == "__main__":
    unittest.main()
