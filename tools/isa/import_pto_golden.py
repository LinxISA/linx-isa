#!/usr/bin/env python3
"""Project the exact PTO development golden into the Linx design."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

import import_pto_v0580 as published

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "isa/v0.58"
LOCK = PROFILE / "pto-scalar-proposal.lock.json"
SOURCE = "f0a876e449a95d26841c5ee7affb4c905ebc5f5b"
TREE = "fe9e8e050375fbce3f526d08acca13c37cd15830"
SOURCE_LOCK = "isa/v0.58/pto-scalar-proposal.lock.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def render(document):
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def build(source):
    for ref, expected in (("HEAD", SOURCE), ("HEAD^{tree}", TREE)):
        actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", ref], text=True).strip()
        if actual != expected:
            raise ValueError(f"PTO golden {ref} differs from frozen source")
    manifest_path = source / "spec/development-manifest.json"
    manifest = read(manifest_path)
    if manifest["status"] != "development-not-published" or manifest["publication"] is not None:
        raise ValueError("expected a development golden, without publication authority")
    if manifest["catalog_counts"] != {"scalar_forms": 473, "command_forms": 105, "tile_operations": 119, "reservations": 50}:
        raise ValueError("unexpected reviewed golden inventory")
    inputs = {name: source / entry["path"] for name, entry in manifest["catalogs"].items()}
    inputs["manifest"] = manifest_path
    for name, path in inputs.items():
        frozen = subprocess.check_output(["git", "-C", str(source), "show", f"{SOURCE}:{path.relative_to(source)}"])
        if path.read_bytes() != frozen:
            raise ValueError(f"dirty golden source: {path}")
        if name != "manifest" and sha(frozen) != manifest["catalogs"][name]["sha256"]:
            raise ValueError(f"stale golden catalog hash: {name}")
    catalogs = {name: read(path) for name, path in inputs.items() if name != "manifest"}
    lock = {
        "status": "development-not-published",
        "source": {"repository": "https://github.com/PTO-ISA/pto-spec.git", "commit": SOURCE, "tree": TREE,
                   "pull_request": "https://github.com/PTO-ISA/pto-spec/pull/390"},
        "development_manifest": {"path": "spec/development-manifest.json", "sha256": sha(manifest_path.read_bytes())},
        "identity": manifest["identity"],
        "catalogs": {("extension_encoding_reservations" if name == "reservations" else name):
                     {**entry, "count": manifest["catalog_counts"].get(name)}
                     for name, entry in manifest["catalogs"].items()},
        "catalog_counts": manifest["catalog_counts"],
        "effective_forms_sha256": sha(json.dumps(catalogs["scalar_forms"]["forms"], sort_keys=True, separators=(",", ":")).encode()),
        "published_identity_compatible": False,
    }
    # The immutable published lock remains a historical baseline. Every active
    # common projection below names the development golden as its authority.
    upstream_manifest = read(source / "spec/release-manifest.json")
    upstream_manifest["catalog_counts"]["command_form_families"] = dict(Counter(form["semantic_family"] for form in catalogs["command_forms"]["forms"]))
    docs = {"manifest": upstream_manifest, "tiles": catalogs["tile_operations"],
            "commands": catalogs["command_forms"], "scalars": catalogs["scalar_forms"],
            "reservations": catalogs["reservations"]}
    published.EXTENSION_RESERVATION_COUNT = 50
    artifacts = published.projections(docs)
    for document in artifacts.values():
        if "source_lock" in document:
            document["source_lock"] = SOURCE_LOCK
    artifacts[PROFILE / "release_manifest.json"].update({"status": "development-not-published", "identity": manifest["identity"], "publication": None})
    binders = {}
    for name, path in {
        "B.IOT": "asl/block/operands/B.IOT.asl",
        "B.IOS": "asl/block/operands/B.IOS.asl",
        "B.IOR": "asl/block/operands/B.IOR.asl",
        "B.DATR": "asl/block/attributes/B.DATR.asl",
    }.items():
        raw = subprocess.check_output(["git", "-C", str(source), "show", f"{SOURCE}:{path}"])
        metadata = json.loads(raw.decode().splitlines()[0].split(": ", 1)[1])
        binders[name] = {"source": path, "sha256": sha(raw), "contract": metadata["contract"]}
    artifacts[PROFILE / "state/pto_binder_contracts.json"] = {"source_lock": SOURCE_LOCK, "instructions": binders}
    artifacts[LOCK] = lock
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = published.compare_or_write(build(args.source_root.resolve()), args.check)
    if errors:
        raise SystemExit("\n".join(errors))
    print("OK: Linx projections match the exact PTO development golden")


if __name__ == "__main__":
    main()
