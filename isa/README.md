# LinxISA Specification (v0.4)

`isa/` is the canonical specification root for the public LinxISA repository.

## Canonical Artifacts

- Source components: `isa/v0.4/{encoding,opcodes,registers,state,meta.json}`
- Compiled catalog: `isa/v0.4/linxisa-v0.4.json`
- Archived historical profile: retained as the repository's versioned history and not used by active defaults
- Generated codec tables: `isa/generated/codecs/`
- Sail model + coverage assets: `isa/sail/`

## Build + Validate

```bash
python3 tools/isa/build_golden.py --profile v0.4 --pretty
python3 tools/isa/validate_spec.py --profile v0.4
```

## Downstream Consumption

Compiler, emulator, and RTL integration MUST consume the compiled v0.4 catalog to avoid decode/semantic drift.

See also:

- `isa/generated/codecs/README.md`
