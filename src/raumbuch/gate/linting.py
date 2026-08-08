"""The leg named ``lint``: the rule set chosen in ``pyproject.toml`` is met.

It refuses rather than advises. The rule set is chosen there and not accumulated
here, every rule switched off is switched off beside its reason, and this leg
reads whatever that file says: a rule added or removed changes what this refuses
without a line changing here.
"""

from __future__ import annotations

from pathlib import Path

from raumbuch import gate
from raumbuch.gate import tool

ARGUMENTS = ["check", "--no-cache", "--output-format", "concise", "."]
SHOWN = 20


def run(root: Path) -> gate.Verdict:
    if not tool.installed():
        return gate.skipped(tool.absent("lints"))
    result = tool.invoke(root, ARGUMENTS)
    lines = tool.output(result)
    if result.returncode == 0:
        return gate.passed(
            "no finding against the rule set in pyproject.toml: "
            f"{lines[-1] if lines else 'nothing to report'}"
        )
    if result.returncode == 1:
        # The tool ends with its own count and, where a fix exists, an offer of
        # one. Neither is a finding, and counting them would report a number the
        # reader cannot match against the list underneath it.
        trailers = ("Found ", "[*] ")
        findings = [line for line in lines if not line.startswith(trailers)]
        rest = len(findings) - SHOWN
        shown = findings[:SHOWN]
        if rest > 0:
            shown.append(f"and {rest} more, which the tool prints in full")
        return gate.refused(
            f"{len(findings)} finding(s) against the rule set in pyproject.toml\n"
            + "\n".join(shown)
        )
    return gate.refused(
        "the linter could not judge this tree, so this leg fails closed rather "
        f"than reading a broken tool as a clean tree (exit {result.returncode})\n"
        + "\n".join(lines[-5:])
    )
