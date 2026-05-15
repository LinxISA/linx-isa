# LLVM Backend Implementation Guide

This document is now a historical bring-up note. The previous external
`~/llvm-project`-centric compiler plan is obsolete.

The canonical compiler implementation for this superproject lives in the
checked-in submodule at:

- `compiler/llvm/llvm/lib/Target/LinxV5/`
- `compiler/llvm/clang/lib/Basic/Targets/LinxV5.*`
- `compiler/llvm/clang/lib/Driver/ToolChains/LinxV5*`

Use the in-repo compiler branch and its gate surface as source of truth; do not
route new implementation work to an external `~/llvm-project` checkout.

## Current implementation surface

The active backend is `LinxV5`, not the older `Linx`/`LinxISA` rename plan:

```
compiler/llvm/llvm/lib/Target/LinxV5/
├── LinxV5InstrInfo.td
├── LinxV5ISelLowering.h/cpp
├── LinxV5ISelDAGToDAG.cpp
├── AsmParser/LinxV5AsmParser.cpp
├── MCTargetDesc/LinxV5*.{cpp,h}
└── TargetInfo/LinxV5TargetInfo.cpp
```

## Generating Instruction Patterns

Use the live v0.56 spec and the checked-in compiler tree. Historical references
to `removed-pre-v056-profile` inputs are obsolete.

TableGen/codegen generation helpers still come from this repo:

```bash
python3 tools/isa/gen_c_codec.py \
  --spec isa/v0.56/linxisa-v0.56.json \
  --out-dir /tmp/linxisa-llvm-codec-check
```

The active compiler evidence path is AVS plus in-tree LLVM tests, not a
separate generated `LinxISAInstrInfo.td` staging file.

## Instruction Selection

### Arithmetic Operations

Map LLVM IR operations to the current `LinxV5` backend instructions:

- `add` → `ADD`, `ADDI`, `HL.ADDI` (based on immediate size)
- `sub` → `SUB`, `SUBI`
- `mul` → `MUL`
- `udiv`/`sdiv` → `DIV` variants
- `urem`/`srem` → `REM` variants

### Memory Operations

- `load` → `LWI`, `LDI`, `LDL` (based on addressing mode)
- `store` → `SWI`, `SDI`, `SDL`
- Load/store pairs → `LDP`/`STP` variants
- Pre/post-index → appropriate variants

### Control Flow

- `br` → `BSTART.*` variants
- `call` → `BSTART.CALL`
- `ret` → `BSTART.RET`
- `switch` → `BSTART` with jump table

### Block ISA

Each `MachineBasicBlock` should:
1. Start with `BSTART.*` or `C.BSTART.*`
2. End with `BSTOP` or implicit termination
3. Use `SETC.*` for conditional execution

## Register Allocation

### GPR Registers

- R0-R23: Standard ABI registers
- R24-R55: XGPR (if implemented)

### Tile Registers

Tile registers (T, U, M, N, ACC) should be:
- Modeled as virtual registers during codegen
- Assigned in a post-RA pass
- Managed with proper lifetimes within blocks

## Variable-Length Instructions

Support instruction length selection:

- 16-bit: Compressed forms (C.*)
- 32-bit: Base instructions
- 48-bit: Extended forms (HL.*)
- 64-bit: Prefixed forms (V.*)

The `MCCodeEmitter` should select the shortest encoding that fits.

## Testing

Run the current in-repo compiler gate:

```bash
cd avs/compiler/linx-llvm/tests
CLANG=compiler/llvm/build-linxisa-clang/bin/clang ./run.sh
```

Analyze coverage:

```bash
python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --verbose
```

## Naming Convention

The previous “rename everything to `Linx`” plan is obsolete for the active
branch. Follow the checked-in implementation names:

- backend target family: `LinxV5`
- architectural/project name in docs/spec: `LinxISA`
- user-facing baremetal target triple: `linx64-linx-none-elf`

## Implementation Checklist

### Phase 1: Core Instructions
- [ ] Generate TableGen patterns from ISA spec
- [ ] Implement arithmetic instruction selection
- [ ] Implement memory instruction selection
- [ ] Implement control flow instruction selection
- [ ] Support immediate materialization
- [ ] Implement PC-relative addressing

### Phase 2: Block ISA
- [ ] Implement BSTART variants
- [ ] Implement SETC variants
- [ ] Implement block formation pass
- [ ] Handle block-private registers (T/U queues)

### Phase 3: Tile Registers
- [ ] Define Tile register classes
- [ ] Implement TLOAD/TSTORE lowering
- [ ] Implement TCVT operations
- [ ] Implement matrix operations (MAMULB, etc.)

### Phase 4: Variable-Length
- [ ] Implement instruction length selection
- [ ] Support 16/32/48/64-bit encodings
- [ ] Optimize for code size

### Phase 5: Testing
- [ ] Run all test programs
- [ ] Achieve 100% instruction coverage
- [ ] Fix any failures

### Phase 6: Naming
- [ ] Rename all "LinxISA" to "Linx"
- [ ] Update documentation
- [ ] Verify consistency

## Resources

- ISA Spec: `isa/v0.56/linxisa-v0.56.json`
- Active backend: `compiler/llvm/llvm/lib/Target/LinxV5/`
- Test Programs: `avs/compiler/linx-llvm/tests/c/*.c`
- Coverage Tool: `avs/compiler/linx-llvm/tests/analyze_coverage.py`
