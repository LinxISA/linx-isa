# Manager ACR dedicated system register

The addressing space of the SSR dedicated to the manager ACR is visible to all ACRs, but is only supported by some ACRs with management functions.

These SSRs follow the following rules:

- These registers are only accessible in ACR0 and ACR1. Accessing this range from other ACRs may have no effect or may trigger illegal SSRexception.
- These registers have different addresses for different ACRs.
- The "_ACRn" suffix indicates that this function must be accessed from ACRn, and accessing from different ACRs can exhibit different behaviors.

## interrupts and exceptions Management Register| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0xnf00 | [ECSTATE_ACRn](./ECSTATE.md) | Exception State Register | exception Status Register |
| 0xnf01 | [EVBASE_ACRn](./EVBASE.md) | Exception Vector Base Register | exceptionvector base address register |
| 0xnf02 | [TRAPNO_ACRn](./TRAPNO.md) | Trap Number Register | exception Reason Register |
| 0xnf03 | [TRAPARG0_ACRn](./TRAPARG0.md) | Trap Argument 0 Register | exception parameter 0 register |
| 0Xnf04 | Reserved | - | - |
| 0xnf05 | [ETEMP_ACRn](./ETEMP.md) | Exception Temporary Register | exception context saving temporary register |
| 0xnf06 | [FUTO_ACRn](./FUTO.md) | Fixup Takeover Register | exception Repair takeover register |
| 0xnf07 | [ECONFIG_ACRn](./ECONFIG.md) | Exception Configuration Register | exception Configuration Register |
| 0xnf08 | [IPENDING_ACRn](./IPENDING.md) | Interrupt Pending Register | interrupt pending register |
| 0xnf09 | [TOPEI_ACRn](./TOPEI.md) | Top Interrupt ID Register | TOPinterruptID register |
| 0xnf0a | [EOIEI_ACRn](./EOIEI.md) | End of Interrupt Register | interruptEnd Register |
| 0xnf0b | [EBPC_ACRn](./EBPC.md) | BPC of Exception Block | BPC of exceptionblock instruction |
| 0xnf0c | [EBARG_ACRn](./EBARG.md) | Arguments of Exception Block | Parameters of exceptionblock instruction |
| 0xnf0d | [ETPC_ACRn](./ETPC.md) | TPC of Exception Instruction | TPC of exception microinstruction || 0xnf0e | [EBPCN_ACRn](./EBPCN.md) | Next BPC of Exception Block | exceptionblock instructionBPC of the next block |

## Memory management register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0x1f10 | [MMTBASE_ACR1](./MMTBASE.md) | Memory Management Translation Base Register for ACR1 | Memory Management Translation Base Register |
| 0x1f11 | [MMCONFIG_ACR1](./MMCONFIG.md) | Memory Management Configuration Register for ACR1 | Memory Management Configuration Register |

## Clock management register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0xnf20 | [TIMER_TIME_ACRn](./TIMER_TIME.md) | Timer Register | Timer Register |
| 0xnf21 | [TIMER_TIMECMP_ACRn](./TIMER_TIMECMP.md) | Timer Compare Register | Timer Comparator Register |

## Others

| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0xnf30 | [XBINFO_ACRn](./XBINFO.md) | Cross Block Info Register | XB block initialization register |
| 0xnf31 | [ACR_PARAM_ACRn](./ACR_PARAM.md) | ACR Parameter Register | ACRn LxLC parameter register |

*n is the ACR ID of the manager ACR.