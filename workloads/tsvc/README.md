# TSVC Workflow

This folder provides a reproducible TSVC workflow for Linx SIMT auto-vectorization
assembly inspection.

## Source policy

- Preferred source location: `workloads/tsvc/upstream/TSVC_2/src`
- Pinned upstream commit: `badf9adb2974867ac0937718d85a44dec6dec95a`
- Fetch helper: `workloads/tsvc/fetch_tsvc.sh`

## Generate auto-mode objdumps + QEMU validation

```bash
python3 workloads/tsvc/run_tsvc.py \
  --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang \
  --qemu $PWD/emulator/qemu/build/qemu-system-linx64 \
  --source-policy linx-v03-parity \
  --vector-mode auto
```

Artifacts are written under `workloads/generated/`:

- `objdump/tsvc/tsvc.auto.objdump.txt`
- `objdump/tsvc/kernels/auto/*.objdump.txt`
- `qemu/tsvc/tsvc.auto.stdout.txt`
- `qemu/tsvc/tsvc.auto.stderr.txt`
- `reports/tsvc/vectorization_coverage.auto.{md,json}`
- `reports/tsvc/vectorization_remarks.auto.json`
- `reports/tsvc/vectorization_gap_plan.auto.json`
- `reports/tsvc/gate_result.json` (canonical machine-readable gate artifact)

## Optional checksum parity gate

1. Build baseline:

```bash
python3 workloads/tsvc/run_tsvc.py \
  --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang \
  --qemu $PWD/emulator/qemu/build/qemu-system-linx64 \
  --source-policy linx-v03-parity \
  --vector-mode off
```

2. Run candidate with parity enforcement:

```bash
python3 workloads/tsvc/run_tsvc.py \
  --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang \
  --qemu $PWD/emulator/qemu/build/qemu-system-linx64 \
  --source-policy linx-v03-parity \
  --vector-mode auto \
  --compare-baseline-log workloads/generated/qemu/tsvc/tsvc.off.stdout.txt \
  --fail-on-checksum-mismatch
```

`--source-policy` controls staged-source behavior only:

- `linx-v03-parity` (default): applies Linx v0.3 parity canonicalizations in staged
  `tsvc.c` (currently `s2111` `/1.9 -> /1.9f`).
- `upstream`: uses staged sources without parity canonicalization.
