# Matrix data block

Matrix data block instruction is a dedicated matrix operation interface provided for hardware, which is used to drive the underlying CUBE computing unit to perform efficient and parallel tensor/matrix operations. This type of instruction takes fractal as the basic granularity and divides the matrix stored in the Tile register into multiple fractal structures for data calculation, thereby supporting high-dimensional, large-scale parallel matrix operation processing.

The matrix data block belongs to the instruction type that only has header but not body. It cannot be programmed or disassembled internally. The software only needs to specify the Tile register where the input matrix is ​​located and its row and column information and other parameters through the matrix data header instruction. After parsing these parameters, the hardware sends the instructions to the CUBE operation unit, which completes the corresponding matrix operation.

## block type Features

- Matrix data block **Only supports Fall jump mode**
- The matrix data block allows access to the global register GGPR and Tile registers, but does not allow access to memory and system registerSSR**.
- A matrix data block allows up to 8 Tile registers to be read and 4 tile registers to be written in one block.
- Every matrix operation writes an explicit Local destination D. ACC forms also read an explicit Local accumulator input C; when D and C alias, the operation reads the old value and writes the new value.
- There is no body in the matrix data block, **B.TEXT instruction is not allowed**

## Command list

| TileOp | Description |
|---------|----------------|
| [TMATMUL](../../header/tileblock/TMATMUL.md) | Matrix multiplication with an explicit destination |
| [TMATMUL.BIAS](../../header/tileblock/TMATMUL.BIAS.md) | Matrix multiplication plus an explicit bias, with an explicit destination |
| [TMATMUL.ACC](../../header/tileblock/TMATMUL.ACC.md) | Matrix multiply-accumulate from explicit accumulator C to explicit destination D |
| [TMATMULMX](../../header/tileblock/TMATMULMX.md) | Scaled matrix multiplication with explicit row/column scales and destination |
| [TMATMULMX.BIAS](../../header/tileblock/TMATMULMX.BIAS.md) | Scaled matrix multiplication plus bias, with an explicit destination |
| [TMATMULMX.ACC](../../header/tileblock/TMATMULMX.ACC.md) | Scaled matrix multiply-accumulate from explicit C to explicit D |
| [TGEMV](../../header/tileblock/TGEMV.md) | Matrix-vector multiplication with an explicit destination |
| [TGEMV.BIAS](../../header/tileblock/TGEMV.BIAS.md) | Matrix-vector multiplication plus bias, with an explicit destination |
| [TGEMV.ACC](../../header/tileblock/TGEMV.ACC.md) | Matrix-vector accumulate from explicit C to explicit D |
| [TGEMVMX](../../header/tileblock/TGEMVMX.md) | Scaled matrix-vector multiplication with an explicit destination |
| [TGEMVMX.BIAS](../../header/tileblock/TGEMVMX.BIAS.md) | Scaled matrix-vector multiplication plus bias, with an explicit destination |
| [TGEMVMX.ACC](../../header/tileblock/TGEMVMX.ACC.md) | Scaled matrix-vector accumulate from explicit C to explicit D |

PTO ISA 0.58 has no hidden architectural accumulator and no `ACCCVT` operation.
The logical accumulator role is carried by an ordinary Local Tile operand. This
keeps destination lifetime, aliasing, and conversion behavior explicit in the
bundle descriptors.

![acc](../../../figs/isa/arch/acc.svg){ width="600" }

For base and BIAS forms, descriptors name D and all matrix/vector inputs. For
ACC forms, descriptors additionally name accumulator input C. `D == C` is a
defined read-old/write-new alias; otherwise C is read and D is independently
updated.

## Input requirements

It should be noted that since the CUBE computing unit performs matrix operations based on a solidified systolic array structure, the input matrix must be organized according to the specified storage layout, otherwise the hardware cannot ensure the correctness of the operation.

In the matrix multiplication operation, the multiple input matrices (here represented by Matrix A, Matrix B and Matrix C respectively) must be stored in the following layout.

Matrix multiplication operation:

![matmul](../../../figs/isa/inst/matmul.svg)

Matrix multiplication and accumulation operations:

![matmadd](../../../figs/isa/inst/matmadd.svg)

Among them, matrix A and matrix C must be stored in the `大N小z` layout, and matrix B must be stored in the `大Z小n` layout. For layout introduction, please see [Storage Layout](../../register/common/tilereg.md).

Assume that S0 and K0 are the number of bytes and the number of elements of the K-dimensional fractal size respectively. Depending on the hardware implementation, the size of S0 can be different. Then:

- The fractal matrix size of matrix A is `16 x K0`.
- The fractal matrix size of matrix B is `K0 x 16`.
- The fractal matrix size of matrix C is `16 x 16`.

K0 can be calculated by the following formula:
```c
    K0 = S0 / sizeof(DataType);   # DataType表示元素ZXTERMZH20QXZ
```

If there are no special requirements, the hardware implemented based on this instruction set is recommended to be implemented according to the following standards:

- The size of a fractal of matrix A and matrix B is **512Byte**, and the corresponding size of S0 is **32Byte**.
- The size of a fractal of a C matrix varies with the bit width of the internal elements. If the elements in the matrix are 4byte wide, then the fractal size is **1024Byte** (16x16x4 byte); if the elements are 2byte wide, then the fractal size is **512Byte**.

In addition, before matrix operations, the hardware is required to convert all elements into FP32 or INT32 format before performing operations. For floating-point input, it is uniformly converted to FP32 format for calculation. If it is an integer input, it is uniformly converted to INT32 format for calculation.

## Output requirements

In v0.58, a matrix result is written directly to the explicit Local destination.
Subsequent activation, quantization, layout conversion, or element operations
consume that Tile through their normal explicit operands.

On the other hand, according to the format requirements of the input matrix, the result matrix must be stored in the layout of `大N小z`. And because the operation is performed in FP32 or INT32 format, the size of each fractal is fixed to **1024Byte** (16x16x4 byte).

The output requirements for matrix operations are summarized as follows:

| Type | Requirements |
|------|-----------|
| Destination register | Explicit Local Tile destination D |
| Output layout | Big N small z format |
| Fractal size | 1024Byte |
