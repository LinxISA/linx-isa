# LinxISA Specification

`isa/` is the canonical specification root for the public LinxISA repository.

## Canonical Artifacts

- Latest stable profile package: `isa/v0.57/`
- Latest stable generated catalog components: `isa/v0.57/{encoding,opcodes,registers,state,meta.json}`
- Latest stable compiled catalog: `isa/v0.57/linxisa-v0.57.json`
- Historical profiles: retained as the repository's versioned history and not used as the live contract
- Generated codec tables: `isa/generated/codecs/`
- Sail model + coverage assets: `isa/sail/`

## Build + Validate

```bash
python3 tools/isa/build_golden.py --profile v0.57 --check
python3 tools/isa/validate_spec.py --profile v0.57
python3 tools/isa/check_canonical_v057.py --root .
```

## Downstream Consumption

Compiler, emulator, benchmark, model, and TileOP API integration MUST consume
the v0.57 stable profile artifacts to avoid decode/semantic drift.

See also:

- `isa/generated/codecs/README.md`
