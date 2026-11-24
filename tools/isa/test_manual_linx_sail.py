#!/usr/bin/env python3

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from export_linxisa_v0591_sail import check as check_export
from export_linxisa_v0591_sail import export as export_sail
from manual_linx_sail import _release_decode, _sail_sources, sail_detail
from manual_tag import tagged_bytes, tagged_json

DATA = ROOT / "docs/architecture/isa-manual/reference/data/manual-linx-sail.json"


class ManualLinxSailTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
        cls.rows = [
            row for row in catalog["instructions"] if not row.get("pto_source_form_id")
        ]

    def test_exact_coverage_and_versioned_decoder_identity(self) -> None:
        self.assertEqual(
            self.data["coverage"],
            {
                "helper_forms": 19,
                "linx_only_forms": 23,
                "platform_dispatch_forms": 0,
                "trap_forms": 4,
                "unique_helpers": 7,
            },
        )
        decoder = _release_decode()
        with tempfile.TemporaryDirectory() as directory:
            exported = Path(directory) / "sail"
            package = export_sail(exported)
            check_export(exported)
            release_package = json.loads(
                (ROOT / "isa/v0.59/release_package.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                hashlib.sha256(decoder).hexdigest(),
                package["files"]["model/decode/decode.sail"],
            )
            self.assertEqual(
                package["files_sha256"], release_package["sail"]["files_sha256"]
            )
        self.assertEqual(
            self.data["decoder"]["sha256"], hashlib.sha256(decoder).hexdigest()
        )
        self.assertNotEqual(
            self.data["decoder"]["sha256"],
            hashlib.sha256(
                tagged_bytes("isa/sail/model/decode/decode.sail")
            ).hexdigest(),
        )

    def test_every_form_matches_exact_row_and_decode_excerpt(self) -> None:
        decoder_lines = _release_decode().decode("utf-8").splitlines(keepends=True)
        for row in self.rows:
            with self.subTest(form=row["id"]):
                evidence = self.data["forms"][row["id"]]
                self.assertEqual(evidence["mnemonic"], row["mnemonic"])
                self.assertEqual(evidence["asm"], row["asm"])
                self.assertEqual(evidence["catalog_note"], row.get("note", ""))
                self.assertEqual(evidence["catalog_source"], row["source"])
                self.assertEqual(evidence["encoding"], row["encoding"])
                decode = evidence["decode"]
                original = "".join(
                    decoder_lines[decode["line_start"] - 1 : decode["line_end"]]
                )
                self.assertEqual(original, decode["excerpt"])
                self.assertEqual(
                    hashlib.sha256(original.encode("utf-8")).hexdigest(),
                    decode["excerpt_sha256"],
                )
                detail = sail_detail(row)
                self.assertIn('class="linx-sail-evidence"', detail)
                self.assertIn("model/decode/decode.sail", detail)

    def test_helpers_are_exact_tagged_definitions_and_real_calls(self) -> None:
        exported = _sail_sources()
        for name, handler in self.data["handlers"].items():
            with self.subTest(helper=name):
                source = exported[handler["path"]]
                self.assertEqual(
                    hashlib.sha256(source).hexdigest(), handler["file_sha256"]
                )
                lines = source.decode("utf-8").splitlines(keepends=True)
                original = "".join(
                    lines[handler["line_start"] - 1 : handler["line_end"]]
                )
                self.assertEqual(original, handler["excerpt"])
                self.assertRegex(original, rf"(?m)^function\s+{re.escape(name)}\s*\(")
        for form in self.data["forms"].values():
            for helper in form["helpers"]:
                self.assertRegex(
                    form["decode"]["excerpt"], rf"\b{re.escape(helper)}\s*\("
                )

    def test_evidence_is_reproducible_and_matches_official_export(self) -> None:
        self.assertNotIn("source_commit", self.data)
        self.assertNotIn("http", json.dumps(self.data))
        with tempfile.TemporaryDirectory() as directory:
            exported = Path(directory) / "sail"
            export_sail(exported)
            check_export(exported)
            self.assertEqual(
                (exported / "model/decode/decode.sail").read_bytes(),
                _release_decode(),
            )

    def test_unsupported_forms_show_trap_and_platform_boundary(self) -> None:
        trapped = {
            form_id
            for form_id, form in self.data["forms"].items()
            if form["disposition"] == "traps-in-sail-executable-subset"
        }
        self.assertEqual(
            trapped,
            {
                "dma_free_l_32_5af48f644596",
                "dma_free_s_32_5de9a6bba806",
                "mcopy_dl_32_d6af61213c20",
                "mcopy_ds_32_e7a90ccbe4db",
            },
        )
        by_id = {row["id"]: row for row in self.rows}
        for form_id in trapped:
            detail = sail_detail(by_id[form_id])
            self.assertIn("trap_illegal_inst", detail)
            self.assertIn("不执行数据移动", detail)
            self.assertIn("不产生架构结果或副作用", detail)
            self.assertNotIn("结果需由平台实现/译码路径", detail)

    def test_mismatched_row_cannot_reuse_evidence(self) -> None:
        row = copy.deepcopy(self.rows[0])
        row["asm"] += " corrupt"
        self.assertEqual(sail_detail(row), "")


if __name__ == "__main__":
    unittest.main()
