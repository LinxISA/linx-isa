# System control instructions

System control instructions are mainly divided into **execution control instructions**, **assertion instructions**, **memory barrier instructions** and **system call instructions**.

## Execute control instructions

Execution control instructions play a key role in computer systems. They are used to control the execution process of the system, including managing communication and coordination between different components of the system to ensure that the system can perform tasks efficiently and orderly. These instructions usually involve functions such as system management, event processing, state transfer, and resource release.

## Assertion directive

Assertion instructions are usually used to check conditions during system execution. If the conditions are not met, exception or interrupt will be triggered so that errors can be discovered and handled in time.

## Memory barrier instructions

### What is a memory barrier?

Most modern computers use out-of-order execution in order to improve performance, which may cause the program running order to not meet our expectations. The memory barrier instruction is a type of synchronization barrier instruction, which is a synchronization point in the random access operation of the memory by the CPU or compiler. Operations after the synchronization point can only be executed after all read and write operations before the synchronization point are completed.

### Why does a memory barrier appear?

In order to solve the problem of out-of-order memory access during the running of the program, out-of-order memory access is to improve the performance of the program when it is running, and the memory barrier can allow the CPU or compiler to access the memory in an orderly manner.

## System call instructions

System call instructions are a type of instructions used to call operating system services in a computer system. These instructions allow user programs or kernel modules to request the operating system to perform specific tasks, such as file operations, network communications, memory management, process scheduling, etc. System call instructions usually involve conversion from user mode to kernel mode, requiring strict permission control and context switching.


## System control instruction list

| Microinstructions | Assembly format | Description |
|--------|---------------|------------------------------------------------|
|Execution control instructions| | |
| BSE | bse SrcL | `发送` customize `事件` to external system |
| BWE | bwe SrcL | The current thread of the processor enters sleep state `等待` external `事件` wakes up |
| BWI | bwi SrcL | The current thread of the processor enters the sleep state `等待` external `ZXTERMZH42QXZ` wakes up |
| BWA | bwa SrcL | The current thread of the processor enters sleep state and waits for `指定地址对应Cacheline进入Cache后` to wake up |
| ASSERT | assert SrcL | After meeting the condition that SrcL is 0, terminate the program, trigger the assertion exception, and jump to the active repair block for processing |
|Memory Barrier Instructions| | |
| DSB | dsb perd_imm, succ_imm | Used to synchronize data streams |
| ISB | isb | used to synchronize instruction flow |
|System call instructions| | |
| ACRC | acrc request_type | Set the system call status of the current block, and initiate the corresponding system request after the block is submitted |
| ACRE | acre SrcL, ACRn | Set and switch to target ACR |

The instructions are encoded as follows:

![excutecontrol](../../../figs/bitfield/svg/Introduction_32bit/ExecutionControl.svg)