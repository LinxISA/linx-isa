# ECSTATE

The exception status register (Exception State Register) saves the current exception status and is used for exception and interrupt processing. Software can understand the processing flow when exception occurs based on this register.

![ECSTATE](../../../figs/bitfield/svg/Sysregs/ECSTATE.svg)

## BI

**BI (Block Interrupted)** is the flag bit in body that triggers exception. It is used to identify whether the exception service request SERVICE_REQUEST occurs in body. If it occurs within body, this bit is set to 1, otherwise it is cleared.

The software can decide whether to save and restore the state in the block based on whether the BI bit is set.

All other fields have the same definition as the [CSTATE](./ECSTATE.md) register.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | ECSTATE_ACR0 | 0x0f00 |
| ACR1 | ECSTATE_ACR1 | 0x1f00 |
| ACR2 | ECSTATE_ACR2 | 0x2f00 |
| ... | ... | ... |
| ACRn | ECSTATE_ACRn | 0xnf00 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.