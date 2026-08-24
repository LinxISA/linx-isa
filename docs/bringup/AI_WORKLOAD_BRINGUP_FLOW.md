# AI workload bring-up flow

The active v0.58 flow discovers SuperNPU cases only from
`workloads/pto_kernels/benchmarks/supernpu` and compiles them against the exact
`tools/Linx-TileOP-API` gitlink. The machine-readable contract is
`docs/bringup/ai_workload_bringup_flow.json`.

```bash
python3 tools/bringup/run_ai_workload_flow.py --profile smoke --list
python3 tools/bringup/run_ai_workload_flow.py --profile smoke --dry-run
python3 tools/bringup/run_ai_workload_flow.py --profile smoke --run-id <run-id>
```

Artifacts are written below `workloads/generated/<run-id>/ai-bringup/`.
`--list` is read-only and creates no run directory. `--dry-run` skips toolchain,
QEMU, and model execution, but still writes the run manifest, report, logs, and
summary artifacts. A dry-run records the configured or default QEMU candidate
path even when no binary exists. A real run with valid exact-pin evidence keeps
the strict HEAD-matched clean-QEMU selection requirement; invalid exact pins
hard-break at `source-contract` before QEMU resolution can hide the mismatch.

## Architecture boundary

The semantic engines are exactly VEC, TLSU, CUBE, and SFU. VEC performs only
element-wise operations. SFU owns operations that require complex or irregular
hardware. TEPL is not an engine; it remains the unchanged Mode/Function
encoding carrier used by the `BSTART.VEC` and `BSTART.SFU` assembly aliases.

The retired v0.57 PTO-Kernel API, standalone SuperNPUBench submodule, and
`tile`, `pto_parity`, and `deepseek_tilekernels` AVS suites are not active
v0.58 inputs. Their historical QEMU sources live under
`avs/archive/v0.57/qemu/`. Fresh runtime AVS is tracked by
[issue 169](https://github.com/LinxISA/linx-isa/issues/169); archived evidence
does not satisfy that issue.

The current tier-0 smoke inventory is the nested, active VEC
`tadd_fp32_16x16`, TLSU `tload_fp32_16x16`, and Local CELL CUBE
`tmatmul_fp16_32x64x64` cases. Discovery accepts the active microbenchmark
`compile.all` files' guarded `run_case <testcase>` rows as the equivalent
single-case `make TESTCASE=<testcase>` command; arbitrary shell calls are not
accepted as manifest rows.

## Required component checks

```bash
make -C tools/Linx-TileOP-API check
python3 workloads/pto_kernels/scripts/check_supernpu_v058.py
python3 tools/bringup/check_tepl_encoding.py --root .
```

These checks validate the API, corpus, engine aliases, and encoding consumers.
They do not turn missing QEMU or model execution into a pass.

## Stages

1. `source-contract` first requires every `.gitmodules` checkout SHA to match
   both the superproject gitlink and its `component-lock.v0.58.json` entry, and
   requires the checkout tree plus `.gitmodules` URL/branch to match a complete
   lock entry with URL, branch, role, and tree. Missing or dirty checkouts,
   incomplete metadata, and any non-`landed` integration status fail closed
   before validating nested `compile.all` rows and hashes.
2. `compiler-contract` builds with pinned Linx LLVM and Linx-TileOP-API.
3. `qemu-execution` requires a fresh ELF and explicit terminal oracle.
4. `model-build-smoke` proves the current LinxCoreModel binary.
5. `linxcoremodel-execution` runs only QEMU-passing ELFs.
6. `differential-triage` compares independent evidence.
7. `fix-packets` records the first failing owner.
8. `skill-doc-evolution` records reusable workflow changes.

The runner stops at the first hard-break failure unless
`--continue-on-fail` is supplied for diagnosis. A missing, skipped, pending, or
stale result is never conformance evidence.
