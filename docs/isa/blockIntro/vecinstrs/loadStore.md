# Memory access instructions

## General overview

- **Execution scope and parallel semantics**: vectorLoad/Store instructions are executed in parallel in each lane within a Group in a lock-step manner. Each lane independently calculates the effective address (EA), initiates memory access, and reads and writes its corresponding vector register element.
- **Element granularity and bit width**: The operation object is an element, and the element bit width is determined by the instruction, and supports 1, 2, 4, and 8 bytes.
- **Effective address unified paradigm**: EA consists of "base address + offset". The offset source can be a register or an immediate value, and can be scaled by instruction type (left shift) or maintained at byte granularity (no scaling).
- **Data expansion and storage**: Load provides two types of semantics: sign extension or unsigned extension for 1/2/4-byte data; 8-byte load does not extend. Store writes back strictly according to the instruction bit width and does not involve data expansion.
- **Aligned vs. Unaligned Access**: The scaled offset form is for naturally aligned access; the unscaled form allows unaligned access at byte granularity. The performance of unaligned accesses and exception behavior are implementation defined.
- **Results and Side Effects**: Load writes data to the target vector register element; Store writes the source vector register element to the target address space. There are no additional register outputs except memory access.
- **exception vs. Memory Consistency**: exception with sorting follows the global memory of the architecture with the exception model. This section does not define barrier or synchronization semantics separately.

## vectorLoad instruction

### **1. Register-Register Addressing**

EA calculation: `SrcL+(SrcR<< shamt), shamt有效范围为[0,31]`.

| Command | Data Extension |
|--------|------------------------|
| V.LB | Load 1 byte, sign extended to the specified bit width of the element |
| V.LH | Load 2 bytes, sign extended to the specified bit width of the element |
| V.LW | Load 4 bytes, sign extended to element execution bit width |
| V.LD | Load 8 bytes, no extension (write as 64-bit) |
| V.LBU | Load 1 byte, unsigned extension to the specified bit width of the element |
| V.LHU | Load 2 bytes, unsigned extension to the specified bit width of the element |
| V.LWU | Load 4 bytes, unsigned extension to the specified bit width of the element |

![LoadRegisterOffset](../../../figs/bitfield/svg/Introduction_64bit/LoadRegisterOffsetVector.svg)

Applicable scenarios: The offset comes from a register and needs to be scaled by `2^shamt`, which is convenient for expressing step access, structure field spacing, or indexed access by element size.

### **Register-with scaled immediate addressing**

In this addressing mode, immediate offsets are naturally aligned according to the element bit width.

| Command | Data extension | Effective address |
|--------|----------------|----------|
| V.LBI | Load 1 byte, sign extended to the specified bit width of the element | SrcL + simm24 |
| V.LHI | Load 2 bytes, sign extended to the specified bit width of the element | SrcL + (simm24<<1) |
| V.LWI | Load 4 bytes, sign extended to the specified bit width of the element | SrcL + (simm24<<2) |
| V.LDI | Load 8 bytes, no extension (write as 64-bit) | SrcL + (simm24<<3) |
| V.LBUI | Load 1 byte, unsigned extension to the specified bit width of the element | SrcL + simm24 |
| V.LHUI | Load 2 bytes, unsigned extension to the specified bit width of the element | SrcL + (simm24<<1) |
| V.LWUI | Load 4 bytes, unsigned extension to the specified bit width of the element | SrcL + (simm24<<2) |

Among them, simm24 is a 24-bit signed immediate number, which is expanded to 64-bit sign before participating in EA calculation.

The instructions are encoded as follows:

![LoadImmediateOffset](../../../figs/bitfield/svg/Introduction_64bit/LoadImmediateOffsetVector.svg)Applicable scenarios: The index is an immediate offset of the number of elements, automatically aligned according to the element bit width, and is often used to access the array base address plus element index.

### **Register-Unscaled Literal Addressing**

In this addressing mode, the immediate offset is in bytes.

| Command | Data extension | Access address |
|--------|-------------------|-----------|
| V.LHI.U | Load 2 bytes, sign extended to the specified bit width of the element | SrcL + simm24 |
| V.LWI.U | Load 4 bytes, sign extended to the specified bit width of the element | SrcL + simm24 |
| V.LDI.U | Load 8 bytes, no extension (write as 64-bit) | SrcL + simm24 |
| V.LHUI.U | Load 2 bytes, unsigned extension to the specified bit width of the element | SrcL + simm24 |
| V.LWUI.U | Load 4 bytes, unsigned extension to the specified bit width of the element | SrcL + simm24 |

Among them, the `.U` suffix indicates that the element bit width of the immediate data is not scaled.

The instructions are encoded as follows:

![LoadInstructionUnScaled](../../../figs/bitfield/svg/Introduction_64bit/LoadInstructionUnScaledVector.svg)

Applicable scenarios: Scenarios where precise control of byte offset or unaligned access is required.

## vectorStore command

The Store instruction does not produce a register output; the write destination is determined by the address space selection (see .local).

### **Register-Register Addressing**

The Store instruction using register-register addressing has three source registers, of which SrcL and SrcR are used to generate addresses, and SrcD is used to provide data elements to be written.

