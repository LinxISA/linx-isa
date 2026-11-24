import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manual_v0592_edition import install


class EditionInstallTest(unittest.TestCase):
    def test_old_pages_are_no_longer_under_the_live_directory(self):
        with tempfile.TemporaryDirectory() as work:
            dest = Path(work) / "manual"
            dest.mkdir()
            (dest / "audit.json").write_text('{"tag":"v0.59.1"}')
            (dest / "op-b-text.html").write_text("old")
            files = {"audit.json": b'{"tag":"v0.59.2"}', "index.html": b"new"}
            with self.assertRaises(ValueError):
                install(files, dest, check=True)
            install(files, dest)
            install(files, dest, check=True)
            self.assertFalse((dest / "op-b-text.html").exists())
            self.assertEqual(
                len(list(Path(work).glob("manual-previous-*/op-b-text.html"))), 1
            )

    def test_unrelated_user_files_are_preserved(self):
        with tempfile.TemporaryDirectory() as work:
            dest = Path(work)
            (dest / "notes.txt").write_text("keep")
            with self.assertRaises(ValueError):
                install({"index.html": b"new"}, dest)
            self.assertEqual((dest / "notes.txt").read_text(), "keep")
