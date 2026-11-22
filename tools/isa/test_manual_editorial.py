import os
import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

import manual_editorial as module


class EditorialTests(unittest.TestCase):
    def setUp(self):
        module.edit_article.cache_clear()
        self.addCleanup(module.edit_article.cache_clear)

    def test_protected_areas_stay_literal(self):
        old = "忽略算数溢出"
        parts = [
            f"# {old}",
            f"| {old} |",
            f"`{old}`",
            f"[原文]({old})",
            f"```asm\n; {old}\n```",
            f"    {old}",
        ]
        text = "\n".join(parts) + "\n" + old
        with patch.object(module, "tagged_bytes", return_value=text.encode()):
            result, hits = module.edit_article("docs/zh/isa/test.md")
        self.assertEqual(result, "\n".join(parts) + "\n忽略算术溢出")
        self.assertEqual(dict(hits), {"arithmetic-typo": 1})

    def test_order_and_register_bounds_remain(self):
        result, hits = module.edit_article("docs/zh/isa/inst/misa_c/C.MOVR.md")
        self.assertIn("将源寄存器值移动到目的寄存器中。", result)
        self.assertIn("R0-R23", result)
        self.assertIn("1-4", result)
        self.assertTrue(dict(hits)["source-range"])
        original = module.tagged_bytes("docs/zh/isa/inst/misa_c/C.MOVR.md").decode()
        import re

        self.assertEqual(
            re.findall(r"```.*?```", original, re.S),
            re.findall(r"```.*?```", result, re.S),
        )

    def test_source_specific_edits(self):
        rule = next(r for r in module.EDITS if r.key == "branch-lead")
        with patch.object(module, "tagged_bytes", return_value=rule.before.encode()):
            self.assertEqual(
                module.edit_article("docs/zh/isa/inst/unrelated.md"), (rule.before, ())
            )
            self.assertEqual(module.edit_article(rule.source)[0], rule.after)

    @unittest.skipUnless(
        os.getenv("HUMANIZER_ZH_ROOT"), "optional pinned upstream checkout"
    )
    def test_pinned_editorial_workflow(self):
        skill = Path(os.environ["HUMANIZER_ZH_ROOT"]) / "SKILL.md"
        self.assertEqual(
            hashlib.sha256(skill.read_bytes()).hexdigest(), module.SKILL_SHA256
        )


if __name__ == "__main__":
    unittest.main()
