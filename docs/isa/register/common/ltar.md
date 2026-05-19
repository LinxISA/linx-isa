# LTAR

LTAR (Local Tile Address Register) is called the Tile parameter register. It is the core mechanism in the Decoupled Block for large block data (Tile) level communication with the caller. It supports efficient and structured input/output transfer.

## Register definition

Each readable and writable Tile register of the block instruction supports:

- 8 input Tile registers
- 4 output Tile registers

In order to meet the data interaction requirements, **12 Tile type parameter registers** are defined inside the separation block, which are used to map the Tile register passed in by the caller.

The Tile formal parameter register list is as follows:

| Register | Type | Description |
|--------|------|-----|
| TA | Input | Stores the first address of the first input Tile register of this block |
| TB | Input | Stores the first address of the second input Tile register of this block |
| TC | Input | Stores the first address of the third input Tile register of this block |
| TD | Input | Stores the first address of the fourth input Tile register of this block |
| TE | Input | Stores the first address of the fifth input Tile register of this block |
| TF | Input | Stores the first address of the sixth input Tile register of this block |
| TG | Input | Stores the first address of the seventh input Tile register of this block |
| TH | Input | Stores the first address of the eighth input Tile register of this block |
| TO | Output | Store the first address of the first output Tile register of this block |
| TO1/TS | Output/Stack | Stores the first address of the second output Tile register of this block (can also be used as the first address of the stack space) |
| TO2 | Output | Stores the first address of the third output Tile register of this block |
| TO3 | Output | Stores the first address of the fourth output Tile register of this block |

Note: TO1/TS supports dual purposes: it can be used as the first address of the output register or the first address of the stack space.

## Mapping mechanism

The Tile formal parameter register is bound to the Tile register passed in by the caller through header instruction [B.IOT](../../header/B.IOT.md).

Mapping sequence: Formal parameter registers TA ~ TH correspond to the first 8 input Tiles passed in by header. TO ~ TO3 correspond to the 4 output Tiles passed in by header.

- **Input Mapping**:
    - TA -> 1st input Tile register
    - TB -> 2nd input Tile register
    -...
    - TH -> The 8th input Tile register (note: 8 inputs in total, index A~H)
- **Output Mapping**:
    - TO -> 1st output Tile register
    - TO1 -> 2nd output Tile register
    - TO2 -> The third output Tile register
    - TO3 -> The 4th output Tile register

The mapping is dynamically bound at runtime, and different callers can specify different Tile registers as input/output.

---

## Assembly example

The assembly example is as follows:
```asm
Header:
    MPAR .Body <LB0:64, LB1:32> T#1, U#1, T#2, [a0], ->M<256B>
    ...
Body:
    l.lw  [TA, LC0.uh<<2],   ->vt.w       # TA映射到ZXTERMZH39QXZ的T#1输入
    l.lw  [TB, LC0.uh<<2],   ->vt.w       # TB映射到ZXTERMZH39QXZ的U#1输入
    l.add vt#1.sw, vt#2.sw,  ->vt.w
    l.sw  vt#1.sw, [TO, LC0<<2]           # TO映射到ZXTERMZH39QXZ的M输出
    l.ld  [TC, LC0.uh<<3],   ->vt.d       # TC映射到ZXTERMZH39QXZ的T#2输入
    l.sd  vt#1.ud, [ri0.ud, LC0<<3]
    bstop
```

---

## Key rules and precautions

**1. Initial value source**

- The initial value of the Tile formal parameter register (TA/TO, etc.) is allocated by the caller hardware when parsing header and cannot be modified within the block.
- If an attempt is made within the block to read an uninitialized parameter register (such as not passed in), the result is undefined.

**2. Mapping space read and write permissions**| Register Type | Permissions | Description |
|-----------|--------|-------|
| Input formal parameter mapping space (TA, TB, etc.) | Read-only | Reading within the block is legal; writing triggers illegal instructions exception |
| Output formal parameter mapping space (TO, TO1, etc.) | Readable and writable | If the unwritten location is read, the result is undefined; after writing, the read result is the written value |

Security design: writing to input registers is prohibited to prevent data pollution and status errors.

---

## Application scenarios

1. **vector data processing**: read input Tiles in batches and write output Tiles in batches.
2. **Modular function call**: Different callers pass in different data sources.
3. **Stack space integration**: The output Tile register can be used for temporary storage (such as function call stack).

## Summary

The Tile formal parameter register provides a structured, efficient, and safe Tile-level data interface for separate blocks. It supports flexible inter-module communication through up to 8 input and 4 output registers, with a total of 12 formal parameters.