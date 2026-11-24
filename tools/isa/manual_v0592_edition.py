"""Release authority and offline catalog projection for the v0.59.2 reader."""

from functools import lru_cache
from hashlib import sha256
import json
import subprocess

from manual_tag import REPO_ROOT

TAG = "v0.59.2"
COMMIT = "830fbdb53bccec889414b5673ffba31b0a08606d"
CATALOG = "isa/v0.59.2/linxisa-v0.59.2.json"
MANIFEST = "isa/v0.59.2/release_manifest.json"


@lru_cache(maxsize=1)
def verified_commit():
    oid = subprocess.check_output(
        ["git", "rev-parse", f"refs/tags/{TAG}^{{commit}}"], cwd=REPO_ROOT, text=True
    ).strip()
    if oid != COMMIT:
        raise ValueError(f"{TAG} does not resolve to the reviewed release commit")
    return oid


@lru_cache(maxsize=None)
def read(path):
    return subprocess.check_output(
        ["git", "show", f"{verified_commit()}:{path}"], cwd=REPO_ROOT
    )


def projection(rows):
    # The full machine specification also contains historical state and encoding
    # reservations. Only the separately named reader projection ships offline.
    return json.dumps(
        {
            "schema": "linxisa.manual.instruction-forms.v1",
            "version": "0.59.2",
            "source_commit": COMMIT,
            "source_catalog_sha256": sha256(read(CATALOG)).hexdigest(),
            "instruction_count": len(rows),
            "instructions": [
                {
                    **row,
                    "uop_class": {
                        key: value
                        for key, value in row["uop_class"].items()
                        if key != "note"
                    },
                }
                if "uop_class" in row
                else row
                for row in rows
            ],
        },
        ensure_ascii=False,
        indent=2,
    ).encode()


def tile_projection(tiles):
    # Four current comparison/selection roles call their still-assigned
    # RowMajor packed carrier "legacy Predicate". Preserve the carrier and its
    # alternatives, using the packing/layout name from the locked owners.
    operations = [
        {
            **op,
            "operands": [
                {
                    **operand,
                    "role": operand["role"].replace(
                        "legacy Predicate", "RowMajor packed Predicate"
                    ),
                }
                for operand in op["operands"]
            ],
        }
        for op in tiles["operations"]
    ]
    return json.dumps(
        {
            "schema": "linxisa.manual.tile-operations.v1",
            "version": "0.59.2",
            "source_commit": COMMIT,
            "source_catalog_sha256": sha256(
                read("isa/v0.59/state/pto_tile_operations.json")
            ).hexdigest(),
            "operation_count": len(operations),
            "operations": operations,
        },
        ensure_ascii=False,
        indent=2,
    ).encode()


@lru_cache(maxsize=1)
def release_decoder():
    """Reproduce the actual tagged Sail package decoder, including its catalog identity."""
    import tempfile
    import sys
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="linx-0592-manual-decode-") as tmp:
        out = Path(tmp) / "decode.sail"
        subprocess.run(
            [
                sys.executable,
                "tools/isa/gen_sail_decode.py",
                "--spec",
                CATALOG,
                "--out",
                str(out),
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        data = out.read_bytes()
    if (
        sha256(data).hexdigest()
        != "cb7517c78a3d591008b2c3a36860147a46ec67241d13237ea4530deffbff0f7a"
    ):
        raise ValueError(
            "generated decoder differs from the v0.59.2 Sail release package"
        )
    return data


def install(files, dest, *, check=False):
    """An older edition can contain HTML, diagrams and manuscripts absent from this one."""
    import os
    import tempfile
    from pathlib import Path

    existing = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
    stale = existing - files.keys()
    if check:
        if stale:
            raise ValueError(f"unexpected file in manual: {min(stale)}")
        for name, data in files.items():
            if not (dest / name).is_file() or (dest / name).read_bytes() != data:
                raise ValueError(f"out of date: {dest / name}")
        return
    if not stale:
        for name, data in files.items():
            path = dest / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return
    # Keep possible user files and the previous edition out of the new site.
    # Only rotate a recognized generated manual, after staging its replacement.
    audit = dest / "audit.json"
    if not audit.is_file() or json.loads(audit.read_text()).get("tag") not in {
        "v0.59.1",
        TAG,
    }:
        raise ValueError(
            f"output directory contains an unrelated file: {dest / min(stale)}"
        )
    with tempfile.TemporaryDirectory(dir=dest.parent, prefix=".manual-stage-") as tmp:
        site = Path(tmp) / "site"
        install(files, site)
        archive = Path(
            tempfile.mkdtemp(dir=dest.parent, prefix=dest.name + "-previous-")
        )
        os.replace(dest, archive)
        try:
            os.replace(site, dest)
        except OSError:
            os.replace(archive, dest)
            raise
        print(f"Previous local manual preserved in {archive}")
