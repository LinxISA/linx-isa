import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/isa/check_pto_functional_model_lock.py"
LOCK = ROOT / "isa/v0.58/pto-functional-model.lock.json"


class PtoFunctionalModelLockTest(unittest.TestCase):
    def run_checker(self, lock: Path = LOCK):
        return subprocess.run(
            ["python3", str(CHECKER), "--root", str(ROOT), "--lock", str(lock)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_exact_repository_lock_passes(self):
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PTO functional-model lock passed", result.stdout)

    def test_consumer_mutation_fails_closed(self):
        payload = json.loads(LOCK.read_text(encoding="utf-8"))
        payload["consumer"]["commit"] = "0" * 40
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "lock.json"
            mutated.write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_checker(mutated)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("consumer gitlink mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
