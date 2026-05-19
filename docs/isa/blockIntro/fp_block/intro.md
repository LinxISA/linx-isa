# Floating point scalar block

Floating point scalarblock instruction is a block type used to process scalar floating point data operations. Floating point arithmetic operations usually occur in scientific computing, engineering applications, image processing and other fields. These fields often require numerical operations with high precision requirements. Therefore, the floating point scalar block is also a more important block instruction. In addition, the general integer scalar operation is also supported in the floating point block.

## block type Features

The floating point scalar block has the following characteristics:

- The floating point scalar block is started by the `BSTART.FP` instruction.
- Floating point scalar block** only supports one block form**.
- Floating point scalar block** provides full jump mode**, please refer to [Jump mode] (../../arch/branch.md#branch) for details.
- Floating point scalar block ** does not support intra-block jump**.
- The floating point scalar block allows access to global states such as [global register GGPR] (../../register/common/ggpr.md), [system registerSSR] (../../register/ssr/ssrintro.md) and memory. **Access to Tile register not allowed**.

## Block status BSTATE

The BSTATE of the floating point scalar block contains the following three parts:

- **[BARG](../../register/common/barg.md) register**: Control parameter register within the block, used for conditional jumps or saving and processing of execution parameters.
- **[TPC](../../register/common/tpc.md) register**: records the address of the instruction being executed within the block (single TPC within the block).
- **[SGPR](../../register/common/sgpr.md) register**: Contains 8 general-purpose scalar registers, which are used to ensure efficient transmission of data flow within the block and provide a carrier for temporary data within the block.

The BSTATE of the FP block uses BARG to manage the block-level control and attributes of the floating-point scalar block, and supports jump and sequence semantics consistent with STD: BPC and BlockType identify block entries and types, BPCN, Type, and Taken are used for jump control between blocks, and AQ/RL is used for execution order and memory visibility constraints. body linearly advances the microinstruction sequence with a single TPC. It also provides eight 64-bit SGPRs, which are general-purpose scalar temporary storage and operand carriers responsible for floating point and related control calculations, supporting operand preparation, loop control and intermediate result storage in the instruction pipeline. On the whole, the FP block forms a closed loop for scheduling and execution of floating-point scalar tasks through BARG's jump and attribute control, single TPC's sequential execution, and SGPR's efficient scalar data channel.

## Assembly example

The floating point scalar block is defined in the form of a single block. The assembly example is as follows:
```asm
    BSTART.FP DIRECT
    lwi [a0, 0],   ->t
    lwi [a0, 8],   ->t
    fadd.fs t#2, t#1,    ->t   
    ...
```