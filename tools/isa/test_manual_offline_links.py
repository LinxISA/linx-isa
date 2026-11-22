#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from check_html_reference import Audit


class OfflineLinksTest(unittest.TestCase):
    def make_site(self, root: Path) -> Audit:
        for name in ("manual.css", "index-filter.js"):
            (root / name).write_text("", encoding="utf-8")
        (root / "audit.json").write_text(
            '{"forms":[],"tile_operations":[]}', encoding="utf-8"
        )
        for name in ("encoding.html", "tile.html", "sources.html"):
            (root / name).write_text("<main></main>", encoding="utf-8")
        return Audit(root, {"instructions": []}, {"operations": []})

    def test_recursive_percent_encoded_links_fragments_and_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "support").mkdir()
            (root / "support-assets").mkdir()
            (root / "support-assets" / "图 x.svg").write_text(
                "<svg/>", encoding="utf-8"
            )
            (root / "support" / "a b.html").write_text(
                '<main id="src-a--说明"><img src="../support-assets/%E5%9B%BE%20x.svg"></main>',
                encoding="utf-8",
            )
            (root / "index.html").write_text(
                '<a href="support/a%20b.html#src-a--%E8%AF%B4%E6%98%8E">说明</a>',
                encoding="utf-8",
            )
            audit = self.make_site(root)
            audit.check_links_and_assets()
            self.assertEqual(audit.errors, [])

    def test_missing_recursive_target_and_fragment_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "support").mkdir()
            (root / "index.html").write_text(
                '<a href="support/missing.html">坏链接</a>', encoding="utf-8"
            )
            audit = self.make_site(root)
            audit.check_links_and_assets()
            self.assertTrue(any("broken href" in e for e in audit.errors))
            (root / "support" / "missing.html").write_text(
                '<main id="other"></main>', encoding="utf-8"
            )
            (root / "index.html").write_text(
                '<a href="support/missing.html#wanted">坏片段</a>', encoding="utf-8"
            )
            audit = self.make_site(root)
            audit.check_links_and_assets()
            self.assertTrue(any("missing fragment" in e for e in audit.errors))

    def test_authored_reader_english_is_exempt_but_generated_english_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                '<div class="authored-reader"><p>This original English annotation is preserved here.</p></div><p>This generated English sentence must be rejected here.</p>',
                encoding="utf-8",
            )
            audit = self.make_site(root)
            audit.check_links_and_assets()
            english = [e for e in audit.errors if "default-visible English" in e]
            self.assertEqual(len(english), 1)
            self.assertIn("generated English", english[0])


if __name__ == "__main__":
    unittest.main()
