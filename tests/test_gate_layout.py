"""The layout leg bites, and it bites for the reason it names.

Each fixture below violates exactly one thing, and the assertion is on what the
refusal says rather than only on the fact of one, because a leg that refuses for
the wrong reason passes a test that only counts refusals.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from raumbuch.gate import layout

ROOT = Path(__file__).resolve().parents[1]

BLOCK = """### The directory layout

Prose before the block.

```
src/raumbuch/            the package
tests/                   the unit suite
docs/                    documents, including docs/decisions/ and docs/checks.md
```

Prose after the block.
"""


class ReadingTheLayoutOutOfTheRecord(unittest.TestCase):
    def test_the_paths_are_the_first_token_of_each_line_of_the_block(self) -> None:
        self.assertEqual(
            layout.declared(BLOCK), ["src/raumbuch/", "tests/", "docs/"]
        )

    def test_prose_after_a_path_is_not_read_as_a_second_path(self) -> None:
        self.assertNotIn("docs/decisions/", layout.declared(BLOCK))

    def test_the_real_record_carries_a_layout(self) -> None:
        text = (ROOT / layout.RECORD).read_text(encoding="utf-8")
        paths = layout.declared(text)
        self.assertIn("src/raumbuch/", paths)
        self.assertIn(".githooks/", paths)


class TheLegRefuses(unittest.TestCase):
    def test_a_tree_missing_a_directory_the_record_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / layout.RECORD).parent.mkdir(parents=True)
            (root / layout.RECORD).write_text(BLOCK, encoding="utf-8")
            (root / "src/raumbuch").mkdir(parents=True)
            (root / "docs").mkdir(exist_ok=True)
            verdict = layout.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("tests/", verdict.detail)
        self.assertNotIn("src/raumbuch/", verdict.detail)

    def test_a_tree_with_no_record_0001_in_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verdict = layout.run(Path(directory))
        self.assertEqual(verdict.state, "refused")
        self.assertIn("record 0001", verdict.detail)

    def test_a_record_whose_layout_block_is_gone(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / layout.RECORD).parent.mkdir(parents=True)
            (root / layout.RECORD).write_text("# 0001. The means\n", encoding="utf-8")
            verdict = layout.run(root)
        self.assertEqual(verdict.state, "refused")
        self.assertIn("names no path", verdict.detail)


class TheLegPasses(unittest.TestCase):
    def test_on_this_tree(self) -> None:
        verdict = layout.run(ROOT)
        self.assertEqual(verdict.state, "passed", verdict.detail)
        self.assertIn("record 0001", verdict.detail)


if __name__ == "__main__":
    unittest.main()
