# MMTBASE

The Memory Management Translation Base Register stores the translation base address of the memory management unit and is used to convert virtual addresses to physical addresses.

![MMTBASE](../../../figs/bitfield/svg/Sysregs/MMTBASE.svg)

- **[1:0]CONST_0**: As a selector for address translation mode, currently starting from bit 0 as a constant value. Constant values ​​work with TN0PB to form a 16 KB aligned base node. (2'b00: Enable address translation mode.)
- **[39:2]TN0PB**: Translation node 0 pointer, the base page (level 0 page) is the base address of the exception level physical page, which should be aligned to 16 KB. The physical address of the base page is calculated as follows and up to 52 bits are allocated to the physical base page.

    `PA = zero_extend_to_64b({MMTBASE.TN0PB,14’d0})`

- **[63:40]ASID**: 24-bit application space identifier. The actual number of bits is implementation-defined. All implemented bits are grouped consecutively starting from the LSB. Unimplemented bits are hardwired to 0. Writes to unimplemented top bits are ignored. For example, if implementation bits = 8, the legal set is [0..255] and the top 16 bits of the ASID are all hardwired to 0.

## Remarks

The SSRID of this register is `0x1f10`, which exists in supervisor, hypervisory, and machinery permissions, but is not used in user-level permissions.