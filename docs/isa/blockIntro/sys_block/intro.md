# System block instruction set

The system block (also called **auxiliary block**) is a very important type of block instruction. It is responsible for updating and maintaining the status of the entire system.

The current operations of system block instruction are divided into:

1. Configure system register, read and write system register
2. Configure and read block status BSTATE
3. Configure the memory system, MMU, TLB, Cache, etc.
4. Privilege level conversion, conversion from user mode to privilege level and vice versa
5. Implement atomic operations, atomic operations of a single instruction or the entire block instruction is defined as atomic
6. Implement inter-core communication, GQM.PUSH, GQM.POP, etc.
7. General operations and memory access operations

## block type Features

System blocks have the following characteristics:

- The system block is opened by the `BSTART.SYS` instruction.
- System block** only supports one block form**.
- System block** only supports Fall jump mode**, please refer to [Jump mode](../../arch/branch.md#branch) for details.
- Intra-block jumps are not supported within system blocks.
- Access to global states such as [Global Register GGPR] (../../register/common/ggpr.md), [system registerSSR] (../../register/ssr/ssrintro.md) and memory is allowed within the system block. **Access to Tile register not allowed**.

## Block status BSTATE

The BSTATE of the system block contains the following three parts:

- **[BARG](../../register/common/barg.md) register**: Control parameter register within the block, used for conditional jumps or saving and processing of execution parameters.
- **[TPC](../../register/common/tpc.md) register**: records the address of the instruction being executed within the block (single TPC within the block).
- **[SGPR](../../register/common/sgpr.md) register**: Contains 8 general-purpose scalar registers, which are used to ensure efficient transmission of data flow within the block and provide a carrier for temporary data within the block.

The BSTATE of the SYS block uses BARG to carry the scheduling and execution attributes of the system block. BPC and BlockType are used to identify the block entry and type, and AQ/RL is used to constrain the order and visibility of system actions; block-level jump control fields are not supported (no BPCN, Type, Taken). body uses a single TPC to promote the microinstruction execution process. It also provides eight 64-bit SGPRs as general scalar registers for parameter temporary storage, pointer and index calculation, flags and lightweight status recording in system routines. The three work together to ensure the controllable execution of system blocks and stable internal data channels.

## Assembly example

The system block is defined in the form of an integrated block. The assembly example is as follows:
```asm
    BSTART.SYS fall
    ...                    # 其他ZXTERMZH19QXZ，根据需要补充
    ssrget TP,     ->t     # ZXTERMZH40QXZ中第一条微指令
    ldi [t#1, 0],  ->t
    ldi [t#1, 8],  ->t
    mul t#2, t#1, ->a1
    ...     
    ic.iva
    ...
```

## Application

The system block is suitable for complex operations such as initiating system calls, sleeping and waiting for interrupt or external events, and Cache updates.