| Command | Memory access bit width | Memory access address |
|--------|-----------|-----------|
| V.SB | 1 byte | SrcL + (SrcR<<shamt) |
| V.SH | 2 bytes | SrcL + (SrcR<<(1+shamt)) |
| V.SW | 4 bytes | SrcL + (SrcR<<(2+shamt)) |
| V.SD | 8 bytes | SrcL + (SrcR<<(3+shamt)) |
| V.SH.U | 2 bytes | SrcL + (SrcR<<shamt) |
| V.SW.U | 4 bytes | SrcL + (SrcR<<shamt) |
| V.SD.U | 8 bytes | SrcL + (SrcR<<shamt) |

Among them, the `.U` suffix means that the register offset does not perform "additional left shift according to the element bit width" and only scales according to shamt; the H/W/D variant without suffix adds a left shift according to the bit width on the basis of shamt to achieve a natural alignment step.

The instructions are encoded as follows:

![StoreRegOffset](../../../figs/bitfield/svg/Introduction_64bit/StoreRegisterOffsetVector.svg)

### **Register-immediate addressing**

| Command | Memory access bit width | Memory access address |
|--------|-----------|-----------|
| V.SBI | 1 byte | SrcL + simm24 |
| V.SHI | 2 bytes | SrcL + (simm24<<1) |
| V.SWI | 4 bytes | SrcL + (simm24<<2) |
| V.SDI | 8 bytes | SrcL + (simm24<<3) |
| V.SHI.U | 2 bytes | SrcL + simm24 |
| V.SWI.U | 4 bytes | SrcL + simm24 |
| V.SDI.U | 8 bytes | SrcL + simm24 |Among them, the `.U` suffix indicates that the element bit width of the immediate data is not scaled.

The instructions are encoded as follows:

![StoreRegOffset](../../../figs/bitfield/svg/Introduction_64bit/StoreImmediateOffsetVector.svg)

## Address space selection

All vectorLoad/Store instructions support the optional .local tag for selecting the memory target space.

- None.local: Access system memory (via MMU/TLB, cache, etc.).
- With .local: Access Tile register space or locally addressable private Tile storage array.
- Address calculation: .local does not change the EA calculation, only the access path and space.
- Implementation purpose: Explicit space selection reduces hardware address determination overhead and facilitates port arbitration, bandwidth management and error isolation.

exception and out of bounds:

- Memory space: Follows the universal memory access exception and permissions model.
- Tile space: Out-of-bounds or unauthorized access triggers Tile space access exception (or implementation-defined error code).
- Semantics maintained: data bit width and extended semantics are consistent with non-.local instructions.

Example:
```asm
V.LW.local [SrcL + (SrcR << shamt)], ->Dst
V.SD.local SrcD, [SrcL + (simm24 << 3)]
```

## Continuous address access within the Group

The vectorLoad/Store instruction supports the access method of continuous addresses within the Group. In this way, the Load/Store instruction has a **LC0** input by default, which is used as a continuously increasing variable for address calculation, and combined with a specific left shift number to meet the stride of the element bit width. The remaining address calculation inputs, including base and offset, must be scalar values, ensuring that LC0 is the only variable.

Continuity definition: Let the element bit width be E (bytes), and the lane index be i=0..(VL-1). If you enable or rely on continuous access optimization, it requires:
```c
EA(i+1) = EA(i) + E
```

Continuous memory access: `Load [base, lc0<<shamt, offset]`; `Store [base, lc0<<shamt, offset], ->dst`.

The base and offset must be guaranteed to be unchanged within each Group, and the value of the lc0 register will increase as the laneid increases. At the same time, the bit width of `shamt` is fixed according to different access elements, for example:

- Load 1 byte: `V.LB [base, lc0, offset]`, lc0 equals 0, 1, 2, 3,...
- Load 2 bytes: `V.LH [base, lc0<<1, offset]`, lc0 equals 0, 1, 2, 3,...
- Load 4 bytes: `V.LW [base, lc0<<2, offset]`, lc0 equals 0, 1, 2, 3,...
- Load 8 bytes: `V.LD [base, lc0<<3, offset]`, lc0 equals 0, 1, 2, 3,...

![](../../../figs/isa/inst/continuous.png){ width="800" }

## Constraints and implementation details

- Register and vector form: vd is the destination vector register; SrcL/SrcR/SrcD are source registers. The number of lanes, vector length and element width are configured by the implementation or compilation environment.
- Address calculation width: In 64-bit implementation, EA calculation is performed in 64 bits. The behavior of EAs out of bounds and address space limitations is implementation-defined.
- Extension and number of bytes accessed: Extension only affects the element value representation in the register and does not change the number of bytes accessed. Store writes back strictly on a bit-wide basis.
- Memory consistency and synchronization: Instructions do not come with their own barriers; when performing strict ordering or visibility guarantees with other processing units or peripherals, the synchronization/barrier instructions provided by the architecture should be combined.
- Masking with exception: If the architecture supports vector masking or lane-by-lane exception suppression, its behavior is as defined by the vector control and exception models.

## Assembly example (suggested)- Load (Register-Register): `V.LW [SrcL + (SrcR << shamt)], ->Dst`
- Load (scaling immediate): `V.LHI [SrcL + (simm24 << 1)], ->Dst`
- Load (unscaled immediate): `V.LWI.U [SrcL + simm24], ->Dst`
- Store (Register-Register): `V.SD SrcD, [SrcL + (SrcR << (3 + shamt))]`
- Store (scaling immediate): `V.SWI SrcD, [SrcL + (simm24 << 2)]`
- Store (no scaling immediate): `V.SDI.U SrcD, [SrcL + simm24]`
- with .local: `V.LW.local [SrcL + (SrcR << 2)], ->Dst`; `V.SDI.local [SrcL + (simm24 << 3)]`