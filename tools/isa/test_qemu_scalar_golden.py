import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_qemu_scalar_golden import mismatches, signature  # noqa: E402


class QemuScalarGoldenTests(unittest.TestCase):
    def test_old_atomic_word_cannot_pass_on_mnemonic_presence(self):
        form = {"form_id": "lr_w", "mnemonic": "LR.W", "length_bits": 32,
                "encoding": [{"index": 0, "mask": "0x7800707f", "match": "0x1000000b"}]}
        self.assertEqual(mismatches([form], {signature(form)}), [])
        self.assertEqual(mismatches([form], {("lr_w", 32, 0xF000707F, 0x2000000B)}), ["lr_w"])
        self.assertEqual(mismatches([form], {("lr_h", 32, 0x7800707F, 0x1000000B)}), ["lr_w"])

    def test_half_long_container_padding_is_fixed_zero(self):
        form = {"mnemonic": "HL.CASW", "length_bits": 48,
                "encoding": [{"index": 0, "mask": "0xf", "match": "0xe"}]}
        self.assertEqual(signature(form), ("hl_casw", 64, 0xFFFF00000000000F, 0xE))


if __name__ == "__main__":
    unittest.main()
