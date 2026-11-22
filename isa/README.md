# LinxISA Specification

`isa/` is the canonical specification root for the public LinxISA repository.

The [0.59.1 specification release](../docs/releases/v0.59.1.md) publishes the v0.59 catalog and Sail model. The following defaults apply to platform bring-up.

## Canonical Artifacts

- Latest stable profile package: `isa/v0.58/`
- Latest stable generated catalog components: `isa/v0.58/{encoding,opcodes,registers,state,meta.json}`
- Latest stable compiled catalog: `isa/v0.58/linxisa-v0.58.json`
- Historical profiles: retained as the repository's versioned history and not used as the live contract
- Generated codec tables: `isa/generated/codecs/`
- Sail model + coverage assets: `isa/sail/`

## Build + Validate

```bash
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/check_canonical_v058.py --root .
```

## Downstream Consumption

Compiler, emulator, benchmark, model, and TileOP API integration MUST consume
the v0.58 stable profile artifacts to avoid decode/semantic drift.

See also:

- `isa/generated/codecs/README.md`
