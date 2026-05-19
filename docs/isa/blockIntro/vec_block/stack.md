# stack register

Since the vector data block does not support direct access to the memory space internally and does not introduce a thread stack model, a type of [Tile register] (../../register/common/tilereg.md) is defined in the first-level architecture, identified as **S (Stack Tile Register)**. The S register is used to save call parameters under the function call semantics of Tile block instruction, and is used as a stack space for register overflow (spill), thereby providing necessary temporary storage capabilities while complying with the no direct access constraints of vectorblock instruction, taking into account computing performance and programmability.

## How to use S register

How to apply for register for header:

- Like other types of Tile registers, block instruction applies to use the S register through the [B.IOT/B.IOTI] (../../header/B.IOT.md) instruction.
- The S register is private to the block instruction that applied for it, that is, the S register is only visible to this block and not to other blocks.
- The S register is released with the commit of the block instruction that requested it.
- The B.IOT instruction applies for the stack space size used within a Group, and the total space size of the S register requires hardware calculation.
  
Note: **S register Group capacity multiplied by the number of Groups is the total space size of the S register, and the space size cannot exceed 512KB**.

Use the formal parameter register to access memory within the block:

- For block instruction that has applied for the S register, a mapping relationship is established with the S register through the formal parameter register **TS** in the block.
- The TS register can be read or written through the load/store local instructions within the block.
- TS points to the corresponding stack space in the current group.

Note: **If an uninitialized TS is read within the block, the return value is undefined**.

## Programming examples

An example of block instruction applying for `S寄存器` is as follows:
```
VPAR <LB0:64, LB1:64>, T#1, U#1, ->T<16KB>, S<8KB>
// 展开形式
BSTART.VPAR
B.DIM zero, 64,  ->LB0
B.DIM zero, 64,  ->LB1
B.IOTI T#1, U#1, ->T<16KB>
B.IOTI last,     ->S<8KB>    # 每个group申请的S-Tile空间8KB
```

Access memory within the block through the formal parameter TS:
```asm
// Spill
l.sd vt#1.ud, [TS, lc0.uh<<3]
// Reload
l.ld [TS, lc0.uh<<3], ->vt.d
```

## Special circumstances

Since the second output Tile of block instruction and the stack space register (S-Tile) correspond to the same formal parameter register TO1/TS in the block, ZXTER with multiple outputs and the need to use the S register MZH32QXZ needs to place `B.IOT xx, ->S` in the second output position, otherwise it will cause a conflict during initialization of the Tile parameter register and trigger the **illegal instruction exception**.

Error example 1:
```asm
# 汇编：
    VPAR xx, ->S<1KB>, T<1KB>, T<1KB>, ..., T<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系
    B.IOT xx, ->T<1KB>    # 第1个输出Tile（T）与TO建立映射关系
    B.IOT xx, ->T<1KB>    # 第2个输出Tile（T）与TO1建立映射关系，出现冲突
    ...
    B.IOT xx, ->T<1KB>    # 第n个输出Tile（T）与TO7建立映射关系
```

Error example 2:
```asm
# 汇编：
    VPAR xx, ->T<1KB>, T<1KB>, S<1KB>, ..., T<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->T<1KB>    # 第1个输出Tile（T）与TO建立映射关系
    B.IOT xx, ->T<1KB>    # 第2个输出Tile（T）与TO1建立映射关系
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系，出现冲突
    ...
    B.IOT xx, ->T<1KB>    # 第n个输出Tile（T）与TO7建立映射关系
```

Correct example:
```asm
# 汇编：
    VPAR xx, ->T<1KB>, S<1KB>, T<1KB>, ..., T<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->T<1KB>    # 第1个输出Tile（T）与TO建立映射关系
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系
    B.IOT xx, ->T<1KB>    # 第2个输出Tile（T）与TO2建立映射关系
    ...
    B.IOT xx, ->T<1KB>    # 第n个输出Tile（T）与TO7建立映射关系
```

If a block instruction does not have an output Tile register, but needs to apply for S register space, you can apply as follows:
```asm
# 汇编：
    VPAR xx, ->S<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系
```