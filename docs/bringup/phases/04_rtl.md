# Phase 4: RTL Bring-up and Verification (Agile pyCircuit)

Primary RTL notes: `rtl/README.md`

## Scope and source of truth

- Architecture/spec authority: `linxisa` (`isa/v0.3/`, `isa/v0.3/linxisa-v0.3.json`, `isa/generated/codecs/`).
- RTL/model generation authority:
  - pinned submodule: `tools/pyCircuit` (recommended for reproducibility)
  - or an external checkout (set `PYCIRCUIT_ROOT=/path/to/pyCircuit`).
- Core targets:
  - **Linx CPU** first
  - **Janus Core** second

The Linux end goal is handled in later phases (`05_fpga_zybo_z7.md`, `06_linux_on_janus.md`), but this phase must
produce stable and diffable models/RTL as prerequisites.

## Contracts (mandatory links)

- Artifact contract: `docs/bringup/contracts/pyc_artifact_contract.md`
- Trace contract: `docs/bringup/contracts/trace_schema.md`
- FPGA platform defaults (for downstream compatibility): `docs/bringup/contracts/fpga_platform_contract.md`

## Required architecture alignment

- Control-flow targets must land on block start markers.
- Block boundaries must commit at `BSTOP` or next block start.
- `SETC.*` must execute inside a block and feed commit-time control-flow.
- Template blocks (`FENTRY`/`FEXIT`/`FRET.*`) are standalone blocks.

## Workstream A: Linx CPU agile loop

### Entry criteria

- Compiler and QEMU regressions are green in `linxisa`.
- `pyCircuit` toolchain builds (`scripts/pyc build`) and can regenerate outputs (`scripts/pyc regen`).

### Implementation loop

One sprint = one feature slice (instruction/CSR/exception/pipeline rule):

1. Implement/update pyCircuit source in:
   - `tools/pyCircuit/examples/linx_cpu_pyc/` (or `$PYCIRCUIT_ROOT/examples/linx_cpu_pyc/`)
2. Regenerate C++ and Verilog artifacts via canonical scripts.
3. Run C++ and RTL simulations on identical program vectors.
4. Diff against QEMU using the trace contract.

### Canonical runners

- `bash tools/pyCircuit/tools/run_linx_cpu_pyc_cpp.sh`
- `python3 tools/pyCircuit/tools/pyc_flow.py verilog-sim linx_cpu_pyc --tool verilator`

(If using an external checkout, prefix those paths with `$PYCIRCUIT_ROOT/`.)

### Exit criteria

- Smoke suite passes in both C++ and RTL simulation.
- No unresolved divergence against QEMU in supported instruction subsets.
- Artifacts are reproducible and script-generated (no manual edits).

## Workstream B: Janus Core stabilization

### Entry criteria

- Workstream A exit criteria complete.
- Janus generated artifacts can be refreshed from source in `tools/pyCircuit/janus` (or `$PYCIRCUIT_ROOT/janus`).

### Canonical runners

- `bash tools/pyCircuit/janus/tools/run_janus_bcc_ooo_pyc_cpp.sh`
- `bash tools/pyCircuit/janus/tools/run_janus_bcc_ooo_pyc_sv.sh`
- `bash tools/pyCircuit/janus/tools/run_janus_bcc_ooo_pyc_verilator.sh`
- `bash tools/pyCircuit/janus/tools/run_janus_benchmarks.sh`

(If using an external checkout, prefix those paths with `$PYCIRCUIT_ROOT/`.)

### Validation

- Reuse identical vectors where Linx and Janus ISA behavior overlaps.
- Add Janus-specific difftest gates against QEMU for supported subsets.
- Keep unsupported features explicitly marked as out-of-scope for current gate.

### Exit criteria

- Janus C++ and Verilog simulations pass defined smoke programs.
- Benchmark scripts run and produce consistent architectural outcomes.
- Remaining deltas are documented with owners and blockers.

## Artifact ingestion into `linxisa`

`linxisa` stores planning, contracts, and validation outcomes. When needed, stage generated integration collateral into:

- `rtl/` for integration wrappers or snapshots
- `models/` for model wrappers and trace adapters
- `tools/` for reproducible import/check scripts

Direct authoring remains in pyCircuit (pinned `tools/pyCircuit` or external `$PYCIRCUIT_ROOT`); copied artifacts in `linxisa` must be script-derived.
