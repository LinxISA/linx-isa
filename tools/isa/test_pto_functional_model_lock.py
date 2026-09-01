import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/isa/check_pto_functional_model_lock.py"
LOCK = ROOT / "isa/v0.58/pto-functional-model.lock.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("functional_lock", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CHECKER}")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    return checker


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_execution_evidence(root: Path, lock: dict) -> tuple[Path, Path]:
    corpus_root = root / "corpus"
    evidence_root = root / "evidence"
    corpus_root.mkdir()
    evidence_root.mkdir()
    toolchain = {
        "clang": "clang",
        "clang_sha256": lock["toolchain"]["clang_sha256"],
        "clang_version": f"clang {lock['toolchain']['commit']}",
        "lld": "ld.lld",
        "lld_sha256": lock["toolchain"]["lld_sha256"],
        "lld_version": f"LLD {lock['toolchain']['commit']}",
        "readelf": "llvm-readelf",
        "readelf_sha256": lock["toolchain"]["readelf_sha256"],
        "readelf_version": f"LLVM {lock['toolchain']['commit']}",
    }
    identity = json.loads(
        (ROOT / "tools/asl-model/pto-lock.json").read_text(encoding="utf-8")
    )
    rows = []
    stop_pcs = {
        "scalar_stop_pc": 0x114,
        "block_64_stop_pc": 0x280,
        "tile_tadd_stop_pc": 0x134,
    }
    for case_id, locked in lock["validated_results"].items():
        artifact = corpus_root / case_id
        output = evidence_root / case_id
        artifact.mkdir()
        output.mkdir()
        elf = artifact / f"{case_id}.elf"
        golden = artifact / f"{case_id}.golden.bin"
        elf.write_bytes(f"ELF:{case_id}".encode())
        golden.write_bytes(bytes.fromhex(locked["result_hex"]))
        case_document = {
            "schema": "pto-functional-model-corpus-v1",
            "toolchain": toolchain,
            "case": {
                "id": case_id,
                "inputs": {
                    "source_sha256": locked["source_sha256"],
                    "linker_sha256": locked["linker_sha256"],
                    "builder_sha256": lock["corpus"]["builder_sha256"],
                    "schema_sha256": lock["corpus"]["schema_sha256"],
                    "clang_sha256": lock["toolchain"]["clang_sha256"],
                    "lld_sha256": lock["toolchain"]["lld_sha256"],
                },
                "elf": {
                    "filename": elf.name,
                    "sha256": sha256(elf),
                    "entry": 0x100,
                },
                "golden": {
                    "filename": golden.name,
                    "sha256": sha256(golden),
                    "size": 4,
                },
                "result": {"address": 0x200, "size": 4},
                "stop_policy": {"stop_pc": stop_pcs[case_id], "max_steps": 8},
            },
        }
        case_manifest = artifact / "manifest.json"
        case_manifest.write_text(json.dumps(case_document), encoding="utf-8")
        result = output / "result.bin"
        result.write_bytes(golden.read_bytes())
        run_manifest = {
            "schema": "pto-asl-model-run-v1",
            "status": "passed",
            "identity": identity,
            "final_tpc": stop_pcs[case_id],
            "result": {
                "address": 0x200,
                "bytes_hex": result.read_bytes().hex(),
                "sha256": sha256(result),
                "size": 4,
            },
            "elf": {"sha256": sha256(elf), "entry": 0x100},
            "stop_policy": {"max_steps": 8, "stop_after_hits": 1, "stop_pc": stop_pcs[case_id]},
        }
        (output / "manifest.json").write_text(json.dumps(run_manifest), encoding="utf-8")
        rows.append({
            "id": case_id,
            "directory": case_id,
            "manifest_sha256": sha256(case_manifest),
            "elf_sha256": sha256(elf),
            "golden_sha256": sha256(golden),
        })
    index = corpus_root / "manifest.json"
    index.write_text(json.dumps({
        "schema": "pto-functional-model-corpus-index-v1",
        "toolchain": toolchain,
        "cases": rows,
    }), encoding="utf-8")
    return index, evidence_root


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

    def test_execution_evidence_rejects_self_consistent_lock_mutation(self):
        checker = load_checker()
        payload = json.loads(LOCK.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            corpus_manifest, evidence_root = write_execution_evidence(root, payload)
            checker.validate_execution_evidence(
                ROOT, LOCK, corpus_manifest, evidence_root
            )
            payload["validated_results"]["scalar_stop_pc"]["result_hex"] = "00000000"
            payload["validated_results"]["scalar_stop_pc"]["result_sha256"] = hashlib.sha256(
                bytes.fromhex("00000000")
            ).hexdigest()
            mutated = root / "mutated-lock.json"
            mutated.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "golden bytes differ from locked result"):
                checker.validate_execution_evidence(
                    ROOT, mutated, corpus_manifest, evidence_root
                )

    def test_required_component_must_be_initialized(self):
        checker = load_checker()
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
