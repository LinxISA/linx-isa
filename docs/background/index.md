# What are LinxISA and block instruction?

LinxISA is a general-purpose computing instruction set that combines scalar, floating-point, vector, system, and customizable operation forms under one architectural framework.
Under the LinxISA framework, implementers can extend instructions and system design choices around a common programming model instead of maintaining completely separate machines.

LinxISA is positioned as the core computing infrastructure in the era of artificial intelligence. It aims to cover the three computing modes of scalar (Scalar), vector (Vector) and tensor (Tile) with a unified instruction set, integrate SIMD and SIMT execution paradigms, and open up the boundary between AI and graphics rendering tasks.

By building a native parallel execution architecture centered on block instruction, LinxISA achieves a more versatile and scalable computing instruction system than NVIDIA PTX.

Our goal is to design a new, autonomous and controllable, completely different, and technically competitive ISA from scratch.

From the perspective of instruction set architecture, LinxISA is a technically differentiated instruction set design that is significantly different from x86/ARM/RISC-V.

The processor built on LinxISA is called "Linx processor". Relying on its unique instruction architecture design, Linx processor not only has outstanding advantages in performance, chip area and energy efficiency, but also can effectively avoid intellectual property and patent risks, thereby achieving complete autonomy in chip design.

## Introduction to Linx block instruction

Linx block instruction is the core structured-execution concept in LinxISA.

block instruction combines a set of semantically related and tightly operated micro-instructions into a complete "instruction block" to uniformly define the overall input and output, representing a small task (micro-task) that can be scheduled independently. In many computing scenarios, the instruction block can be equivalently expressed as a tensor calculation (micro-kernel), such as a matrix multiplication, convolution kernel or normalization operation. This "block-based" packaging method not only helps the hardware execute complex operators more efficiently, but also increases the optimization space of the compiler and executor.


  ![block-isa](../figs/intro/granule.PNG){ width="800" }


The compiler emits block-structured binary code on the software side; on the hardware side, the processor no longer has to treat the program as only a flat instruction stream, but can execute the block as a structured unit.

block instruction combines a set of associated microinstructions into a complete "instruction block" and uniformly defines the overall input and output of the block. The compiler compiles the program into binary code in the form of block instruction on the software side; on the hardware side, Linx processor no longer executes the program in the traditional instruction-by-instruction manner, but executes it as a whole according to block instruction.

## Why block instruction is easier to obtain performance improvements

The block instruction set is a hierarchical instruction set with first- and second-level register states. The block instruction dependency and compiler allocation algorithm expresses the entire program hierarchy and defines shared variables and private variables from the instruction level. Linx processor parses and executes the program concurrently according to the two asynchronous pipelines of **header-body**.

![layer](../figs/intro/two-layer.png){ width="800" }

The core of block instruction performance gains are:- Block Level Parallelism: Linx processor can achieve parallel execution at a higher level and achieve significant performance improvements.
- Instruction blocks can be regarded as independent computing tasks, achieving "small task" level parallelism within a single core of Linx processor.
- header and body are separated to realize the decoupling of jump control and actual calculation, improving execution efficiency.
- Hierarchical register management, the hardware can efficiently allocate and reclaim register resources.

## block instruction: Improve instruction set expression granularity

Overall plan: We use block instruction to improve the granularity of instruction information density. block instruction has a **scope** of additional information. Each instruction no longer expresses a single operation, but a series of operations that are expressed as a block of instructions and make modifications to the system atomically.

However, inside block instruction, we have a simple fixed-length RISC instruction set.

![bheader](../figs/intro/block-header.PNG){ width="800" }


Compared with the traditional instruction set, block instruction expresses more information, including:

- **Dependencies between instructions within a block**: Through efficient coding, the instruction dependency graph within a block is directly transferred to the micro-architecture. The micro-architecture no longer needs to use complex algorithms to resolve dependencies, reducing the complexity of the micro-architecture.

## block instruction: Hierarchical instruction set

We encapsulate the heterogeneous and accelerated parts into block instruction and express them at different abstract levels, so that under a common framework, new acceleration units can be enabled under the same programming framework.


  ![hier-isa](../figs/intro/hier-isa.PNG){ width="800" }

- **Fully customized second-layer architecture**: The second-layer instruction set has independent coding space, register and instruction definitions. Extremely scalable. At the same time, it does not affect the first layer architectural state of block instruction. The product line has the ability to customize instructions without destroying the architecture of the hierarchical instruction set.
- **Private and Shared Registers**: Through the representation of the block instruction range, the compiler can express the first and second layers of architectural register and pass this information directly to the hardware. Through the allocation and management of two-layer registers, hardware implementation overhead is greatly reduced.
- **Semantic Scope**: If multiple instructions are combined as a whole, the internal complexity and external complexity are decoupled through the interface. No matter how complicated the Scope is, it will not affect the logical operations outside the Scope. With this information, we can mark a range of instructions, thereby improving the information entropy of instruction marking and providing a more efficient interface for instruction prompt information.

## History of block instruction

The concept of LinxISA was not imagined from scratch, but derived from the existing block instruction set.

Among them, the design of the instruction set of LinxISA mainly comes from this paper from Stanford University:

- [BLISS: Block-Aware Instruction Set Architecture (2006)](https://dl.acm.org/doi/abs/10.1145/1162690.1162694)

LinxISA CPU hardware implementation also mainly uses some data inspiration from the EDGE instruction set. The design concept of the EDGE instruction set originated from the data stream processor in the 1970s. The core point is to execute a series of instructions in the form of a block. The inside of the block is expressed by the dependency graph between instructions, while the outside of the block is still expressed in the traditional controlflow (jump) way.

Regarding the design of the EDGE instruction set, you can refer to the following papers:

- [Scaling to the End of Silicon with EDGE Architectures](https://www.cs.utexas.edu/users/cart/trips/publications/computer04.pdf)

- [Exploiting ILP, TLP and DLP with the Polymorphous TRIPS Architecture](https://www.cs.utexas.edu/users/cart/trips/publications/isca03.pdf)- [TRIPS Reference Manual](https://www.cs.utexas.edu/users/cart/trips/publications/TR-05-19.pdf)

## Why is block instruction designed like this?

For a detailed comparison between block instruction and traditional ARM/RISC-V instructions, please see [block instruction Design Philosophy](./phil.md)