# CSTATE

The Common State Register stores the public status information of the processor and is used by the scheduler to manage the execution status of each core and thread. 

![CSTATE](../../../figs/bitfield/svg/Sysregs/CSTATE.svg)

- **ACR**: This field always reads as the current ACR and is **read-only (RO)**.
- **I**: interrupt enable bit. If this bit is cleared, interrupt access to the ACR is disabled and this field is readable and writable (RW).
- **E**: Endian control bit. This bit controls whether the endianness of memory access is little endian (E=0) or big endian (E=1), but does not control the endianness of instruction reading, which is always little endian. This field is **read-only (RO)**.
- **P**: Supervisor user memory access is enabled. This bit changes the behavior of memory accesses. When this bit is cleared, some memory areas allocated to ACRs with lower permissions may not be available to the current ACR. This field is read-write (RW).
- **FFLAGS**: Accumulated floating-point exception flags indicating exception conditions that have occurred on any floating-point arithmetic instruction since this field was last reset by software. Indicates the occurrence of exceptions for various floating point operations NV, DZ, OF, UF, and NX.
- **FRM**: Floating point calculation rounding mode, used to dynamically control the result rounding mode of floating point operation operations. Contains four modes: RNE, RTZ, RDN, and RUP.

The meaning of each bit in the FFLAGS field is as follows:

| FFLAGS field | identifier | explanation |
|------------|--------|------|
| bit[0] | NV | Illegal operation |
| bit[1] | DZ | divide by zero |
| bit[2] | OF | overflow |
| bit[3] | UF | underflow |
| bit[4] | NX | imprecise |

The meanings of different encodings of the FRM field are as follows:

| FRM | Identifier | Explanation |
|------|-------|--------|
| 000 | RNE | Round to Nearest, ties to Even |
| 001 | RTZ | Round towards Zero |
| 010 | RDN | Round Down/towards -∞ (Round Down/towards -∞) |
| 011 | RUP | Round Up/towards +∞ (Round Up/towards +∞) |
| RESERVE | | |

!!! note "note"

    The P bit cannot be used for safety protection. The current ACR can always change it.

## Remarks

The SSRID of this register is **0x0020**.