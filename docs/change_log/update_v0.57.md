# Version 0.57 Update

Update date: 2026-06-30

## Update Summary

LinxISA v0.57.0 adds **32-bit Compare-And-Swap (CAS)** instructions and reserves encoding space for **DMA** operations. This update improves code density for atomic synchronization primitives and lays the foundation for future direct memory access capabilities.

---

## Key Changes

### 1. Added 32-bit CAS Instructions

Four new atomic compare-and-swap instructions have been added to the base 32-bit instruction set:

| Instruction | Width | Description |
|-------------|-------|-------------|
| **CASB** | 8-bit | Compare-and-swap byte |
| **CASH** | 16-bit | Compare-and-swap halfword |
| **CASW** | 32-bit | Compare-and-swap word |
| **CASD** | 64-bit | Compare-and-swap doubleword |

**Encoding**: `6..4=3'b000, 3..1=3'b101, 14..12=3'b111` (Atomic instruction group)

**Key features**:
- Full support for memory ordering flags: `aq`, `rl`, `f`, `aqrl`, `aqf`, `rlf`, `aqrlf`
- Register reuse pattern: destination register serves as both input (swap value) and output (old value)
- Complements existing 48-bit `HL.CAS*` instructions with better code density

### 2. Reserved DMA Instruction Group

A new instruction group has been reserved for future DMA operations:

**Encoding**: `6..4=3'b001, 3..1=3'b101` (DMA instruction group)

**Characteristics**:
- Uses only `SrcL` and `SrcR` registers
- All other fields set to zero for future extension
- Provides 128 encoding slots (8 sub-opcodes × 16 variants)

---

## Motivation

### Why 32-bit CAS?

Prior to v0.57, LinxISA only provided **48-bit CAS instructions** (`HL.CASB/CASH/CASW/CASD`), which require 48 bits per instruction. While these offer independent input and output registers, they impact code density in atomic synchronization hot paths.

The new 32-bit CAS instructions:
1. **Reduce code size** by 33% compared to 48-bit variants
2. **Improve instruction cache utilization** for high-frequency atomic operations
3. **Match industry practice** - ARM, RISC-V, and x86 all provide compact CAS encodings
4. **Enable lock-free algorithms** at competitive code density

### Why Register Reuse?

32-bit encoding space cannot accommodate four independent 5-bit register operands (20 bits) plus control flags. The register reuse pattern:

```
RegDst serves as both:
  • Input: swap value (new value to write if comparison succeeds)
  • Output: old value (value read from memory, always returned)
```

This follows the same pattern as `SWAP*` instructions and is consistent with RISC-V atomic extensions.

**When the swap value must be preserved**, compilers can:
1. Insert a `MOV` instruction to save it beforehand
2. Use the 48-bit `HL.CAS*` variant instead

### Why Separate DMA Group?

DMA operations are **not atomic operations** - they represent bulk data transfers rather than read-modify-write synchronization primitives. Separating them into an independent instruction group:

1. **Clarifies semantics** - atomic vs. transfer operations
2. **Simplifies hardware** - different execution units
3. **Reserves extension space** - DMA may need diverse sub-opcodes
4. **Enables coexistence** - both groups share `3..1=101` but differ in `6..4`

---

## Encoding Design

### Instruction Group Allocation

| Group | 6..4 | 3..1 | 0 | Full encoding | Hex | Purpose |
|-------|------|------|---|---------------|-----|---------|
| Atomic + CAS | 000 | 101 | 1 | 000_101_1 | 0x0B | 48 atomic instructions |
| DMA | 001 | 101 | 1 | 001_101_1 | 0x15 | DMA operations (reserved) |

**Key difference**: Only the highest bit of `6..4` distinguishes the two groups.

### Atomic Instruction Group Encoding Space

| 14..12 | Instruction Type | Count | Status |
|--------|-----------------|-------|--------|
| 000 | LR.* | 4 | ✓ Pre-existing |
| 001 | SC.* | 4 | ✓ Pre-existing |
| 010 | LW.* | 8 | ✓ Pre-existing |
| 011 | SW.* | 8 | ✓ Pre-existing |
| 100 | LD.* | 8 | ✓ Pre-existing |
| 101 | SD.* | 8 | ✓ Pre-existing |
| 110 | SWAP* | 4 | ✓ Pre-existing |
| **111** | **CAS*** | **4** | **✅ New in v0.57** |

**Atomic instruction group is now full** (48 instructions total).

---

## Assembly Syntax

### 32-bit CAS Instructions

```assembly
casb<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}
cash<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}
casw<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}
casd<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}
```

**Examples**:
```assembly
casb [x5], x6, x7, ->x7          # Basic compare-and-swap
casw.aq [x1], x2, x3, ->x3       # With acquire semantics
casd.aqrl [x10], x11, x12, ->x12 # Full memory barrier
casb.f [x20], x21, x22, ->x22    # Far cache access
```

### DMA Instruction (Placeholder)

```assembly
dma SrcL, SrcR
```

**Note**: This is a placeholder for future DMA instruction definitions. Specific semantics will be defined as DMA requirements are finalized.

