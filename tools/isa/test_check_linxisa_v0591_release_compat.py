#!/usr/bin/env python3

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from check_linxisa_v0591_release_compat import check  # noqa: E402


class LinxISAV0591ReleaseCompatibilityTest(unittest.TestCase):
    def test_immutable_release_and_historical_registry_slice(self):
        self.assertEqual(check(), [])


if __name__ == "__main__":
    unittest.main()
