#!/usr/bin/env python3
"""Focused checks for the inactive full-schema v0.59.1 catalog candidate."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from build_linxisa_v0591_candidate import (
    build,
    check_collisions,
    render,
)
from build_golden import effective_pto_encoding
from check_pto_v058_manifest import compiled_constraint_key, source_constraint_key


class LinxISAV0591CandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(
            (ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8")
        )
        cls.candidate = build()

    def test_counts_identity_and_linx_only_preservation(self):
        instructions = self.candidate["instructions"]
        common = [
            item
            for item in instructions
            if item.get("pto_source_form_id") and not item.get("pto_base_form_id")
        ]
        scoped = [item for item in instructions if item.get("pto_base_form_id")]
        linx_only = [
            item for item in instructions if not item.get("pto_source_form_id")
        ]
        self.assertEqual((len(common), len(linx_only), len(scoped)), (578, 216, 705))
        old_common = {
            item["pto_source_form_id"]: (item["id"], item["uid"])
            for item in self.baseline["instructions"]
            if item.get("pto_source_form_id")
        }
        self.assertEqual(
            {item["pto_source_form_id"]: (item["id"], item["uid"]) for item in common},
            old_common,
        )
        old_linx = {
            item["id"]: item
            for item in self.baseline["instructions"]
            if not item.get("pto_source_form_id")
        }
        self.assertEqual({item["id"]: item for item in linx_only}, old_linx)

    def test_full_schema_is_deterministic_and_has_unique_rows(self):
        self.assertEqual(render(self.candidate), render(build()))
        self.assertEqual(self.candidate["schema"], "linxisa.catalog.v0")
        self.assertEqual(self.candidate["instruction_count"], 1499)
        ids = [item["id"] for item in self.candidate["instructions"]]
        uids = [item["uid"] for item in self.candidate["instructions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(uids), len(set(uids)))
        for item in self.candidate["instructions"]:
            self.assertEqual(len(item["parts"]), len(item["encoding"]["parts"]))

    def test_released_encodings_and_constraints_are_applied(self):
        scalar = json.loads(
            (ROOT / "isa/v0.59/state/pto_scalar_forms.json").read_text(encoding="utf-8")
        )
        command = json.loads(
            (ROOT / "isa/v0.59/state/pto_command_forms.json").read_text(
                encoding="utf-8"
            )
        )
        source = {
            item["form_id"]: item
            for item in [*scalar["forms"], *command["forms"], *scalar["scoped_forms"]]
        }
        compiled = {
            item["pto_source_form_id"]: item
            for item in self.candidate["instructions"]
            if item.get("pto_source_form_id")
        }
        self.assertEqual(source.keys(), compiled.keys())
        for identity, form in source.items():
            expected = [
                (int(part["width_bits"]), int(part["mask"], 0), int(part["match"], 0))
                for part in effective_pto_encoding(form)
            ]
            actual = [
                (int(part["width_bits"]), int(part["mask"], 0), int(part["match"], 0))
                for part in compiled[identity]["encoding"]["parts"]
            ]
            self.assertEqual(actual, expected, identity)
            widths = {field["name"]: int(field["width"]) for field in form["fields"]}
            actual_constraints = dict(compiled_constraint_key(compiled[identity], form))
            expected_constraints = dict(source_constraint_key(form))
            for field, accepted in expected_constraints.items():
                actual = actual_constraints.get(field, tuple(range(1 << widths[field])))
                self.assertEqual(actual, accepted, identity)

    def test_collision_checker_rejects_duplicate_scoped_encoding(self):
        candidate = copy.deepcopy(self.candidate)
        scoped = [
            item for item in candidate["instructions"] if item.get("pto_base_form_id")
        ]
        scoped[1]["encoding"] = copy.deepcopy(scoped[0]["encoding"])
        with self.assertRaisesRegex(ValueError, "encoding collisions"):
            check_collisions(candidate)

    def test_catalog_tools_can_consume_candidate(self):
        from gen_c_codec import _emit_tables
        from gen_sail_decode import render as render_sail_decode
        from report_encoding_space import _build_instructions, _extract_patterns

        header, source = _emit_tables(self.candidate, "candidate.json")
        self.assertIn("linxisa_inst_forms_count = 1499", source)
        self.assertIn("linxisa_inst_form", header)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            path.write_text(render(self.candidate), encoding="utf-8")
            decoded = _build_instructions(_extract_patterns(path))
        self.assertEqual(len(decoded), 1499)
        sail = render_sail_decode(
            self.candidate,
            (ROOT / "isa/sail/model/execute/execute.sail").read_text(encoding="utf-8"),
            "isa/v0.59/linxisa-v0.59-candidate.json",
            self.candidate["retired_encodings"],
        )
        self.assertIn("c.ldi.private [srcL, simm], ->t", sail)


if __name__ == "__main__":
    unittest.main()
