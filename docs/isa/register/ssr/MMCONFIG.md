# MMCONFIG

The Memory Management Configuration Register is used to configure the behavior of the memory management unit, such as paging size, address space range, etc. The compiler generates optimized memory management code based on this register.

![MMCONFIG](../../../figs/bitfield/svg/Sysregs/MMCONFIG.svg)

- **M**: Mode or number of layers. Layer conversion mode selector. The mode is defined and bound to the implemented mode, otherwise reset to 2'b00.

| M | mode |
|-----|----------------|
| 00 | VA39 or VA36 |
| 01 | VA48 or VA44 |
| 10 | VA57 or VA52 |
| 11 | Reserved |

- **Q**: Quad-word page table enabled. Indicates the effective page mode and VA slicing mode. Connect to the implemented content, otherwise reset to 1'b1.
    - 0: 8 Byte (Longword page table entry (LPTE)
    - 1:16 Byte (Quadword) Quadword Page Table Entry (QPTE)

- **HU**: (reserved field) Hardware is used to update the a/d bit of the pte. This is to specify whether the update of pte.A or pte.D is hardware or software based.
    - 0: A/D field update is software based.
    - 1: A/D field update is hardware based.

- **EN**: Enable. Enable address translation. Reset to 0. VA slicing options, expected VA slicing options on MMCONFIG.NL and MMCONFIG.Q field definitions.

| Virtual Address Mode | Virtual Address Width | MMCONFIG.Q | MMCONFIG.NL | Levels of Translation | Virtual Address Space |
|----------------------|-----------------------|------------|-------------|-----------------------|-----------------------|
| VA36 | 36 | 1 | 0 | 3 | 64G |
| VA39 | 39 | 0 | 0 | 3 | 512G |
| VA44 | 44 | 1 | 1 | 4 | 16T |
| VA48 | 48 | 0 | 1 | 4 | 256T |
| VA52 | 52 | 1 | 2 | 5 | 4P |
| VA57 | 57 | 0 | 2 | 5 | 128P |

## Remarks

The SSRID of this register is `0x1f11`, which exists in supervisor, hypervisory, and machinery level permissions, but is not used in user level permissions.