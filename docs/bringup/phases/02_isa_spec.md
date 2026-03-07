# Phase 2: ISA Spec Integration

Source of truth: `isa/v0.4/**` (compiled to `isa/v0.4/linxisa-v0.4.json`)

Supporting context:
- `isa/README.md`
- `isa/generated/codecs/` (generated decode/encode artifacts)

## Rule

Compiler, emulator, and RTL behavior must be derived from, or checked against, the same catalog.

## Regeneration

```bash
python3 tools/isa/build_golden.py --profile v0.4 --pretty
python3 tools/isa/validate_spec.py --spec isa/v0.4/linxisa-v0.4.json
```
