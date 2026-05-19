# Loop register

The Loop register is mainly used in [vector data block] (../../blockIntro/vec_block/intro.md) and [access data block] (../../blockIntro/mem_block/intro.md) to indicate the total number of body iteration expansions and record the ID of each iteration. According to the function of the register, the Loop register is divided into the following two groups:

## <span id="LB">**1.LB register**</span>

LB (full name: **Lane Bound Register**) contains 3 registers, named LB0, LB1 and LB2 respectively. Each register width is **16bit**.

- **LB0**: used to store the upper limit of the innermost loop iteration.
- **LB1**: used to store the upper limit value of the middle layer loop iteration.
- **LB2**: used to store the upper limit of the outermost loop iteration.

In data blocks without body (such as [TMA block] (../../blockIntro/tma_block/intro.md) or [CUBE block] (../../blockIntro/cube_block/intro.md)), the LB register is usually used to set the number of rows and columns of data in Tile and other dimension information.

## <span id="LC">**2.LC register**</span>

LC (full name: **Lane Counter Register**) also contains 3 registers, named LC0, LC1 and LC2 respectively. The register width is also **16bit**.

- **LC0**: used to record the ID of the innermost loop iteration.
- **LC1**: used to record the ID of the middle layer loop iteration.
- **LC2**: used to record the ID of the outermost loop iteration.

## Access properties

- The LB register is readable and writable (RW), and can only be set by the [B.DIM](../../header/B.DIM.md) and [C.B.DIM](../../header/C.B.DIM.md) instructions.
- The LC register is read-only (RO).