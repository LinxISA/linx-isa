# VGPR

The vector register is called **VGPR (General Purpose Vector Register)** and is used to store and manage intermediate results of multi-threaded calculations.

vector registers are managed through **register queue** and encoded using **relative index**.

In the current version, 4 vector register queues are defined in LinxISA, named VT, VU, VM, and VN respectively. Each queue contains 4 registers.

| Queue type | Register name | Alias | Description |
|------------|-----------|--------|------------------------|
| VT register queue | VTR1-VTR4 | VT#1-VT#4 | Save the results of T register queue |
| VU register queue | VUR1-VUR4 | VU#1-VU#4 | Save the results of U register queue |
| VM register queue | VMR1-VMR4 | VM#1-VM#4 | Save the results of M register queue |
| VN register queue | VNR1-VNR4 | VN#1-VN#4 | Save the results of N register queue |

## Register bit width

The vector register width is not fixed and can be 64bit (.d), 32bit (.w), 16bit (.h), 8bit (.b). The actual bit width is defined by the instruction used.

Examples are as follows:
```asm
    l.lwi [a3, 8], ->vt.w     # 指示指令输出寄存器位宽为32bit（.w）
    l.lwi [a1, 8], ->vt.w     # 指示指令输出寄存器位宽为32bit（.w）
    l.add vt#1.sw, vt#1.sw, ->vt.w
```

## Reuse feature

When the vector register is used as the input of an instruction, it is allowed to have the **reuse** flag. Its semantics are:

- When the source register is marked as reuse: the register must remain available after the current instruction is executed and committed, and the hardware must not release the register at this commit point.
- When the source register is not marked as reuse: When the current instruction is submitted, the occupation of this register can be reclaimed by hardware (kill/release), and subsequent instructions should no longer use this register.

Visibility and lifecycle:

- Marking it as reuse only affects the register retention behavior when the current instruction is submitted, ensuring that its value can still be read in subsequent instructions.
- Source registers not marked for reuse are no longer guaranteed to be readable after the current instruction is committed; any subsequent read from them is illegal.

On subsequent reads of registers that have been freed, the hardware must generate exception.

Example description
```asm
v.lwi [ri0, 0], ->vt.w ; i0
v.lwi [ri0, 4], ->vt.w ; i1
v.lwi [ri0, 8], ->vt.w ; i2
v.add vt#1.sw, vt#2.reuse.sw, ->vt.w ; i3
```

In i3, using the `.reuse` mark for the vt#2 source operand means that after i3 commits, the register corresponding to vt#2 must not be released by the hardware, allowing subsequent instructions to continue reading the register; if `.reuse` is not marked, the register can be recycled after i3 commits, and subsequent reads should trigger exception.

The reuse attribute only applies to source registers and does not affect the allocation and release strategy of destination registers.

## Access properties

This set of registers are both readable and writable (RW).