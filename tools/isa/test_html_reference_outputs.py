from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from gen_html_reference import remove_stale_outputs


class GeneratedOutputTest(unittest.TestCase):
    def test_removed_form_is_deleted_only_after_all_files_are_verified(self):
        with TemporaryDirectory() as folder:
            out = Path(folder)
            retired = out / "op-v-add.html"
            retired.write_bytes(b"generated")
            (out / "generated-files.json").write_text(
                json.dumps(
                    {"files": {retired.name: sha256(retired.read_bytes()).hexdigest()}}
                )
            )
            (out / "notes.txt").write_text("local notes")
            with self.assertRaises(SystemExit):
                remove_stale_outputs(out, [retired.name, "notes.txt"], None)
            self.assertTrue(retired.exists())
            remove_stale_outputs(out, [retired.name], None)
            self.assertFalse(retired.exists())
            self.assertEqual((out / "notes.txt").read_text(), "local notes")

    def test_first_upgrade_checks_previous_zip_bytes(self):
        with TemporaryDirectory() as folder:
            out = Path(folder)
            path = out / "class-vec.html"
            archive = out / "previous.zip"
            with ZipFile(archive, "w") as bundle:
                bundle.writestr(path.name, "previous")
            path.write_text("modified")
            with self.assertRaises(SystemExit):
                remove_stale_outputs(out, [path.name], archive)
            path.write_text("previous")
            remove_stale_outputs(out, [path.name], archive)
            self.assertFalse(path.exists())
