# Atomic instructions

Atomic instructions, also known as atomic operations or atomic instructions, refer to operations that will not be executed by interrupt when executed in a multi-processor system or multi-threaded environment, that is, the operation is either completely executed or not executed at all. Because in these environments there may be multiple processors or threads accessing shared resources simultaneously. Atomic instructions ensure that these operations are not interrupted or partially executed, thus avoiding data inconsistencies and unpredictable results. An atomic instruction often contains a set of operations, which can improve the efficiency of the instruction set, simplify the programming model, reduce the overhead of the instruction pipeline, and improve the throughput of the processor.

The atomic instructions in the system block currently mainly include the following types:

## LOAD.OP class instructions

LOAD.OP class instructions read a 32- or 64-bit value from the memory location specified by the left source register SrcL and write it into the destination register. Then perform corresponding operations (such as addition, bitwise AND, etc.) between this read value and the value of the right source register SrcR. The calculation results are stored in the memory specified by the SrcL register, and these steps are guaranteed to be atomic.| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| LW.ADD | lw.add<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | **Add** memory words are written back and the original memory words are output |
| LW.AND | lw.and<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | ** and ** memory words are written back and the original memory words are output |
| LW.OR | lw.or<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | ** or ** memory words are written back and the original memory words are output |
| LW.
| LW.SMAX | lw.smax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory word comparison **signed maximum** write back, output the original memory word |
| LW.UMAX | lw.umax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory word comparison **unsigned maximum** write back, output the original memory word |
| LW.SMIN | lw.smin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory word comparison **Signed Minimum** Write back, output the original memory word |
| LW.UMIN | lw.umin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory word comparison** unsigned minimum value** written back, output the original memory word |
| LD.ADD | ld.add<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | **Add** memory double word write back, output the original memory double word |
| LD.AND | ld.and<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | ** and ** memory double words are written back and the original memory double words are output |
| LD.OR | ld.or<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | ** or ** memory double word write back, output the original memory double word |
| LD.
| LD.SMAX | ld.smax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory double word comparison** signed maximum value** write back, output the original memory double word |
| LD.UMAX | ld.umax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory double word comparison** unsigned maximum value** write back, output the original memory double word || LD.SMIN | ld.smin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory double word comparison** signed minimum value** write back, output the original memory double word |
| LD.UMIN | ld.umin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory double word comparison** unsigned minimum value** write back, output the original memory double word |

LOAD.OP class atomic instructions can add additional memory access sequence restrictions through the two suffixes "aq" and "rl" to ensure the consistency of memory access. Please see "Memory Access Restriction Parameter Table" for specific definitions.

![AtomicLoad](../../../figs/bitfield/svg/Introduction_32bit/AtomicLoad.svg)

## STORE.OP class instructions

The STORE.OP class instructions have the same basic functions as the LOAD.OP class instructions, except that there is no destination register and the unmodified value at the specified memory location will not be returned.| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| SW.ADD | sw.add<{.rl}> [SrcL], SrcR | **Add** memory word write back |
| SW.AND | sw.and<{.rl}> [SrcL], SrcR | ** and ** memory word write back |
| SW.OR | sw.or<{.rl}> [SrcL], SrcR | ** or ** memory word write back |
| SW.XOR | sw.xor<{.rl}> [SrcL], SrcR | **XOR** memory word write back |
| SW.SMAX | sw.smax<{.rl}> [SrcL], SrcR | Memory word comparison **Signed Maximum** Writeback |
| SW.UMAX | sw.umax<{.rl}> [SrcL], SrcR | Memory word comparison **unsigned maximum** writeback |
| SW.SMIN | sw.smin<{.rl}> [SrcL], SrcR | Memory word comparison **Signed Minimum** Writeback |
| SW.UMIN | sw.umin<{.rl}> [SrcL], SrcR | Memory word comparison ** unsigned minimum ** write back |
| SD.ADD | sd.add<{.rl}> [SrcL], SrcR | **Add** memory double word write back |
| SD.AND | sd.and<{.rl}> [SrcL], SrcR | ** and ** memory double word write back |
| SD.OR | sd.or<{.rl}> [SrcL], SrcR | ** or ** memory double word write back |
| SD.XOR | sd.xor<{.rl}> [SrcL], SrcR | **XOR** Memory double word write back |
| SD.SMAX | sd.smax<{.rl}> [SrcL], SrcR | Memory double word comparison** signed maximum** write back |
| SD.UMAX | sd.umax<{.rl}> [SrcL], SrcR | Memory double word comparison ** unsigned maximum ** write back |
| SD.SMIN | sd.smin<{.rl}> [SrcL], SrcR | Memory double word comparison ** signed minimum ** write back |
| SD.UMIN | sd.umin<{.rl}> [SrcL], SrcR | Memory double word comparison ** unsigned minimum ** write back |
| SW.SUB | sw.sub<{.rl}> [SrcL], SrcR | **Subtract** memory word write back (v0.58) |
| SD.SUB | sd.sub<{.rl}> [SrcL], SrcR | **Subtract** memory double word write back (v0.58) |

