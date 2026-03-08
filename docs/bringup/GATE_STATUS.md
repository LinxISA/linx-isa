# Bring-up Gate Status (AVS-first)

Last refreshed: 2026-03-07

This page summarizes the checked-in AVS-first bring-up status for canonical `v0.4`.

## Canonical Status Sources

- AVS contract: `avs/linx_avs_v1_test_matrix.yaml`
- AVS status: `avs/linx_avs_v1_test_matrix_status.json`
- QEMU decode coverage: `docs/bringup/gates/qemu_isa_coverage_latest.json`
- Architecture contract: `docs/architecture/v0.4-architecture-contract.md`

## Current Snapshot

| Area | Status | Evidence |
| --- | --- | --- |
| Golden/spec validation | ✅ | `python3 tools/isa/build_golden.py --profile v0.4 --check`; `python3 tools/isa/validate_spec.py --profile v0.4` |
| AVS contract schema | ✅ | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| AVS tier closure | ❌ Open work | `20/54` active entries in `avs/linx_avs_v1_test_matrix_status.json` are currently `pass` for both `pr` and `nightly` |
| Sail strict model gate | ✅ | `python3 tools/bringup/check_sail_model.py --require-parser` |
| Compiler compile coverage | ✅ | `avs/compiler/linx-llvm/tests/run.sh`; `analyze_coverage.py --fail-under 100` |
| QEMU runtime baseline | ✅ | `avs/qemu/check_system_strict.sh`; `avs/qemu/run_tests.sh --all` |
| QEMU decode-spectrum closure | ❌ Open work | `524/710` legal `v0.4` mnemonics and `521/740` legal forms in `docs/bringup/gates/qemu_isa_coverage_latest.json` |
| Linux smoke/full boot | ✅ | `kernel/linux/tools/linxisa/initramfs/smoke.py`; `full_boot.py` |
| musl runtime baseline | ✅ | `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both` |
| glibc baseline | ✅ | `bash lib/glibc/tools/linx/build_linx64_glibc.sh`; `build_linx64_glibc_g1b.sh` |
| Workload/SPEC hard closure | ❌ Open work | AVS workload and SPEC entries are active but not all validated |

## Required Canonical Gates

```bash
python3 tools/isa/build_golden.py --profile v0.4 --check
python3 tools/isa/validate_spec.py --profile v0.4
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/gen_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --source-status avs/linx_avs_v1_test_matrix_status.json --out avs/linx_avs_v1_test_matrix_status.json
python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json
python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr
python3 tools/bringup/check_sail_model.py
python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full
```

## Notes

- `docs/bringup/gates/latest.json` remains the per-run gate evidence artifact, but it predates the AVS contract cutover and must be refreshed by a new strict run before it is used as release evidence.
- The checked-in AVS status file already includes Linux, libc, workload, and SPEC rows, so closure work now happens by filling those entries with executable evidence rather than by adding a second contract source.
