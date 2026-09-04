from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "tools" / "isa" / "gen_c_codec.py"
SPEC = ROOT / "isa" / "v0.58" / "linxisa-v0.58.json"


class CCodecGeneratorTest(unittest.TestCase):
    def test_retires_legacy_shared_source_variants(self) -> None:
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        expected = {
            instruction["id"]: instruction["pto_source_form_variant"]
            for instruction in spec["instructions"]
            if instruction.get("pto_source_form_variant")
        }
        self.assertEqual(expected, {})

        with tempfile.TemporaryDirectory(prefix="linx-c-codec-") as directory:
            output = Path(directory)
            subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--spec",
                    str(SPEC),
                    "--out-dir",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            header = (output / "linxisa_opcodes.h").read_text(encoding="utf-8")
            source = (output / "linxisa_opcodes.c").read_text(encoding="utf-8")

        self.assertIn("const char *source_variant", header)
        self.assertNotRegex(source, r'\.source_variant = "[^"]+"')


if __name__ == "__main__":
    unittest.main()
