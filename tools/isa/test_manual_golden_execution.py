#!/usr/bin/env python3

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from manual_architecture import architecture_pages  # noqa: E402
from manual_golden_execution import (  # noqa: E402
    IMPLEMENTATION_SOURCES,
    SAIL_EXECUTE_SOURCE,
    golden_execution_pages,
    implementation_review,
)


class GoldenExecutionPagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(
            (ROOT / "isa/v0.59.2/linxisa-v0.59.2.json").read_text()
        )
        cls.registers = json.loads(
            (ROOT / "isa/v0.59/state/pto_system_registers.json").read_text()
        )
        cls.sources = {
            path: (ROOT / path).read_bytes() for path in IMPLEMENTATION_SOURCES.values()
        }
        from manual_v0592_edition import release_decoder

        cls.sail_decode = release_decoder()
        cls.sail_execute = (ROOT / SAIL_EXECUTE_SOURCE).read_bytes()
        cls.pages, cls.audit, cls.review = golden_execution_pages(
            "830fbdb53bccec889414b5673ffba31b0a08606d",
            cls.catalog,
            cls.registers,
            cls.sail_decode,
            cls.sail_execute,
        )

    def test_every_original_execution_state_system_and_model_key_was_reviewed(self):
        wanted = {
            p.key
            for p in architecture_pages()
            if p.collection in {"execution", "state", "system", "implementation"}
        }
        self.assertEqual(set(self.review), wanted)

    def test_retained_fall_forms_do_not_revive_futo_semantics(self):
        text = self.pages["arch-fixup.html"][1]
        self.assertEqual(text.count("<tr>"), 19)
        self.assertIn("扩展目标的译码与异常路由", text)
        self.assertIn("reserved-in-pto", text)
        self.assertNotIn("FUTO_ACRn", text)

    def test_extension_boundary_and_current_queues_are_distinct(self):
        xb = self.pages["arch-xb-block.html"][1]
        for literal in ("XB", "ESAVE", "ERCOV", "产生架构效果之前拒绝"):
            self.assertIn(literal, xb)
        queues = self.pages["arch-state-lgpr.html"][1]
        for literal in ("T#1", "U#1", "HL.QMT", "HL.QPUSH", "HL.QPOP"):
            self.assertIn(literal, queues)
        self.assertNotIn("RI0", queues)
        self.assertNotIn("MPAR", queues)

    def test_exception_pages_use_only_published_saved_state(self):
        text = "\n".join(
            self.pages[name][1]
            for name in ("arch-privilege-switch.html", "arch-exception-overview.html")
        )
        for literal in ("CORE_STATE", "EVBASE_ACRn", "BPC", "TPC", "BARG"):
            self.assertIn(literal, text)
        self.assertNotIn("FUTO", text)
        self.assertNotIn("CAC_TABLE", text)

    def test_obsolete_scope_does_not_remove_independently_consumed_state(self):
        self.assertNotIn("arch-obsolescence-boundary.html", self.pages)
        boundary = self.review["vgpr"]["evidence"]
        self.assertIn("未对这些队列另行作废弃决策", boundary)
        masks = self.pages["arch-tile-masks.html"][1]
        self.assertIn("显式谓词 Tile", masks)
        self.assertIn("tile-mgather-mask.html", masks)
        self.assertIn("tile-mscatter-mask.html", masks)

    def test_implementation_evidence_is_separate_from_golden_html(self):
        self.assertFalse(
            any(route.startswith("arch-implementation-") for route in self.pages)
        )
        records = implementation_review(
            "830fbdb53bccec889414b5673ffba31b0a08606d", self.sources
        )
        self.assertEqual(len(records), 12)
        self.assertEqual(
            records["implementation-brob"]["normative_scope"],
            "implementation-reference-only",
        )
        self.assertIn("尚未实现处理器异常", records["implementation-brob"]["summary"])

    def test_source_inventory_is_fail_closed(self):
        broken = dict(self.sources)
        broken.pop(next(iter(broken)))
        with self.assertRaisesRegex(ValueError, "source inventory"):
            implementation_review("x", broken)


if __name__ == "__main__":
    unittest.main()
