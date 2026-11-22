#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from manual_reader import (
    _plain_markdown,
    operation_detail,
    reader_detail,
    reader_summary,
)


DATA = ROOT / "docs/architecture/isa-manual/reference/data/manual-reader-zh.json"
LICENSE = ROOT / "docs/architecture/isa-manual/reference/data/PTO-SPEC-LICENSE.txt"


class ManualReaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_exact_coverage_and_pinned_identity(self) -> None:
        self.assertEqual(
            self.data["coverage"],
            {
                "common_forms": 578,
                "tile_operations": 119,
                "unique_reader_pages": 669,
            },
        )
        records = self.data["records"]
        self.assertEqual(sum(len(row["identities"]) for row in records.values()), 697)
        commit = self.data["source"]["commit"]
        for asl_path, row in records.items():
            with self.subTest(asl_path=asl_path):
                self.assertTrue(asl_path.startswith("asl/"))
                self.assertIn(f"/blob/{commit}/{asl_path}", row["normative_asl_url"])
                self.assertTrue(row["mnemonic"])
                self.assertTrue(row["owners"])
                self.assertTrue(row["identities"])

    def test_plain_summary_and_detail_keep_authority_boundary(self) -> None:
        path = "asl/tile/matrix-and-matrix-vector/matrix-matrix/TMATMUL.asl"
        summary = reader_summary(path)
        self.assertIn("TMATMUL", summary)
        self.assertNotIn("`", summary)
        self.assertNotRegex(summary, r"\[[^]]+\]\([^)]+\)")
        detail = reader_detail(path)
        self.assertIn('data-content-role="non-normative-explanation"', detail)
        self.assertIn("解释性说明", detail)
        self.assertIn("中文导读", detail)
        self.assertIn("zh-CN/", detail)

    def test_markdown_cleanup_preserves_architectural_literals(self) -> None:
        source = (
            "`PTO_XLEN` 中的 `<dst>` 从 `[SrcL]` 与 `__tmp__` 读取，计算 `a * b`、"
            "`x << 12` 与 `0 < x > -1`；参见[规范](../broken.md)。"
        )
        self.assertEqual(
            _plain_markdown(source),
            "PTO_XLEN 中的 <dst> 从 [SrcL] 与 __tmp__ 读取，计算 a * b、x << 12 与 "
            "0 < x > -1；参见规范。",
        )

    def test_unknown_or_unsafe_path_has_no_fallback(self) -> None:
        for path in ("", "../secret.asl", "/asl/scalar/ADD.asl", "asl/missing.asl"):
            with self.subTest(path=path):
                self.assertEqual(reader_summary(path), "")
                self.assertEqual(reader_detail(path), "")
                self.assertEqual(operation_detail(path), "")

    def test_normative_operation_is_exact_and_visibly_separate(self) -> None:
        path = "asl/tile/matrix-and-matrix-vector/matrix-matrix/TMATMUL.asl"
        record = self.data["records"][path]
        self.assertEqual(record["operation_kind"], "doc-operation-blocks")
        self.assertEqual(len(record["operation_blocks"]), 1)
        block = record["operation_blocks"][0]
        self.assertTrue(block["text"].startswith("// DOC-BEGIN: operation\n"))
        self.assertTrue(block["text"].rstrip().endswith("// DOC-END: operation"))
        detail = operation_detail(path)
        self.assertIn('<details class="asl-operation"', detail)
        self.assertIn('data-content-role="normative-asl"', detail)
        self.assertIn("<pre><code>", detail)
        self.assertIn(f"#L{block['line_start']}-L{block['line_end']}", detail)

    def test_license_asset_is_exact_offline_notice(self) -> None:
        text = LICENSE.read_text(encoding="utf-8")
        self.assertEqual(text, self.data["license"]["notice"])
        self.assertEqual(
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
            self.data["license"]["sha256"],
        )
        self.assertEqual(self.data["license"]["asset"], "PTO-SPEC-LICENSE.txt")
        self.assertTrue(text.startswith("BSD 3-Clause License\n"))

    @unittest.skipUnless(os.environ.get("PTO_SPEC_ROOT"), "PTO_SPEC_ROOT is not set")
    def test_every_operation_block_is_verbatim_from_pinned_source(self) -> None:
        root = Path(os.environ["PTO_SPEC_ROOT"])
        commit = self.data["source"]["commit"]
        for asl_path, record in self.data["records"].items():
            with self.subTest(asl_path=asl_path):
                source = subprocess.check_output(
                    ["git", "-C", str(root), "show", f"{commit}:{asl_path}"]
                )
                self.assertEqual(
                    hashlib.sha256(source).hexdigest(), record["asl_file_sha256"]
                )
                lines = source.splitlines(keepends=True)
                for block in record["operation_blocks"]:
                    original = b"".join(
                        lines[block["line_start"] - 1 : block["line_end"]]
                    )
                    self.assertEqual(original.decode("utf-8"), block["text"])
                    self.assertEqual(
                        hashlib.sha256(original).hexdigest(), block["sha256"]
                    )


if __name__ == "__main__":
    unittest.main()
