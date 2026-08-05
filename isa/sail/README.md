# LinxISA Sail Model (v0.58)

This directory contains the active **Sail** formal and executable model for the canonical LinxISA `v0.58` profile.

Scope policy:

- The Sail model is an executable reference for `v0.58` semantics and legality checks.
- The v0.58 surface is built on the retained executable subset; new v0.58 forms are explicit deltas in `semantics_policy.json`.
- `toolchain.json` pins the required OCaml and Sail versions.
- Semantic readiness is graded by stable instruction form ID in `semantics_status.json`.
- Coverage is tracked as data in `isa/sail/coverage.json`.

## Coverage report

`isa/sail/coverage.json` is generated from:

- the compiled ISA catalog: `isa/v0.58/linxisa-v0.58.json`
- the generated form status map: `isa/sail/semantics_status.json`

Regenerate:

```bash
python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend
python3 tools/isa/gen_sail_status.py --check
python3 tools/isa/sail_coverage.py --spec isa/v0.58/linxisa-v0.58.json --check
```

## Layout

- `isa/sail/model/linxisa.sail`: top-level canonical Sail entry
- `isa/sail/model/linxisa.sail_project`: project wrapper pointing at the canonical entry
- `isa/sail/model/lib/`: shared helpers
- `isa/sail/model/state/`: architectural state definitions
- `isa/sail/model/decode/`: decode model
- `isa/sail/model/execute/`: per-unit execute semantics
- `isa/sail/tests/directed.sail`: executable block/return/trap/atomic/FP edge checks
- `isa/sail/semantics_status.json`: machine-readable semantic readiness status
- `isa/sail/semantics_policy.json`: default grade and explicit form-ID overrides
- `isa/sail/toolchain.json`: hermetic Sail/OCaml version pin
