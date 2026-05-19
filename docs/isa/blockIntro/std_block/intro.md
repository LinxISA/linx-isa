# Integer type scalarblock instruction

The integer scalar block is a block instruction used to perform scalar integer data operations. It carries most of the business in general scalar operations, so it is also the most commonly used block instruction among LinxISA. The integer scalar block is suitable for sequentially executed scalar computing tasks and is suitable for calculations with relatively simple data flow.

## block type Features

The integer scalar block has the following characteristics:

- The integer scalar block is opened by the `BSTART.STD` instruction.
- The integer scalar block** only supports the one-piece block form**.
- The integer scalar block** provides full jump mode**, please refer to [Jump mode] (../../arch/branch.md#branch) for details.
- Integer scalar block ** does not support intra-block jump**.
- The integer scalar block allows access to global states such as [global register GGPR] (../../register/common/ggpr.md), [system registerSSR] (../../register/ssr/ssrintro.md) and memory. **Access to Tile register not allowed**.

## Block status BSTATE

The BSTATE of the integer scalar block contains the following three parts:

- **[BARG](../../register/common/barg.md) register**: Control parameter register within the block, used for conditional jumps or saving and processing of execution parameters.
- **[TPC](../../register/common/tpc.md) register**: records the address of the instruction being executed within the block (single TPC within the block).
- **[SGPR](../../register/common/sgpr.md) register**: Contains 8 general-purpose scalar registers, which are used to ensure efficient transmission of data flow within the block and provide a carrier for temporary data within the block.

In general, the BSTATE of the STD block uses BARG to manage block-level control (jumps, sequences, attributes), uses a single TPC to promote body microinstruction execution, and uses 8 SGPR to provide efficient scalar data channels and temporary storage within the block. The three work together to complete the scheduling and execution closed loop of the integer scalar block.

## Assembly example

The integer scalar block is defined in the form of an integrated block. The assembly example is as follows:
```asm
    BSTART.STD FAll
    ...                   # 其他ZXTERMZH19QXZ，根据需要补充定义
    add a0, a1,   ->t     # ZXTERMZH40QXZ中第一条微指令
    ldi [a2, 8],  ->u
    mul t#1, u#1, ->a1
    ...     
```