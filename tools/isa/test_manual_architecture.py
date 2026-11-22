#!/usr/bin/env python3
from __future__ import annotations
import re, unittest
from manual_architecture import (
    architecture_collections,
    architecture_pages,
    architecture_routes,
    register_catalog_html,
    register_catalog_records,
    render_architecture_page,
    silicon_canvas_targets,
    validate_architecture_sources,
)


class ManualArchitectureTest(unittest.TestCase):
    def test_all_routes_disjoint_and_ssr_directory_reachable(self):
        pages = architecture_pages()
        self.assertEqual(len(pages), len({p.route for p in pages}))
        self.assertNotEqual(
            next(p.route for p in pages if p.key == "ssr-index"),
            next(p.route for p in pages if p.key == "ssr"),
        )

    def test_curated_sources_and_routes_are_exact(self):
        self.assertEqual(validate_architecture_sources(), [])
        pages = architecture_pages()
        routes = architecture_routes()
        self.assertEqual(len(pages), 125)
        self.assertEqual(len(routes), 118)
        self.assertEqual(
            {p.route for p in pages if p.collection == "index"},
            {
                "architecture.html",
                "execution-model.html",
                "arch-state.html",
                "arch-system.html",
                "arch-ssr.html",
                "arch-datatypes.html",
                "arch-model-notes.html",
            },
        )
        self.assertEqual(len(routes), len(set(routes.values())))
        self.assertEqual(len(pages), len({page.key for page in pages}))

    def test_collections_and_version_boundaries_are_explicit(self):
        groups = architecture_collections()
        self.assertEqual(
            set(groups),
            {"execution", "state", "system", "ssr", "datatype", "implementation"},
        )
        self.assertGreaterEqual(len(groups["execution"]), 8)
        self.assertGreaterEqual(len(groups["state"]), 10)
        contextual = [
            p for p in architecture_pages() if p.status == "contextual-original"
        ]
        self.assertEqual([p.key for p in contextual], ["memory-context"])
        self.assertIn("不作为", contextual[0].version_note)
        pages = {page.key: page for page in architecture_pages()}
        self.assertIn("79 个", pages["tepl-carrier"].version_note)
        self.assertIn("v0.55", pages["exception-model"].version_note)

    def test_every_chapter_renders_tagged_original(self):
        for page in architecture_pages():
            if not page.source_path:
                continue
            with self.subTest(page=page.key):
                fragment = render_architecture_page(page)
                self.assertIsNotNone(fragment)
                self.assertTrue(fragment.html.strip())
                self.assertRegex(page.summary, r"[\u4e00-\u9fff]")
                self.assertNotIn("<h1", fragment.html)

    def test_silicon_canvas_targets_name_specific_mechanisms(self):
        targets = silicon_canvas_targets()
        self.assertGreaterEqual(len(targets), 10)
        self.assertTrue(
            {
                "block-lifecycle",
                "execution-pipeline",
                "register-state-map",
                "exception-lifecycle",
                "memory-hierarchy",
            }
            <= {p.illustration for p in targets}
        )

    def test_full_normalized_system_register_catalog(self):
        records = register_catalog_records()
        self.assertEqual(len(records), 100)
        self.assertEqual(len({record.key for record in records}), 100)
        self.assertTrue(
            any(
                record.name == "BLOCKNUM" and record.historical_source
                for record in records
            )
        )
        self.assertIn("THREAD_PTR", register_catalog_html())


if __name__ == "__main__":
    unittest.main()
