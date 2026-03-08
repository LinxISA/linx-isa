# LinxISA Sail Model (v0.4)

This directory contains the active **Sail** formal and executable model for canonical LinxISA `v0.4`.

Scope policy:

- The Sail model is an executable reference for `v0.4` semantics and legality checks.
- Semantic readiness is tracked only in `isa/sail/semantics_status.json`.
- Coverage is tracked as data in `isa/sail/coverage.json`.

## Coverage report

`isa/sail/coverage.json` is generated from:

- the compiled ISA catalog: `isa/v0.4/linxisa-v0.4.json`
- the semantic status map: `isa/sail/semantics_status.json`

Regenerate:

```bash
python3 tools/bringup/check_sail_model.py --require-parser
```

## Layout

- `isa/sail/model/linxisa.sail`: top-level canonical Sail entry
- `isa/sail/model/linxisa.sail_project`: project wrapper pointing at the canonical entry
- `isa/sail/model/lib/`: shared helpers
- `isa/sail/model/state/`: architectural state definitions
- `isa/sail/model/decode/`: decode model
- `isa/sail/model/execute/`: per-unit execute semantics
- `isa/sail/semantics_status.json`: machine-readable semantic readiness status
