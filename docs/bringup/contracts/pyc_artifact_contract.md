# pyCircuit Artifact Contract

## Authority and source roots

- pyCircuit source of truth can be either:
  - the pinned submodule: `tools/pyCircuit` (recommended for reproducibility), or
  - an external checkout (set `PYCIRCUIT_ROOT=/path/to/pyCircuit`).
- Linx CPU source root:
  - `tools/pyCircuit/examples/linx_cpu_pyc`
- Janus source root:
  - `tools/pyCircuit/janus/pyc/janus`

`linxisa` does not manually author these RTL/model sources.

## Required generated outputs

For each tracked core target:

- Verilog RTL: `*.v`
- C++ cycle model headers: `*_gen.hpp`
- Testbench execution logs (C++ and RTL simulation paths)

Recommended generated locations in pyCircuit:

- Linx generated artifacts: `tools/pyCircuit/examples/generated/linx_cpu_pyc/`
- Janus generated artifacts: `tools/pyCircuit/janus/generated/`

## Canonical generation entrypoints

- `bash tools/pyCircuit/scripts/pyc build`
- `bash tools/pyCircuit/scripts/pyc regen`
- `bash tools/pyCircuit/janus/update_generated.sh`

If using an external checkout, prefix those paths with `$PYCIRCUIT_ROOT/` instead.

## Reproducibility rules

- Generated artifacts copied/staged into `linxisa` must come from scripts, not manual edits.
- Every bring-up gate must record the command used and artifact origin.
- If generator versions change, note the version/commit in gate notes.
