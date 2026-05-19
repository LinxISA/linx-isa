# Data transfer block

## Function Overview

The TMA (Tile Memory Access) data movement block is a dedicated data movement engine in the tensor computing architecture. It is responsible for establishing an efficient and programmable data transmission path between the memory subsystem and Tile registers. This module provides continuous data supply and result write-back capabilities to the computing core through hardware-accelerated multi-dimensional data movement operations. It is a key interface connecting the storage layer and the computing unit.

## Core Competencies

| Function | Description |
|------|--------|
| **Multi-dimensional data movement** | TMA supports structured access to multi-dimensional tensor data, and can efficiently handle matrix, tensor and other non-contiguous memory access modes. Through the built-in address generation unit, TMA can automatically calculate complex memory access patterns, including but not limited to:<br>1. Strided Access (Strided Access)<br>2. Block Transfer (Block Transfer)<br>3. Broadcast Operation (Broadcast)<br>4. Data Rearrangement (Data Rearrangement) |
| **Asynchronous Parallel Execution** | TMA uses an independent hardware execution engine to support parallel operations with computing units:<br>1. Non-blocking transmission: data transmission deeply overlaps with the computing pipeline<br>2. Command queue: supports queuing and scheduling of multiple transmission operations<br>3. Priority management: configurable transmission priority and control |
| **Zero-overhead data management** | Optimized management of data transmission through dedicated hardware:<br>1. Automatic address generation: eliminates the additional overhead of software address calculation<br>2. Burst transmission optimization: maximizes memory bandwidth utilization<br>3. Data format conversion: supports transparent conversion of computing formats and storage formats |

## Architecture positioning

TMA is located between the memory controller and the computing unit and serves as an intelligent scheduler for data flow:
```
内存子系统 → TMA数据搬运块 → Tile寄存器阵列 → 计算单元
```
This design achieves the decoupling of storage access and computing execution, allowing the computing unit to focus on arithmetic and logical operations, while the data supply is guaranteed by dedicated hardware.

Interface with computing unit

- Data supply interface: Provides input data loading services to computing units
- Result recovery interface: receives the output data of the computing unit and writes it back to the memory
- Inter-register transfer: supports data reorganization and copying within the Tile register array

## block type Features

- Data transfer block** only supports Fall jump mode**
- The data transfer block allows access to the global register GGPR, Tile register, and memory.
- The data transfer block allows up to 8 Tile registers to be read and 4 tile registers to be written in one block.
- There is no body in the data transfer block, **B.TEXT instruction is not allowed**