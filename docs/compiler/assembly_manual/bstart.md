# block instruction start directive: **BSTART**
    
```
BSTART.<type> <brType>, <label>     /*通用伪指令形态*/

BSTART <brType>, <label>            /*ZXTERMZH33QXZ为标准块时的通用伪指令形态*/

```

Two simplified expressions of standard blocks with jump type FALL

```
BSTART                              /*ZXTERMZH33QXZ为标准块且跳转类型为FALL时的伪指令形态*/

BSTART.STD                          /*ZXTERMZH33QXZ为标准块且跳转类型为FALL时的伪指令形态*/
```


BSTART represents the beginning of block instruction. The assembly starting from this point can be the accumulation of header descriptions or the body microinstructions until the end of block instruction is encountered. block instruction requires to start with 'BSTART', otherwise it will trigger running of exception, and the assembler will not do additional detection. The assembly pseudo-instruction description of BSTART includes the block type, jump type, and jump target address when the jump type is DIRECT, CALL, or COND. The linker generates the final assembly based on the actual link situation. Possible situations for the final assembly include:

- Consistent with the directive form
- Generate compressed header instruction'C.BSTART'. Generating assembly in this form requires that the compiler's instruction compression feature be enabled.

Next, we will mainly describe in detail the <type>, <brType> and <label> in the BSTART pseudo-instruction.


## block type

<type> is used to indicate the type of block. Block types include STD, FP, SYS, SIMT, LOOP, ECALL, ERET. The default is standard block.

| block instruction Type | Description |
|---------------------|---------------------|
| STD | **Standard block instruction Standard Block**, all instructions in the public encoding field and instructions in the private encoding field of the standard block are allowed in the block |
| FP | **Floating-point block instruction Floating-point Block**, the block allows all instructions in the public encoding field and instructions in the private encoding field of the floating-point block |
| SYS | **System block instruction System Block**, the block allows all instructions in the public encoding domain and instructions in the private encoding domain of the system block. |
| PAR | **Parallel block instruction**, the block only supports the instructions of all parallel block private coding fields, indicating that the parallel block group can be parallelized, and the relevant parameters need to be configured in advance. |
| VECT | **vectorblock instruction**, the block only supports the instructions of all SIMT block private coding fields, indicating that the block group can be parallelized, and the relevant parameters need to be configured in advance. |


## Jump type

<brType> is used to indicate the jump type of the block. Jump types include FALL, DIRECT, CALL, INDCALL, IND, COND, RET. Only FALL type defaults for standard blocks are supported.| Descriptor | Brief description | Whether there is an operation object | Format constraints of the operation object |
|--|--|--|--|
| FALL | Fall-Through, execute the next block instruction sequentially | No | NA |
| DIRECT | Jump directly to the block instruction location pointed to by the value of the operation object | Yes | Expression (a certain header address) |
| CALL | Jump directly to the location pointed to by the value of this operation object, and you need to use addpc to set the first header address of the next block instruction in the sequence into the RA register | Yes | Expression (a certain header address) |
| COND | 有条件地跳转到此操作对象的值指向的位置 | 是 | 表达式(某个header地址) |
| IND | Indirectly jump to the location pointed to by the value of the operand of setc.tgt | No | NA |
| ICALL | Indirectly jump to the location pointed to by the value of the operand of setc.tgt, and you need to use addpc to set the first header address of the next block instruction in the sequence to the RA register | No | NA |
| RET | Indirectly jump to the location pointed to by the value of the operand of setc.tgt | No | NA |


**Usage Precautions**

- For blocks with block type as PAR, the jump type only supports FALL.

- block instruction of COND jump type and body need to include microinstructions of setc.cond class.

- CALL跳转类型的block instruction的body中需要addpc来设置RA寄存器中的值。

- body of indirect jump type block instruction needs to contain setc.tgt.

- Microinstructions starting with setc. cannot appear in body of FALL/DIRECT/CALL jump type block instruction.

## Jump target address

<label> only exists when the jump type is DIRECT, CALL, or COND.


## Example <br>

Basic example:

```
BSTART.STD COND, .LBB0     /* 标准ZXTERMZH32QXZ有条件跳转的跳转目标地址为label(‘.LBB0’)对应的地址 */
微指令
BSTART COND, 0x20000       /* 标准ZXTERMZH32QXZ有条件跳转的跳转目标地址为0x20000 */
微指令
.LBB0：
BSTART                     /* 跳转类型为FALL的标准ZXTERMZH32QXZ*/
```

vector数据块需要提前设置LB寄存器，具体使用方式可以参见[vector数据块](../../isa/blockIntro/vec_block/intro.md)。