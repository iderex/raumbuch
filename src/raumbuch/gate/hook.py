"""The leg named ``hook``: the pre-push hook execs the gate verb and nothing else.

The failure this prevents is the second procedure. A hook that grows one extra
line is a copy of the gate that nobody runs in the workflow, and the day the two
disagree the disagreement is discovered by whoever is pushing at the time. So the
hook carries the invocation and no logic of its own, and this leg refuses
anything more.

What the hook is for is a different question and this leg does not answer it.
Installing the hook is optional and it is not what stands behind a merge, which
``CONTRIBUTING.md`` says in the place a contributor reads.
"""

from __future__ import annotations

from pathlib import Path

from raumbuch import gate

HOOK = Path(".githooks/pre-push")
COMMAND = "exec python3 -m raumbuch gate"


def instructions(text: str) -> list[str]:
    """The lines of a shell file that do something.

    Blank lines carry nothing and a comment carries nothing to the shell. The
    shebang begins with a hash and is a comment by this reading, which is what
    lets the rule below be one line rather than one line and an exception.
    """
    stripped = (line.strip() for line in text.splitlines())
    return [line for line in stripped if line and not line.startswith("#")]


def run(root: Path) -> gate.Verdict:
    path = root / HOOK
    if not path.is_file():
        return gate.refused(
            f"{HOOK.as_posix()} is not in the tree, so the hook that would run the "
            "gate before a push does not exist"
        )
    body = instructions(path.read_text(encoding="utf-8"))
    if body != [COMMAND]:
        return gate.refused(
            f"{HOOK.as_posix()} runs something other than the gate verb alone. "
            f"Expected exactly one instruction, {COMMAND!r}; found {body!r}"
        )
    return gate.passed(
        f"{HOOK.as_posix()} execs {COMMAND!r} and carries no other instruction"
    )
