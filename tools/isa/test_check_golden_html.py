#!/usr/bin/env python3

import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_golden_html import (
    _check_audit_prose,
    _check_b_ior_contract,
    _check_orphans,
    _check_register_details,
    _check_ssr,
    history_hits,
)


class GoldenHTMLCheckTest(unittest.TestCase):
    def test_history_pattern_preserves_current_old_value_semantics(self):
        self.assertEqual(history_hits("op-casw.html", "比较并返回内存旧值。"), [])
        for text in (
            "查看历史说明",
            "保留旧版模型",
            "下方原页用于对照",
            "0.59.1 增补",
            "v0.58 编码说明",
            "This is a legacy instruction model.",
            "193 obsolete forms are removed",
        ):
            self.assertTrue(history_hits("page.html", text), text)

    def test_sources_allow_only_exact_upstream_identity(self):
        current = "PTO 标签 v0.59.1.0；ABI pto-isa-0.59.1-mode-function-v1。"
        self.assertEqual(history_hits("sources.html", current), [])
        self.assertTrue(history_hits("sources.html", current + "兼容旧机器字。"))

    def test_old_navigation_and_review_artifacts_are_not_golden(self):
        self.assertTrue(history_hits("arch-ssr.html", "系统寄存器原文"))
        self.assertTrue(history_hits("architecture.html", "实现模型补充"))

    def test_architecture_audit_rejects_historical_and_implementation_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "architecture-audit.json").write_text(
                json.dumps(
                    {
                        "arch-a.html": {
                            "status": "historical-register-note",
                            "source_path": "x",
                        },
                        "arch-b.html": {
                            "status": "implementation-only",
                            "source_path": "docs/zh/isa/model/BCC.md",
                        },
                    }
                )
            )
            errors: list[str] = []
            _check_audit_prose(site, errors)
            self.assertTrue(
                any("historical-register-note" in error for error in errors)
            )
            self.assertTrue(any("implementation tutorial" in error for error in errors))

    def test_ssr_table_cannot_link_historical_register_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "architecture-audit.json").write_text("{}")
            (site / "arch-ssr.html").write_text(
                '<table><tr><th>旧中文页</th><td><a href="arch-ssr-time.html">历史说明</a></td></tr></table>'
            )
            errors: list[str] = []
            _check_ssr(site, errors)
            self.assertGreaterEqual(len(errors), 2)

    def test_machine_generated_ssr_overview_is_current(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "architecture-audit.json").write_text(
                json.dumps(
                    {"arch-ssr-overview.html": {"origin": "v0.59.2-machine-projection"}}
                )
            )
            (site / "arch-ssr.html").write_text("<table></table>")
            (site / "arch-ssr-overview.html").write_text("current")
            errors: list[str] = []
            _check_ssr(site, errors)
            self.assertFalse(
                any(
                    "overview is not a current machine projection" in error
                    for error in errors
                )
            )

    def test_register_details_require_current_anchors_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "arch-ssr.html").write_text("<table></table>")
            errors: list[str] = []
            _check_register_details(site, errors)
            self.assertTrue(
                any("detail inventory differs" in error for error in errors)
            )
            self.assertIn("golden-ssr-evidence.json: missing", errors)

    def test_orphaned_downloadable_manuscript_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "article-source").mkdir()
            (site / "article-source/old.md").write_text("old")
            errors: list[str] = []
            _check_orphans(site, errors)
            self.assertEqual(
                errors, ["article-source/old.md: orphaned packaged artifact"]
            )

    def test_b_ior_accepts_range_descriptor_and_rejects_reserved_selectors(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            text = (
                "选择器 24 至 31 保留，并在读取或改变绑定状态之前引发 "
                "Fault_IllegalInstruction。RegSrc1 和 RegSrc2 分别提供 S64 "
                "MinIndex 和 MaxIndex 范围描述符；(RegSrc1, RegSrc2)=(zero, zero) 时"
                "表示不提供范围描述符。范围描述符与 GPR 掩码同时使用时，第二条 "
                "B.IOR 携带掩码，并只在最后一条记录设置 ExecMaskPresent。"
            )
            (site / "op-b-ior.html").write_text(text)
            errors: list[str] = []
            _check_b_ior_contract(site, errors)
            self.assertEqual(errors, [])

    def test_b_ior_old_constraint_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "op-b-ior.html").write_text(
                "带索引 TLSU 要求 RegSrc1、RegSrc2 与 RegDst 必须为零。"
                "记录仍会保存这些编码。"
            )
            errors: list[str] = []
            _check_b_ior_contract(site, errors)
            self.assertTrue(
                any("stores reserved selectors" in error for error in errors)
            )
            self.assertTrue(
                any("forbids every indexed descriptor" in error for error in errors)
            )


if __name__ == "__main__":
    unittest.main()
