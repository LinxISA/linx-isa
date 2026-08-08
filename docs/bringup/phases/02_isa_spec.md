# Phase 2: ISA Spec Integration

Source of truth: `isa/v0.58/linxisa-v0.58.json` and its component artifacts
under `isa/v0.58/`.

Supporting context:
- `isa/README.md`
- `isa/generated/codecs/` (generated decode/encode artifacts)

## Rule

Compiler, emulator, and RTL behavior must be derived from, or checked against, the same catalog.

## Regeneration

```bash
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/check_canonical_v058.py --root .
```
