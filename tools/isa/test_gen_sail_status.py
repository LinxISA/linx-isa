#!/usr/bin/env python3
"""Focused tests for stable PTO-source semantic policy overrides."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import gen_sail_status


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        spec = root / "spec.json"
        policy = root / "policy.json"
        spec.write_text(
            json.dumps(
                {
                    "version": "0.58.3",
                    "instructions": [
                        {
                            "id": "compiled_dma_identity",
                            "mnemonic": "DMA",
                            "pto_source_form_id": "stable_pto_dma_identity",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        policy.write_text(
            json.dumps(
                {
                    "default_status": "executable-subset",
                    "form_overrides": {"stable_pto_dma_identity": "decode-only"},
                }
            ),
            encoding="utf-8",
        )
        result = gen_sail_status.build(spec, policy)
        assert result["forms"]["compiled_dma_identity"]["status"] == "decode-only"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
