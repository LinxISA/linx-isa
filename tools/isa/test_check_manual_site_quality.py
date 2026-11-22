#!/usr/bin/env python3

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from tools.isa.check_manual_site_quality import (
    _SSRTable,
    _check_canvas,
    _check_editorial,
    _check_mgather,
)


class CheckManualSiteQualityTest(unittest.TestCase):
    def test_ssr_parser_preserves_key_address_access_and_scope(self):
        parser = _SSRTable()
        parser.feed(
            '<table><tr data-register-key="base:TIME:0x0010"><td><code>TIME</code></td><td><code>0x0010</code></td><td>RO</td><td>base</td><td>—</td></tr></table>'
        )
        self.assertEqual(
            parser.rows, {"base:TIME:0x0010": ("TIME", "0x0010", "RO", "base", "—")}
        )

    def test_mgather_current_and_variant_notes_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = "S32、U32、S64 或 U64 字节位移，不再按传输元素大小缩放。MinIndex 和 MaxIndex 是有符号的相对字节界限。"
            (root / "tile-mgather.html").write_text(base)
            for suffix in (
                "ADD",
                "AND",
                "CAS",
                "DEC",
                "EXCH",
                "INC",
                "MAX",
                "MIN",
                "OR",
                "XOR",
            ):
                name = f"MGATHER_{suffix}"
                (root / f"tile-{name.lower().replace('_', '-')}.html").write_text(
                    f"{name} 原子操作；普通搬运循环只解释寻址，不能代替本形式的原子操作"
                )
            for name in ("MGATHER_MASK", "MSCATTER_MASK"):
                (root / f"tile-{name.lower().replace('_', '-')}.html").write_text(
                    f"{name} 按掩码选择参与访问的元素；原页没有掩码步骤"
                )
            errors = []
            _check_mgather(root, errors)
            self.assertEqual(errors, [])

    def test_canvas_manifest_binds_hash_sources_and_consumers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "figures").mkdir()
            (root / "figure-source").mkdir()
            image = b"PNG"
            image_digest = sha256(image).hexdigest()
            (root / "figures/x.png").write_bytes(image)
            (root / "figure-source/x.json").write_text("{}")
            decision_ref = "silicon-canvas://submit-review/x/final"
            review = {
                "artifact_id": "x",
                "image_sha256": image_digest,
                "decision": {"action": "accept"},
                "blocking_findings": [],
                "decision_ref": decision_ref,
                "raw_decision": {"decision": {"action": "accept"}},
                "provenance_snapshot": {
                    "artifact_id": "x",
                    "image_sha256": image_digest,
                    "decision_ref": decision_ref,
                },
            }
            review_bytes = json.dumps(review, sort_keys=True).encode()
            (root / "figure-source/x-review.json").write_bytes(review_bytes)
            pages = ("tile-mgather.html", "op-c-movr.html", "arch-state.html")
            for page in pages:
                (root / page).write_text(
                    '<img class="canvas-figure-image" src="figures/x.png" alt="结构图">'
                )
            (root / "canvas-audit.json").write_text(
                json.dumps(
                    {
                        "figures": [
                            {
                                "id": "x",
                                "image": "figures/x.png",
                                "sha256": image_digest,
                                "source_files": ["figure-source/x.json"],
                                "review_decision": "accept",
                                "review_file": "figure-source/x-review.json",
                                "review_sha256": sha256(review_bytes).hexdigest(),
                                "accepted_image_sha256": image_digest,
                                "pages": list(pages),
                            }
                        ]
                    }
                )
            )
            errors = []
            _check_canvas(root, errors)
            self.assertEqual(errors, [])

    def test_canvas_rejects_non_accept_official_decisions(self):
        for action in ("needs_changes", "reject"):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "figures").mkdir()
                (root / "figure-source").mkdir()
                image = b"PNG"
                image_digest = sha256(image).hexdigest()
                (root / "figures/x.png").write_bytes(image)
                (root / "figure-source/x.json").write_text("{}")
                decision_ref = f"silicon-canvas://submit-review/x/{action}"
                review = {
                    "artifact_id": "x",
                    "image_sha256": image_digest,
                    "decision": {"action": action},
                    "blocking_findings": [],
                    "decision_ref": decision_ref,
                    "raw_decision": {"decision": {"action": action}},
                    "provenance_snapshot": {
                        "artifact_id": "x",
                        "image_sha256": image_digest,
                        "decision_ref": decision_ref,
                    },
                }
                review_bytes = json.dumps(review, sort_keys=True).encode()
                (root / "figure-source/x-review.json").write_bytes(review_bytes)
                pages = ("tile-mgather.html", "op-c-movr.html", "arch-state.html")
                for page in pages:
                    (root / page).write_text(
                        '<img class="canvas-figure-image" src="figures/x.png" alt="结构图">'
                    )
                (root / "canvas-audit.json").write_text(
                    json.dumps(
                        {
                            "figures": [
                                {
                                    "id": "x",
                                    "image": "figures/x.png",
                                    "sha256": image_digest,
                                    "source_files": ["figure-source/x.json"],
                                    "review_decision": "accept",
                                    "review_file": "figure-source/x-review.json",
                                    "review_sha256": sha256(review_bytes).hexdigest(),
                                    "accepted_image_sha256": image_digest,
                                    "pages": list(pages),
                                }
                            ]
                        }
                    )
                )
                errors = []
                _check_canvas(root, errors)
                self.assertIn(
                    f"canvas x: official decision.action is not a terminal success",
                    errors,
                )

    def test_canvas_stop_requires_signoff_and_exact_best_attempt(self):
        for defect in (None, "missing_signoff", "wrong_best_attempt"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "figures").mkdir()
                (root / "figure-source").mkdir()
                image = b"PNG"
                image_digest = sha256(image).hexdigest()
                (root / "figures/x.png").write_bytes(image)
                (root / "figure-source/x.json").write_text("{}")
                decision_ref = "silicon-canvas://submit-review/x/stop"
                review = {
                    "artifact_id": "x",
                    "image_sha256": image_digest,
                    "decision": {"action": "stop"},
                    "blocking_findings": [],
                    "decision_ref": decision_ref,
                    "reviewed_attempt": 3,
                    "best_attempt_technically_correct": True,
                    "raw_decision": {
                        "decision": {"action": "stop"},
                        "best_attempt": {
                            "attempt": 3 if defect != "wrong_best_attempt" else 2,
                            "score": 97,
                            "image_path": "/review-output/x.png",
                        },
                    },
                    "provenance_snapshot": {
                        "artifact_id": "x",
                        "image_sha256": image_digest,
                        "decision_ref": decision_ref,
                        "best_attempt_file": "x.png",
                        "best_attempt_image_sha256": image_digest,
                    },
                }
                if defect != "missing_signoff":
                    review["independent_technical_review"] = {
                        "verdict": "approve",
                        "image_sha256": image_digest,
                        "blocking_findings": [],
                        "limitations": [
                            "评审器到达迭代上限；当前图已经通过技术正确性复核。"
                        ],
                    }
                review_bytes = json.dumps(review, sort_keys=True).encode()
                (root / "figure-source/x-review.json").write_bytes(review_bytes)
                pages = ("tile-mgather.html", "op-c-movr.html", "arch-state.html")
                for page in pages:
                    (root / page).write_text(
                        '<img class="canvas-figure-image" src="figures/x.png" alt="结构图">'
                    )
                (root / "canvas-audit.json").write_text(
                    json.dumps(
                        {
                            "figures": [
                                {
                                    "id": "x",
                                    "image": "figures/x.png",
                                    "sha256": image_digest,
                                    "source_files": ["figure-source/x.json"],
                                    "review_decision": "stop",
                                    "review_file": "figure-source/x-review.json",
                                    "review_sha256": sha256(review_bytes).hexdigest(),
                                    "accepted_image_sha256": image_digest,
                                    "pages": list(pages),
                                }
                            ]
                        }
                    )
                )
                errors = []
                _check_canvas(root, errors)
                if defect is None:
                    self.assertEqual(errors, [])
                elif defect == "missing_signoff":
                    self.assertIn(
                        "canvas x: stopped review lacks independent technical signoff",
                        errors,
                    )
                else:
                    self.assertIn(
                        "canvas x: stopped review does not bind the reviewed best attempt",
                        errors,
                    )

    def test_missing_editorial_audit_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = []
            _check_editorial(Path(tmp), errors)
            self.assertEqual(errors, ["editorial-audit.json: missing"])


if __name__ == "__main__":
    unittest.main()
