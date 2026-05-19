# LGPR

**LGPR (Local General Purpose Register)** serves as an intra-block backup of the global register and is only valid in separate blocks.

## **1.Formal parameter register definition**

In the separated block design, each block defines 16 formal parameter registers for binding with the **input/output global register (GPR)** passed in by header. The specific division is as follows:

| Type | Quantity | Register Name | Description |
|------|------|-----------|--------|
| Input register | 12 | **RI0 ~ RI11** | Receive global register input of header |
| Output register | 4 | **RO0 ~ RO3** | Write the calculation result back to the specified global register |

Each formal parameter register is used as a local variable within the block, and its value is dynamically bound by header at runtime.

## **2. Register mapping rules**

The formal parameter register is mapped through the input/output register list specified by the [B.IOR](../../header/B.IOR.md) instruction.

Mapping sequence: Formal parameter registers RI0 ~ RI11 correspond to the first 12 input GGPRs passed in by header. RO0 ~ RO3 correspond to the 4 output GGPRs passed in by header.

- **Input Mapping**:
    - RI0 -> 1st input GGPR
    - RI1 -> 2nd input GGPR
    -...
    - RI11 -> The 12th input GGPR (Note: 12 inputs in total, index 0~11)
- **Output Mapping**:
    - RO0 -> 1st output GPR
    - RO1 -> 2nd output GPR
    -...
    - RO3 -> The 3rd output GPR (Note: 4 outputs in total, index 0~3)

The mapping is dynamically bound at runtime, and different callers can specify different GPRs as input/output.

If the number of input/output registers passed in by header is less than the number of formal parameter registers, then the formal parameter register with a relatively larger number will be in an uninitialized state. **The result of reading an uninitialized parameter register within a block is undefined**.

## **3.Example analysis**

Sample code:
```asm
Header0:
    MPAR .L1_body <LB0:64, LB1:32> [a1, a2, s0], ->T<256B>
Header1:
    MPAR .L1_body <LB0:32, LB1:32> [a3, a4, a5], ->T<128B>
    ...
.L1_body:
    l.madd    lc0.uh, ri0.uh, lc1.uh, ->vu.w      // ri0映射到ZXTERMZH32QXZ第1个输入GPR
    l.lw      [ri1.sd, vu#1.sw<<2],   ->vt.w      // ri1映射到ZXTERMZH32QXZ第2个输入GPR
    l.madd    lc1.uh, ri2.uh, lc0.uh, ->vu.w      // ri2映射到ZXTERMZH32QXZ第3个输入GPR
    l.sw      vt#1.sw, [TO, vu#1.sw<<2]
    bstop
```

| When Header0 is called | When Header1 is called |
|----------------|----------------|
| RI0 -> a1 | RI0 -> a3 |
| RI1 -> a2 | RI1 -> a4 |
| RI2 -> s0 | RI2 -> a5 |
| The remaining RI3~RI11 remain undefined (can be ignored or set to zero) | RI3~RI11 are not initialized |

The same .L1_body body is called multiple times, but different GPRs are passed in each time to achieve parameterized execution.

## **4. Summary**

The separation block is dynamically bound to the GPR passed in by header through the formal parameter register (RI/RO) and has the following advantages:

| Advantages | Description |
|-----|--------|
| Code reuse | Multiple header can share the same body to reduce duplicate code |
| High flexibility | Dynamically bind the input/output register at runtime to adapt to different calling scenarios |
| Performance optimization | Avoid copying data and pass parameters directly through registers |
| Support vectorization and parallelization | Formal parameter design facilitates vector instruction operation (such as v.madd, v.lw) |

This is one of the core mechanisms for LinxISA to achieve efficient, flexible, and scalable computing models.