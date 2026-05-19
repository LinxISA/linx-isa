# FUTO

The exception Repair Takeover Register (Fixup Takeover Register) is **readable and writable (RW)** system register, used to configure the repair block takeover.

![FUTO](../../../figs/bitfield/svg/Sysregs/FUTO.svg)

This register stores the status of exception repair takeover, helping the operating system to process and repair exception scenarios.

Its format is defined as follows:

| futo bits | assembly symbols | exception reason | description |
| --------- | --------|-------------------------- | ----------------------- |
| 0 | LF |E_DATA(1)-EC_LOAD(0) | Memory load (Load) access error |
| 1 | LMA |E_DATA(1)-EC_MISALIGNED(1) | Memory load (Load) is not aligned |
| 2 | SF |E_DATA(1)-EC_STORE_A_ACCESS(3) | Memory write (Store) access error |
| 3 | SMA |E_DATA(1)-EC_STORE_A_MISALIGNED(4) | Memory write (Store) is not aligned |
| 4 | A |ASSERT EXCEPTIONS | trigger assertexception |

- When this bit is set, the corresponding exception will be taken over by the corresponding ACR's exception handler.
- On system reset, all futo bits are set to 0 by default.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | FUTO_ACR0 | 0x0f06 |
| ACR1 | FUTO_ACR1 | 0x1f06 |
| ACR2 | FUTO_ACR2 | 0x2f06 |
| ... | ... | ... |
| ACRn | FUTO_ACRn | 0xnf06 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.