#!/usr/bin/env python3

import tempfile
from pathlib import Path
import unittest

try:
    from check_manual_detail_semantics import _reader, _reject, _require
except ModuleNotFoundError:
    from tools.isa.check_manual_detail_semantics import _reader, _reject, _require


class ManualDetailSemanticCheckTest(unittest.TestCase):
    def test_reader_uses_only_the_normal_chinese_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "op-x.html"
            page.write_text(
                "before<!-- authored:start --><p>当前 <code>32 位</code></p>"
                "<!-- authored:end -->after",
                encoding="utf-8",
            )
            text, fragment = _reader(page)
            self.assertEqual(text, "当前 32 位")
            self.assertIn("<code>32 位</code>", fragment)

    def test_require_and_reject_report_visible_contract_failures(self):
        errors = []
        _require(errors, "p.html", "逻辑右移", "逻辑右移", "Dst0")
        _reject(errors, "p.html", "循环左移", "循环左移", "旧表")
        self.assertEqual(
            errors,
            [
                "p.html: missing current semantic fact 'Dst0'",
                "p.html: stale or contradictory text '循环左移'",
            ],
        )

    def test_reader_fails_closed_on_missing_or_duplicate_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "op-x.html"
            page.write_text("plain", encoding="utf-8")
            with self.assertRaises(ValueError):
                _reader(page)
            page.write_text(
                "<!-- authored:start --><!-- authored:end -->" * 2,
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                _reader(page)


if __name__ == "__main__":
    unittest.main()
