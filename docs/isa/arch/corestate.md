# Janus Corearchitectural state

The LinxISA architecture enables parallel execution of multi-task blocks through its unique hierarchical design. Janus Core is a converged computing architecture processor based on LinxISA. It uses BCC (Block Control Core) as the core control unit to build a complete computing system.

## **BCC**

As the top-level control center of the system, BCC mainly undertakes the following two key functions:

1. Instruction acquisition and Tile scheduling: Obtain the program Tile (instruction block) through the instruction module, manage the Unified Buffer as a register, express the dependency relationship between each Tile with input/outputTileReg, and complete the dedependency, scheduling and distribution of Tiles;
2. Hybrid computing capability: BCC has a complete built-in scalar computing unit, which allows BCC to not only serve as a control core to manage control flow and branch logic, but also independently execute the load tasks of traditional CPUs. Its computing capabilities cover the complete requirements from scalar operations to complex control flow processing.

It contains the following architectural state internally:

| Name |Bitwidth| Introduction | Description
| ---- | ----| ---- | ---- |
| PC | 64bit | Program Counter | block instruction level pointer |
| BARG | 256bit | Commit Argument | Block commit parameter register |
| R1-R23 | 64bit | Global GPR | Global register, a register accessed by all units |
| T#1-T#4 | 64bit | Temporal Hand | Private T register relative index 1-4 |
| U#1-U#4 | 64bit | Uniform Hand | Private U register relative index 1-4 |

## **VEC**

Vector Core is an efficient processing unit specially designed for AIvector calculations. It adopts group plus SIMD execution mode and has the computing capabilities of scalar and vector. As an out-of-order processor, it cooperates with upstream and downstream modules through the simple block instruction interface to provide high-performance parallel computing support for AI loads.

It contains the following architectural state internally:

| Name |Bitwidth| Introduction | Description
| ---- | ----| ---- | ---- |
| TPC | 64bit | Program Counter | Microinstruction level pointer |
| T#1-T#4 | 64bit | Scalar Temporal Hand | Private scalarT register relative index 1-4 |
| U#1-U#4 | 64bit | Scalar Uniform Hand | Private scalarU register relative index 1-4 |
| VT#1-VT#4 | 32bit | Vector Temporal Hand | Private vectorT register relative index 1-4 |
| VU#1-VU#4 | 32bit | Vector Uniform Hand | Private vectorU register relative index 1-4 |
| VM#1-VN#4 | 32bit | Vector Michealous Hand | Private vectorM register relative index 1-4 |
| VN#1-VN#4 | 32bit | Vector Normalized Hand | Private vectorN register relative index 1-4 |

## **TMU**

**TMU (Tile Manager Unit)** is a hardware unit for users to manage Tile Register and traffic bus.

It contains the following architectural state internally:| Name |Bitwidth| Introduction | Description
| ---- | ----| ---- | ---- |
| TT#1-TT#8 | 512B-32KB | Tile Temporal Hand | Global Tile T register relative index 1-8 |
| TU#1-TU#8 | 512B-32KB | Tile Uniform Hand | Global Tile U register relative index 1-8 |
| TM#1-TN#8 | 512B-32KB | Tile Michealous Hand | Global Tile M register relative index 1-8 |
| TN#1-TN#8 | 512B-32KB | Tile Normalized Hand | Global Tile N register relative index 1-8 |
| SCR | 512B-32KB | Scratch Tile | Private Scratch Tile |

## **CUBE**

Cube is the computing unit responsible for matrix multiplication. Compared with the complex instruction flow of other PEs, Cube only needs to process three instructions: TMATMUL, TMATMUL.BIAS and TMATMUL.ACC (i.e. matrix multiplication and matrix multiplication and accumulation). Therefore, there are no complex control circuits such as instruction fetching, reordering, and control flow in Cube Core.

It contains the following architectural state internally:

| Name |Bitwidth| Introduction | Description
| ---- | ----| ---- | ---- |
| ACC | 512B-32KB | Tile Normalized Hand | Private accumulated Tile |

## architectural state

These templates each have a separate set of register states based on functional requirements, as follows:| Module | Name | Bitwidth | Introduction | Description
| ---- | ---- | ----| ---- | ---- |
| BCC | PC | 64bit | Program Counter | block instruction level pointer |
| BCC | BARG | 256bit | Commit Argument | Block commit parameter register |
| BCC | R1-R23 | 64bit | Global GPR | Global register, a register accessed by all units |
| BCC | T#1-T#4 | 64bit | Temporal Hand | Private T register relative index 1-4 |
| BCC | U#1-U#4 | 64bit | Uniform Hand | Private U register relative index 1-4 |
| VEC | TPC | 64bit | Program Counter | Microinstruction level pointer |
| VEC | T#1-T#4 | 64bit | Scalar Temporal Hand | Private scalarT register relative index 1-4 |
| VEC | U#1-U#4 | 64bit | Scalar Uniform Hand | Private scalarU register relative index 1-4 |
| VEC | VT#1-VT#4 | 32bit | Vector Temporal Hand | Private vectorT register relative index 1-4 |
| VEC | VU#1-VU#4 | 32bit | Vector Uniform Hand | Private vectorU register relative index 1-4 |
| VEC | VM#1-VN#4 | 32bit | Vector Michealous Hand | Private vectorM register relative index 1-4 |
| VEC | VN#1-VN#4 | 32bit | Vector Normalized Hand | Private vectorN register relative index 1-4 |
| TMU | TT#1-TT#8 | 512B-32KB | Tile Temporal Hand | Global Tile T register relative index 1-8 |
| TMU | TU#1-TU#8 | 512B-32KB | Tile Uniform Hand | Global Tile U register relative index 1-8 |
| TMU | TM#1-TN#8 | 512B-32KB | Tile Michealous Hand | Global Tile M register relative index 1-8 |
| TMU | TN#1-TN#8 | 512B-32KB | Tile Normalized Hand | Global Tile N register relative index 1-8 |
| TMU | SCR | 512B-32KB | Scratch Tile | Private Scratch Tile |
| CUBE | ACC | 512B-32KB | Tile Normalized Hand | Private accumulated Tile |

The definitions of MTC and VEC are the same, except that MTC has a mark for DDR memory access, and VEC's mark cannot access DDR.