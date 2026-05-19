# Linxblock instructionDefinition

**Linxblock instruction** is a structured and hierarchical instruction form used to describe the logical structure and execution scope of complex computing tasks. By introducing the concept of "blocks", LinxISA significantly improves the expression ability of instructions and the execution efficiency of the processor.

Different from the traditional instruction set that executes one by one, Linxblock instruction encapsulates multiple related instructions into an execution unit "block". Each block can contain any number of body instructions and is scheduled, optimized and executed as a whole.

Linxblock instruction consists of two parts: **header (Header)** and **body (Body)**. Among them, header is used to describe the scheduling and control information of the block, and body is responsible for performing specific calculations or memory access operations.

![block](../../figs/isa/arch/header_body.png){ width="600" }

The instruction used to define header is called "header instruction". This type of instruction marks the start of block instruction, and specifies parameters such as block type, setting jump logic and execution requirements. There are some basic parameters, including:

| Parameters | Description |
|------|------------|
| **block type** | This parameter determines what engine is used to execute this block, and what rules the engine must follow to execute this block. |
| **branch parameter** | This parameter defines how to find the next block. |
| **Block Attribute** | This parameter is a parameter of block type. It is used to describe other requirements other than this block type. Many attributes can be used on multiple block type. Please refer to the attribute description for details. |
| **input/output** | This parameter sets the input/output register of this block, but it is not required. If this parameter is not defined, then all one-level registers are considered to be used for input/output, which may reduce the parallelism of the instruction pipeline. |
| **block structure** | This parameter defines the organizational structure of header and body and is used to indicate the position of the block body. |

The assembly syntax of header instruction is defined as the following form: `OPCODE {parameters}`. Among them, `OPCODE` defines the instruction function; `{parameters}` describes the instruction parameter content.

body contains actual execution instructions, such as calculation instructions, memory operation instructions, etc. They are called "body instructions".

The form of the body instruction is related to block type. Without special instructions, the body command form is unified as:

```asm
opcode {input_parameters} {, ->output_parameters}
```

The input/output parameter of the instruction is clearly divided into two parts, split by `,->`. `input_parameters` describes the input parameters, and `output_parameters` describes the output parameters.

## block structure

According to the different organizational forms between header and body, block instruction supports three definition methods:* **Coupled Block**: header and body are defined together and are fetched uniformly by the first-level scheduler. The bodybody instructions are passed to the block engine through the internal channel. This is the basic form of Linxblock instruction, which is suitable for programs with intensive control flow or low parallelism. For detailed definition, please see [block instructionexecution mechanism](./executemachine.md).
* **Decoupled Block**: header is separated from body. The first-level scheduler is responsible for header instruction fetching, and the second-level block engine is responsible for body decoding execution. For detailed definition, please see [block instructionexecution mechanism](./executemachine.md).
* **template block (Template Block)**: Contains only header, excluding explicit body. header is handed over to the template generation unit CodeGen to automatically generate the body instruction sequence or header is directly executed in a specific execution unit, which is suitable for fixed function modules, such as memory copy, matrix operation, etc.

Different block structure blocks have different header definition methods and the status of the registers in the block.

## block type

block type determines what engine is needed to execute this block and the execution capabilities of this block. The block type supported in the current version of LinxISA are as follows:| block type | Assembly symbols | Description |
|--------|---------|--------------|
| [Integer scalar Block](../blockIntro/std_block/intro.md)（**Integer Scalar Block**） | STD | The basic block of LinxISA, providing general integer computing capabilities |
| [System Block](../blockIntro/sys_block/intro.md)（**System Block**） | SYS | Used to maintain system status and provide system control computing capabilities |
| [Floating-point scalar Block](../blockIntro/fp_block/intro.md)（**Floating-point Scalar Block**） | FP | Provides scalar floating-point computing capabilities |
| [Memory Access and Parallel Block] (../blockIntro/mem_block/intro.md) (**Memory Access and Parallel Block**) | MPAR | Provides vector-based memory data transfer capabilities, multiple Groups parallel execution |
| [Memory Access and Sequel Block](../blockIntro/mem_block/intro.md)（**Memory Access and Sequel Block**） | MSEQ | Provides vector-based memory data transfer capabilities, multi-Group serial execution |
| [vector Parallel Block](../blockIntro/vec_block/intro.md)（**Vector and Parallel Block**） | VPAR | Provides vector data computing capabilities, multi-Group parallel execution |
| [vector serial block](../blockIntro/vec_block/intro.md) (**Vector and Sequel Block**) | VSEQ | Provides vector data computing capabilities, multi-Group serial execution |
| [Data Movement Block](../blockIntro/tma_block/intro.md)（**Tile and Memory Access Block**） | TMA | Provides data movement capabilities between memory and Tile registers |
| [Matrix Data Block](../blockIntro/cube_block/intro.md)（**Cube Block**） | CUBE | Provides matrix operation capabilities, splits the matrix into multiple subtypes, and performs matrix operations at the granularity of subtypes |
| [Template Data Block](../blockIntro/tepl_block/intro.md)（**Template Tile Block**） | TEPL | Provides templated data block (Tile) computing capabilities |
| [system-call block](../blockIntro/xb_block/intro.md)（**Cross Block**） | XB | Provides lightweight system calling capabilities |