---

## Semantic Details

### CAS Pseudocode

```c
// CASB example
integer m = UInt(SrcL);      // address register
integer n = UInt(SrcR);      // expected value
integer d = UInt(RegDst);    // swap value (input)

Atomic {
    bits(8) old = Mem[m, 8];
    bits(8) expected = n[7:0];
    bits(8) newval = d[7:0];
    
    if (old == expected) {
        Mem[m, 8] = newval;  // Conditional write
    }
    
    R[RegDst, 64] = ZeroExtend(old, 64);  // Always return old value
}
```

**Key properties**:
- Entire operation is atomic (no interruption)
- Old value is always returned, regardless of comparison result
- RegDst is overwritten (input swap value is lost)

### Register Roles

| Register | CAS | DMA |
|----------|-----|-----|
| **SrcL** | Memory address | Source register 1 |
| **SrcR** | Expected value | Source register 2 |
| **RegDst** | Input: swap value<br>Output: old value | (unused) |

---

## Comparison: 32-bit vs 48-bit CAS

| Feature | 32-bit CAS | 48-bit HL.CAS |
|---------|------------|---------------|
| **Instruction length** | 32 bits | 48 bits |
| **Encoding** | Base `3..1=101` | HL prefix + main |
| **Registers** | 3 (RegDst reused) | 4 (fully independent) |
| **Swap value** | Overwritten | Preserved |
| **Code density** | High | Lower |
| **Use case** | High-frequency atomic ops | Register-constrained contexts |

### Selection Guide

**Use 32-bit CAS when**:
- High code density is critical
- Swap value need not be preserved
- Instruction cache pressure is high
- The operation is in a hot path

**Use 48-bit HL.CAS when**:
- Swap value must be preserved
- Register pressure is already high
- Four independent registers are required
- Code size is not a concern

---

## Compiler Considerations

### Automatic Selection

Compilers should:
1. **Default to 32-bit CAS** for atomic primitives
2. **Insert MOV** if swap value preservation is required:
   ```assembly
   mov x8, x7           # Save swap value
   casb [x5], x6, x7, ->x7
   # x7 = old value, x8 = swap value
   ```
3. **Use 48-bit HL.CAS** when register pressure prevents MOV insertion

### Code Generation Example

```c
// C source
int old = atomic_cas(&addr, expected, newval);
```

**Generated assembly** (32-bit):
```assembly
# Optimized: swap value not used afterward
casw [x5], x6, x7, ->x7      # x7 = newval (input), then old (output)
```

**Generated assembly** (48-bit, if swap value needed):
```assembly
hl.casw [x5], x6, x7, ->x8   # x7 = newval (preserved), x8 = old
```

---

## Hardware Implementation Notes

### Execution Pipeline

32-bit CAS instructions share execution resources with other atomic operations:

1. **Issue stage**: Decode as atomic operation (`3..1=101`, `14..12=111`)
2. **Read stage**: Read `SrcL` (address), `SrcR` (expected), `RegDst` (swap value)
3. **Execute stage**: Atomic compare-and-swap in L1 cache controller
4. **Writeback stage**: Write old value to `RegDst` (overwrites input)

### Cache Coherence

The `far` flag controls cache level targeting:
- `far=0`: L1/L2 cache atomic operation (default)
- `far=1`: Remote cache access (NUMA/multi-socket systems)

### Performance Characteristics

- **Latency**: Similar to `SWAP*` instructions (~20-50 cycles depending on cache hit)
- **Throughput**: One CAS per atomic execution unit per cycle
- **Code size**: 4 bytes (vs. 6 bytes for 48-bit `HL.CAS`)

---

## Migration from v0.56

### Source Code Compatibility

**No source-level changes required**. Existing code using 48-bit `HL.CAS` instructions continues to work.

### Binary Compatibility

**Not binary-compatible**. The addition of new instructions changes:
- Instruction encoding tables
- Disassembler output
- Debugger symbol tables

### Toolchain Updates Required

1. **Assembler**: Add 32-bit CAS mnemonic parsing
2. **Disassembler**: Recognize `6..4=000, 3..1=101, 14..12=111` as CAS
3. **Compiler**: Implement CAS selection heuristics
4. **Simulator**: Implement 32-bit CAS semantics

---

## Future Work

### v0.57.x

- Finalize DMA instruction semantics
- Add DMA sub-opcode variants
- Benchmark 32-bit vs 48-bit CAS performance

### v0.58+

- Additional atomic operations (if atomic group opens via new encoding)
- Extended DMA capabilities (scatter-gather, stride, etc.)

---

## References

- [32-bit CAS Encoding Specification](/tmp/cas_encoding_visual.txt)
- [Complete Encoding Table](/tmp/atomic_dma_cas_full_encoding.txt)
- [Implementation Checklist](/tmp/cas_implementation_checklist.md)

---

## Acknowledgments

This update was developed to address code density concerns in lock-free algorithms while maintaining full memory ordering semantics. The register reuse pattern balances encoding constraints with practical compiler optimization strategies.
