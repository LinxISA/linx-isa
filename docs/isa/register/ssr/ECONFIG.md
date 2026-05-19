# ECONFIG

The **exception Configuration Register (Exception Config Register)** is a **readable and writable (RW)** system register used to enable or disable ACR for a specific interrupt and enable or disable triggering for a specific block type for a exception.

The register fields are defined as shown below:

![ECONFIG](../../../figs/bitfield/svg/Sysregs/ECONFIG.svg)

## interrupt control bit

This register controls whether the processor is enabled to receive a specific interrupt. The compiler can use this register to optimize code for interrupt processing. These bits map to the following corresponding interrupt of the ACR:

- **E**: Maps to external interrupt.
- **T**: Map to timer interrupt.

When the corresponding bit is cleared, the corresponding interrupt will not be triggered.

## exception enable bit

These fields are used to control whether the processor triggers the corresponding exception when parsing to a specific block type. The details are as follows:

- **V**: Enable VECTOR type block instruction (packet block MPAR, MSEQ, VPAR, VSEQ block) whether to trigger exception.
- **C**: Enable CUBE type block instruction (package block CUBE block) whether to trigger exception.

The exception enable bit should be initialized to 1 when the processor is powered on or reset. When the corresponding bit is cleared, the corresponding exception will not trigger; otherwise, the corresponding exception will trigger.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | ECONFIG_ACR0 | 0x0f07 |
| ACR1 | ECONFIG_ACR1 | 0x1f07 |
| ACR2 | ECONFIG_ACR2 | 0x2f07 |
| ... | ... | ... |
| ACRn | ECONFIG_ACRn | 0xnf07 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.