Among them, the memory access parallel block and the memory access parallel block are both used to perform data movement tasks between memory and Tile, but the execution requirements between groups are different, so these two blocks are collectively called memory access data blocks. vector parallel block and vector serial block only have different execution requirements between groups, so they can also be collectively called vector data block.

All block instruction share the same first layer architectural state, but different types of block instruction can have their own unique second layer architectural state, for example, the second layer architectural state of a scalar block can be completely different from a vector block. This design can provide a flexible and adaptable computing framework when processing tasks of different complexity such as scalar operations, vector operations and large-scale parallel operations, helping the processor achieve efficient performance in different scenarios.

Not only that, each specific block instruction can also have its own set of private registers. These registers are allocated when block instruction is initialized, released after block instruction is submitted, and can only be accessed and used by instructions within this block.![block](../../figs/isa/arch/BlockState.png){ width="800" }

## branch parameter

branch parameter is used to define the execution path between block instruction, indicating how to find the next block from the current block. This parameter contains the type and the jump distance for the specific type. LinxISA supports the following branch parameter:

There is no need for a jump distance parameter, or the jump distance is provided through a register:

- FALL: Fall Through, the next block will be executed after the end of the block.
- IND: Indirect Branch, jump to the specified absolute address after the block ends.
- ICALL: Indirect Call, after the block ends, jump to the absolute address of the instruction to implement the function call. Its actual execution effect is the same as IND, but an additional call return address needs to be recorded.
- RET: Return, after the block ends, jump to the specified absolute address location to implement function return. Its actual execution effect is the same as IND, but it gives the processor an execution hint to better predict the execution sequence of instructions.

Need jump distance parameters:

- DIRECT: Direct Branch, jump to the specified offset position after the end of the block.
- COND: Conditional Branch, after the block ends, jump to the specified offset position according to the calculated result condition.
- CALL: Call, after the block ends, jump to the specified offset position for function call. Its actual execution effect is the same as DIRECT, but an additional call return address needs to be recorded.

## Block attributes

The block attributes set the execution behavior of the block as a whole. This section describes the parts containing complex functions. For other simple attributes, please refer to the definition method description of each specific block type.

### Atomic properties

Atomic attributes give atomicity to block memory operations. Blocks with atomic attributes are called atomic blocks. Memory operations in atomic blocks will not be interrupted or observed by other memory observers. If the atomic block is interrupted by interrupt or exception, the memory operations and register output effects of the atomic block will either be invalid or all effective.

The memory behavior of atomic blocks is limited to a continuous range (future versions may be upgraded to more continuous ranges). If the actual operation exceeds this range, the **E_DATA(EC_RANGE)exception** of this instruction is triggered.

The current version's continuous access range to atomic blocks is defined as a 16-byte aligned 16-byte space. An atomic block behaves in memory as a single memory macro instruction, so the instruction itself can have acquisition and release order properties.

### Inherited properties

Inherited attributes can retain the internal state of the block to subsequent blocks, which is beneficial to the continuous transfer of data. The inheritance attribute is defined as that after the execution of a block instruction is completed, its internal state is inherited by default to the next block instruction of the same execution engine, and the block instruction of different execution engines can be spanned in the middle.

Its characteristics can be summarized as:

- Not all block instruction are allowed to inherit from each other, but block instruction that must have the same block state and execute in the same engine have inherited attributes.
- Inherited attributes are the default attributes of block instruction and do not require additional parameters to be specified.
- Inheritance is cross-functional, allowing inheritance relationships between two discontinuous blocks on program order.

For example, the following program:
```asm
block1:
    BSTART.STD FALL
    ld [r1, r2<<3], ->t     # i0
    ld [r1, r3<<3], ->t     # i1
    setc.ne t#1, zero
    ...
block2:
    BSTART.VPAR FALL
    B.DIM 100, zero, ->LB0
    B.TEXT .foo
block3:
    BSTART.SYS FALL
    add t#1, t#2, ->t      # t#1读取i0的结果，t#2读取i1的结果  
    BSTOP
foo:    # block2的ZXTERMZH40QXZ
    v.lwi [TA, LC0<<2], ->vt.w
    v.lwi [TB, LC0<<2], ->vt.w
    rdadd vt#1, ->t
    ...
```
Among them, `block1` and `block3` execute on the same engine, while `block2` executes on different block engines. Therefore, `block2` cannot inherit the internal state of `block1`. `block3` can inherit the internal state of `block1`, but cannot inherit the internal state of `block2`.

It is important to note that if a register in body of a block is read that has not been written by the previous block, then the content read is an undefined random value. For example:

```asm
# 程序开始第一个块
BSTART.SYS
addi t#1, 8, ->t       # t#1的值是未定义的
ld [a0, t#1<<3], ->t
...
```