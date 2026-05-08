# LinxISA ISA Tooling (v0.56)

These tools operate on the canonical LinxISA v0.56 catalog.

- Golden source root: `isa/v0.56/`
- Compiled catalog: `isa/v0.56/linxisa-v0.56.json`
- Generated codecs: `isa/generated/codecs/`

## Core Commands

Build catalog:

```bash
python3 tools/isa/build_golden.py --profile v0.56 --pretty
```

Validate catalog:

```bash
python3 tools/isa/validate_spec.py --profile v0.56
```

Generate decode tables:

```bash
python3 tools/isa/gen_qemu_codec.py --profile v0.56 --out-dir isa/generated/codecs
python3 tools/isa/gen_c_codec.py --profile v0.56 --out-dir isa/generated/codecs
```

Generate manual fragments:

```bash
python3 tools/isa/gen_manual_adoc.py --profile v0.56 --out-dir docs/architecture/isa-manual/src/generated
python3 tools/isa/gen_instruction_fragments.py --profile v0.56 --out-dir docs/architecture/isa-manual/src/generated/instructions
python3 tools/isa/gen_ssr_adoc.py --profile v0.56 --out-dir docs/architecture/isa-manual/src/generated
```

Run the active canonical-content guard:

```bash
python3 tools/isa/check_canonical_v056.py --root .
```
