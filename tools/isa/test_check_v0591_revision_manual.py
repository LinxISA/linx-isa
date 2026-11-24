#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_v0591_revision_manual import (
    ENCODING_ONLY_FORMS,
    REMOVED_BLOCK_FORMS,
    check_removed_and_legacy_material,
    check_representative_semantics,
    check_ssr_projection,
    compare_site_and_zip,
    reader_text,
    signed_baseline,
    zip_members,
)


class V0591RevisionManualCheckTest(unittest.TestCase):
    def test_signed_baseline_difference_is_exactly_193(self):
        _catalog, removed_ids, removed_names = signed_baseline()
        self.assertEqual(len(removed_ids), 193)
        self.assertEqual(sum(name.startswith("V.") for name in removed_names), 184)
        self.assertEqual(
            {name for name in removed_names if not name.startswith("V.")},
            REMOVED_BLOCK_FORMS,
        )
        self.assertEqual(
            ENCODING_ONLY_FORMS,
            {"DMA.FREE.L", "DMA.FREE.S", "MCOPY.DL", "MCOPY.DS"},
        )

    def test_real_lock_identity_and_old_value_are_not_legacy_patterns(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            page = site / "article-source/current.md"
            page.parent.mkdir()
            page.write_text(
                "PTO 锁 v0.59.1.0；原子操作返回内存旧值。"
                "[早期文件名](docs/zh/isa/inst/V.ADD.md)\n",
                encoding="utf-8",
            )
            self.assertIn("旧值", reader_text(page))
            errors: list[str] = []
            check_removed_and_legacy_material(site, {"V.ADD"}, errors)
            self.assertEqual(errors, [])

    def test_download_scan_rejects_removed_form_and_vgpr_tutorial(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "bad.md").write_text("执行 V.ADD 并写入 VGPR。", encoding="utf-8")
            errors: list[str] = []
            check_removed_and_legacy_material(site, {"V.ADD"}, errors)
            self.assertTrue(any("removed form" in error for error in errors))

    def test_only_historical_ssr_status_is_rejected_by_status_alone(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "architecture-audit.json").write_text(
                json.dumps(
                    {
                        "arch-constraints.html": {"status": "historical-note"},
                        "arch-ssr-time.html": {"status": "historical-register-note"},
                    }
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            check_removed_and_legacy_material(site, {"V.ADD"}, errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("arch-ssr-time.html", errors[0])

    def test_reservation_json_is_the_only_removed_name_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            spec = site / "spec"
            spec.mkdir()
            document = {"reservations": [{"mnemonic": "V.*"}, {"mnemonic": "B.TEXT"}]}
            (spec / "extension_encoding_reservations.json").write_text(
                json.dumps(document), encoding="utf-8"
            )
            errors: list[str] = []
            check_removed_and_legacy_material(site, {"B.TEXT"}, errors)
            self.assertEqual(errors, [])

    def test_embedded_catalog_reservation_is_not_active_reader_content(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            spec = site / "spec"
            spec.mkdir()
            document = {
                "state": {
                    "extension_encoding_reservations": {
                        "reservations": [{"mnemonic": "B.TEXT"}]
                    }
                }
            }
            (spec / "linxisa-v0.59.json").write_text(
                json.dumps(document), encoding="utf-8"
            )
            errors: list[str] = []
            check_removed_and_legacy_material(site, {"B.TEXT"}, errors)
            self.assertEqual(errors, [])

    def test_representative_contracts_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "op-b-ior.html").write_text("<main>B.IOR</main>")
            errors: list[str] = []
            check_representative_semantics(site, errors)
            self.assertTrue(any("op-b-ior.html" in error for error in errors))
            self.assertTrue(
                any("op-hl-ccat.html: missing" in error for error in errors)
            )

    def test_ssr_projection_requires_100_details_and_no_old_links(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "arch-ssr.html").write_text(
                '<a href="arch-ssr-time.html">TIME</a>', encoding="utf-8"
            )
            errors: list[str] = []
            check_ssr_projection(site, errors)
            self.assertTrue(any("expected 100" in error for error in errors))
            self.assertTrue(any("historical per-register" in error for error in errors))

    def test_zip_inventory_and_bytes_must_match_site(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / "site"
            site.mkdir()
            (site / "index.html").write_text("current", encoding="utf-8")
            bundle = root / "manual.zip"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("index.html", "stale")
            errors: list[str] = []
            compare_site_and_zip(site, bundle, errors)
            self.assertTrue(any("files differ" in error for error in errors))

    def test_zip_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "manual.zip"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("../escape", "bad")
            with self.assertRaisesRegex(ValueError, "unsafe ZIP member"):
                zip_members(bundle)

    def test_percent_encoded_zip_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "manual.zip"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("%2e%2e/escape", "bad")
            with self.assertRaisesRegex(ValueError, "unsafe ZIP member"):
                zip_members(bundle)


if __name__ == "__main__":
    unittest.main()
