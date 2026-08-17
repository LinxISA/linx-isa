# Bring-up Progress (v0.58.1)

Last updated: 2026-08-17

## Current architecture baseline

- `isa/v0.58/linxisa-v0.58.json` is the canonical ISA catalog.
- `isa/v0.58/pto-spec.lock.json` pins the released PTO common subset.
- The semantic engines are `VEC`, `TLSU`, `CUBE`, and `SFU`; TEPL remains an
  unchanged encoding carrier and is not an engine.
- LLVM, QEMU, and Linux gitlinks are updated to their merged v0.58.1-compatible
  commits.
- `tools/Linx-TileOP-API` is the active Tile API component.
- SuperNPU sources are nested under
  `workloads/pto_kernels/benchmarks/supernpu`; the standalone SuperNPUBench
  gitlink is removed.

## Evidence policy

Only exact-head v0.58.1 results may be promoted as current evidence. Historical
v0.57 reports and the retired AVS Tile/PTO parity suites are archived and do
not transfer pass status to v0.58.1. Pending, skipped, missing-tool, or
different-SHA results are not success.

## Current checked-in status

| Surface | Status | Evidence |
| --- | --- | --- |
| ISA catalog and PTO lock | Released | v0.58.1 catalog projection, manifest, and PTO lock |
| Component topology | Required check | `python3 tools/ci/check_component_lock.py --root .` |
| Linx-TileOP-API | Required check | `make -C tools/Linx-TileOP-API check` |
| Nested SuperNPU source contract | Required check | `python3 workloads/pto_kernels/scripts/check_supernpu_v058.py` |
| QEMU decode inventory | L1 complete | 731/731 mnemonics and 765/765 forms; L2/L3 remain separate runtime evidence levels |
| AVS Tile/PTO runtime | Verified | Exact merged QEMU passed native Tile tests, strict system AVS, and the full AVS suite |
| Cross-model release closure | Verified | Seven ordered release-strict cases passed on one exact compiler/QEMU/model manifest; see `docs/bringup/gates/model_diff_release-strict.json` |
| Broader nightly and benchmark closure | Open | Nightly workload breadth remains separate from the release-strict result-memory proof |

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
python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json
python3 docs/check_documentation.py --root .
```

Generated gate pages are views. The component lock, v0.58 catalog, AVS
matrix/status, and exact run manifests are the machine-readable authorities.
