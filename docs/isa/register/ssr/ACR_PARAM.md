# ACR_PARAM

The ACRn LxLC parameter register (ACR Parameter Register) is **read-only (RO)** system register, used to specify the LxLC parameters of ARCn.

![ACR_PARAM](../../../figs/bitfield/svg/Sysregs/ACR_PARAM.svg)

**EBS_SZ** is the maximum number of 64-bit integers that ACRn's `EBSTATE` memory needs to hold.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | ACR_PARAM_ACR0 | 0x0f31 |
| ACR1 | ACR_PARAM_ACR1 | 0x1f31 |
| ACR2 | ACR_PARAM_ACR2 | 0x2f31 |
| ... | ... | ... |
| ACRn | ACR_PARAM_ACRn | 0xnf31 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.