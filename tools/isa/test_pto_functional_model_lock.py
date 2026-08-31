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

    def test_result_hash_mutation_fails_closed(self):
        payload = json.loads(LOCK.read_text(encoding="utf-8"))
        payload["validated_results"]["scalar_stop_pc"]["result_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "lock.json"
            mutated.write_text(json.dumps(payload), encoding="utf-8")
            result = self.run_checker(mutated)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scalar_stop_pc result hash mismatch", result.stderr)

    def test_required_component_must_be_initialized(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("functional_lock", CHECKER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        commit = "1" * 40
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                [
                    "git", "update-index", "--add", "--cacheinfo",
                    f"160000,{commit},tools/consumer",
                ],
                cwd=root,
                check=True,
            )
            with self.assertRaisesRegex(ValueError, "required initialized submodule"):
                checker.validate_component(
                    root,
                    {"path": "tools/consumer", "commit": commit, "tree": "2" * 40},
                    "consumer",
                )


if __name__ == "__main__":
    unittest.main()
