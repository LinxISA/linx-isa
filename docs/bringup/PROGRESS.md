# Bring-up Progress (v0.58)

Last updated: 2026-08-10

## Current architecture baseline

- `isa/v0.58/linxisa-v0.58.json` is the canonical ISA catalog.
- `isa/v0.58/pto-spec.lock.json` pins the released PTO common subset.
- The semantic engines are `VEC`, `TLSU`, `CUBE`, and `SFU`; TEPL remains an
  unchanged encoding carrier and is not an engine.
- LLVM, QEMU, and Linux gitlinks are updated to their merged v0.58-compatible
  commits.
- `tools/Linx-TileOP-API` is the active Tile API component.
- SuperNPU sources are nested under
  `workloads/pto_kernels/benchmarks/supernpu`; the standalone SuperNPUBench
  gitlink is removed.

## Evidence policy

Only exact-head v0.58 results may be promoted as current evidence. Historical
v0.57 reports and the retired AVS Tile/PTO parity suites are archived and do
not transfer pass status to v0.58. Pending, skipped, missing-tool, or
different-SHA results are not success.

## Current checked-in status

| Surface | Status | Evidence |
| --- | --- | --- |
| ISA catalog and PTO lock | Released | v0.58 catalog, manifest, and PTO lock |
| Component topology | Required check | `python3 tools/ci/check_component_lock.py --root .` |
| Linx-TileOP-API | Required check | `make -C tools/Linx-TileOP-API check` |
| Nested SuperNPU source contract | Required check | `python3 workloads/pto_kernels/scripts/check_supernpu_v058.py` |
| QEMU decode inventory | Partial | 728/728 mnemonics and 759/766 forms; L2/L3 unavailable in the checked-in report |
| AVS Tile/PTO runtime | Open | Rebuild on v0.58 components; tracked by issue 169 |
| Full runtime/model/nightly closure | Open | Must be rerun on one exact component manifest |

## Canonical commands

```bash
bash tools/ci/check_repo_layout.sh
python3 tools/ci/check_component_lock.py --root .
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/check_pto_v058_manifest.py --root .
python3 tools/isa/check_canonical_v058.py --root .
python3 tools/isa/check_agent_navigation.py --root .
make -C tools/Linx-TileOP-API check
python3 workloads/pto_kernels/scripts/check_supernpu_v058.py
python3 docs/check_documentation.py --root .
```

Generated gate pages are views. The component lock, v0.58 catalog, AVS
matrix/status, and exact run manifests are the machine-readable authorities.