### SX size-override extension (v0.58)

Starting with v0.58 the top five bits `31..27` of the atomic main class
(`6..4=000`) form a unified **op5** field:

- **b30..27 carries the operation/size code** (b27, formerly the far flag, is
  absorbed as the code's least-significant bit): operations `0000`=ADD,
  `0001`=AND, `0010`=OR, `0011`=XOR, `0100`=SMAX, `0101`=SMIN, `0110`=UMAX,
  `0111`=UMIN, and `1000`=SUB (new); the LR/SC/SWAP size codes are
  `0000`=B, `0001`=H, `0010`=W, `0011`=D;
- **b31 is the flag bit**: for the store-op forms (SW/SD slots) it is the
  **size-override** bit (0 keeps the word/doubleword width; 1 shrinks the
  access one step — the SW slot `14..12=011` becomes a byte SB access and the
  SD slot `14..12=101` becomes a halfword SH access); for LR/SC/SWAP and the
  load-op forms (LW.*/LD.*) it is the `far` remote-access flag, relocated
  from b27 to b31 with unchanged semantics;
- the `.f` suffix is therefore removed from the store-op forms (b31 is
  occupied by the override), while the remaining families keep it.

This adds four size-override atomic store instructions:

| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| SB.ADD | sb.add<{.rl}> [SrcL], SrcR | **Add** memory byte write back (SW-slot override) |
| SB.SUB | sb.sub<{.rl}> [SrcL], SrcR | **Subtract** memory byte write back (SW-slot override) |
| SH.ADD | sh.add<{.rl}> [SrcL], SrcR | **Add** memory halfword write back (SD-slot override) |
| SH.SUB | sh.sub<{.rl}> [SrcL], SrcR | **Subtract** memory halfword write back (SD-slot override) |

STORE.OP class atomic instructions need to add additional memory access sequence restrictions through the "rl" suffix to ensure the consistency of memory access. Please see "Memory Access Restriction Parameter Table" for detailed definitions.

![AtomicStore](../../../figs/bitfield/svg/Introduction_32bit/AtomicStore.svg)

## Atomic swap instructions

The atomic swap instruction reads the value of `8,16,32或64位` from the memory location specified by register SrcL and writes it to the destination register. Then store the 8, 16, 32 or 64-bit value in register SrcR into the memory specified by register SrcL, and ensure that these steps are atomic.| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| SWAPB | swapb<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory and register swap **byte** |
| SWAPH | swaph<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory and register swap **halfword** |
| SWAPW | swapw<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory and register swap **word** |
| SWAPD | swapd<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd} | Memory and register swap **double** |

The atomic swap operation instruction can add additional memory access sequence restrictions through the "aq" and "rl" suffixes to ensure the consistency of memory access. Please see "Memory Access Restriction Parameter Table" for specific definitions.

![AtomicSwap](../../../figs/bitfield/svg/Introduction_32bit/AtomicSwap.svg)

## Atomic compare-and-swap instructions

The atomic compare-and-swap instruction reads an `8, 16, 32, or 64-bit` value
from the memory location designated by register SrcL, compares the read value
with register SrcR, and stores the `8, 16, 32, or 64-bit` value of register
SrcD into that memory location when they are equal. Regardless of the
comparison result, the original value read from memory is written to the
destination register, and **all of these steps are atomic**.

The 32-bit CAS forms support `.aq`/`.rl` ordering but **no `.f` remote-access
suffix**; use the 48-bit [HL.CAS\*](../../../isa/inst/misa_h/HL.CASB.md)
family for remote-cache access.

| Microinstruction | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
|  CASB   | casb<{.aq,.rl,.aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}   |  Compare-and-swap **byte**   |
|  CASH   | cash<{.aq,.rl,.aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}   |  Compare-and-swap **halfword**   |
|  CASW   | casw<{.aq,.rl,.aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}   |  Compare-and-swap **word**     |
|  CASD   | casd<{.aq,.rl,.aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}   |  Compare-and-swap **doubleword**   |

![AtomicCompareandSwap](../../../figs/bitfield/svg/Introduction_32bit/AtomicCompareandSwap.svg)

The atomic compare-and-swap instructions can add extra memory-ordering
restrictions through the "aq" and "rl" suffixes; see the memory access
restriction parameter table for the exact definitions.

## Memory access restriction parameter table

| aq | rl | meaning |
|-------|--------|----------------------------------------|
| 0 | 0 | No order restrictions |
| 0 | 1 | Indicates that the results of all memory access instructions preceding this instruction must be observed before this instruction is executed |
| 1 | 0 | Indicates that all instructions that access memory after this instruction must wait until the instruction is completed before starting to execute |
| 1 | 1 | means that the results of all instructions that access memory before this instruction must be observed before the instruction is executed, and that all instructions that access memory after this instruction must wait until the execution of this instruction is completed before starting to execute |