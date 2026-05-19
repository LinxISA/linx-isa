# EOIEI

The interrupt End of Interrupt Register is **Write Only (WO)** system register, used to indicate the end of interrupt processing, allowing the processor to return to normal execution state.

![EOIEI](../../../figs/bitfield/svg/Sysregs/EOIEI.svg)

- **IntID**: When this field is written, LxLC will delete the corresponding pending bit of interrupt in the [IPENDING](./IPENDING.md) register.

All valid values that can be used as IntID are listed here:

- 0, ACR0_EI, Accepted only from EOIEI_ACR0.
- 1, ACR0_TI, Accepted only from EOIEI_ACR0.
- 2, ACR1_EI, Accepted only from EOIEI_ACRn where n p>= 1.
- 3, ACR1_TI, Accepted only from EOIEI_ACRn where n p>= 1.

LxLC does nothing if another value is written.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | EOIEI_ACR0 | 0x0f0a |
| ACR1 | EOIEI_ACR1 | 0x1f0a |
| ACR2 | EOIEI_ACR2 | 0x2f0a |
| ... | ... | ... |
| ACRn | EOIEI_ACRn | 0xnf0a |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.