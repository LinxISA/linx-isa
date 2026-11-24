#!/usr/bin/env python3
from __future__ import annotations
import subprocess, unittest
from pathlib import Path
from manual_markdown import (
    build_support_bundle,
    document_namespace,
    render_tagged_markdown,
    support_asset_path,
    support_document_path,
)
from manual_tag import REVIEWED_COMMIT
from manual_reader_site import ArticleLibrary

ROOT = Path(__file__).resolve().parents[2]
MOVR = "docs/zh/isa/inst/misa_c/C.MOVR.md"
PSEUDO = "docs/zh/isa/inst/LibPseudoCode.md"
COMPRESS = "docs/zh/isa/instset/compressInstrs.md"


class ManualMarkdownTest(unittest.TestCase):
    def test_cmovr_full_article_and_dependencies(self):
        result = render_tagged_markdown(MOVR, current_page="op-c-movr.html")
        self.assertIn("寄存器移动", result.html)
        self.assertIn("admonition info", result.html)
        self.assertIn("c.movr", result.html)
        self.assertIn("SrcL", result.html)
        self.assertIn(PSEUDO, result.documents)
        self.assertIn(COMPRESS, result.documents)
        image = "docs/zh/figs/bitfield/svg/Instruction_16bit/C.MOVR.svg"
        self.assertIn(image, result.assets)
        self.assertIn(support_asset_path(image), result.html)
        self.assertNotIn("<h1", result.html)
        self.assertIn("<h2", result.html)

    def test_bounded_support_bundle_keeps_required_material_offline(self):
        required = {PSEUDO, COMPRESS}
        bundle = build_support_bundle(
            [MOVR], follow_document=lambda _s, t: t in required
        )
        self.assertIn(support_document_path(MOVR), bundle.fragments)
        for path in required:
            self.assertIn(support_document_path(path), bundle.fragments)
        self.assertIn("<table>", bundle.fragments[support_document_path(COMPRESS)])
        self.assertTrue(any(name.endswith("C.MOVR.svg") for name in bundle.assets))
        self.assertIn(
            "unbundled-local-reference",
            bundle.fragments[support_document_path(COMPRESS)],
        )

    def test_primary_document_route_and_namespaced_fragment(self):
        routes = {COMPRESS: "op-compressed-reference.html"}
        result = render_tagged_markdown(
            MOVR, current_page="op-c-movr.html", document_routes=routes
        )
        self.assertIn('href="op-compressed-reference.html"', result.html)
        self.assertNotIn(COMPRESS, result.documents)

    def test_removed_instruction_links_keep_text_without_href(self):
        result = render_tagged_markdown(
            "docs/zh/isa/instset/longInstrs.md",
            current_page="support-long-instructions.html",
            follow_document=lambda _s, _t: False,
        )
        self.assertIn("V.ADD", result.html)
        self.assertIn("removed-local-reference", result.html)
        self.assertNotIn("misa_v/V.ADD", result.html)

    def test_downloadable_markdown_uses_flat_offline_routes_and_assets(self):
        source = "docs/zh/isa/register/common/barg.md"
        library = ArticleLibrary.__new__(ArticleLibrary)
        library.routes = {
            "docs/zh/isa/inst/misa_g/SETC.TGT.md": "op-setc-tgt.html",
            "docs/zh/isa/arch/branch.md": "arch-branch.html",
        }
        markdown = """[设置目标](../../inst/misa_g/SETC.TGT.md)
[跳转方式](../../arch/branch.md#branch)
[保留文字](../../header/DOES-NOT-EXIST.md)
![BARG](../../../figs/bitfield/svg/Sysregs/BARG.svg)
"""
        rewritten = library.download_source(source, markdown)
        self.assertIn(
            "[设置目标](../op-setc-tgt.html)",
            rewritten,
        )
        self.assertIn(
            "[跳转方式](../arch-branch.html#"
            + document_namespace("docs/zh/isa/arch/branch.md")
            + "--branch)",
            rewritten,
        )
        self.assertIn("保留文字", rewritten)
        self.assertNotIn("DOES-NOT-EXIST.md", rewritten)
        self.assertIn(
            "![BARG](../support-assets/docs--zh--figs--bitfield--svg--Sysregs--BARG.svg)",
            rewritten,
        )

    def test_safe_raw_html_is_preserved_without_active_content(self):
        result = render_tagged_markdown(
            "docs/zh/index.md",
            current_page="source-index.html",
            follow_document=lambda _s, _t: False,
        )
        self.assertIn("<section", result.html)
        self.assertIn("linx-home-hero", result.html)
        self.assertNotIn("<script", result.html.lower())
        self.assertNotIn(" on", result.html.lower())

    def test_every_tagged_chinese_isa_markdown_renders(self):
        listing = subprocess.check_output(
            [
                "git",
                "ls-tree",
                "-r",
                "--name-only",
                REVIEWED_COMMIT,
                "docs/zh/isa",
            ],
            cwd=ROOT,
            text=True,
        )
        paths = [
            p
            for p in listing.splitlines()
            if p.endswith(".md")
            and (
                p.startswith("docs/zh/isa/inst/")
                or p.startswith("docs/zh/isa/header/")
                or "/blockIntro/" in p
            )
        ]
        self.assertGreaterEqual(len(paths), 900)
        for path in paths:
            with self.subTest(path=path):
                result = render_tagged_markdown(
                    path,
                    current_page="source.html",
                    follow_document=lambda _s, _t: False,
                )
                self.assertTrue(result.html.strip())
                self.assertNotIn("javascript:", result.html.lower())


if __name__ == "__main__":
    unittest.main()
