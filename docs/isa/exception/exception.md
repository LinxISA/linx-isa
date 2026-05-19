# exception

exception is an event that is detected synchronously in the instruction pipeline. This kind of event usually causes the pipeline to be logically unable to continue (for example, the requirements of the instruction cannot be met), and must be immediately transferred to other instruction sequences.

exception can occur synchronously during the execution of the instruction. During this process, part of the behavior of the instruction may have taken effect, may not have taken effect, or may have all taken effect. The specific situation and specific instructions are related to the type of exception. If there is no special explanation, by default the specific instruction occurs exception, then all actions required by the instruction will not take effect, and the instruction pointer will still stay on the instruction where exception occurred.

When exception is detected, unless the instruction causing exception comes from the [active repair block] (../arch/fixup.md) that has not been taken over, otherwise `ZXTERMZH38QXZ逻辑核` will enter the [SERVICE_REQUEST] (./acr_switch.md#SR_Process) process.

## exception trap code

Different exception causes can be distinguished by their `陷入代号` and `陷入参数`. The following table lists all supported `陷入代号`:| exception Category | Subcode | Description |
|----------|------|-------|
| **E_INST(0)** | | Instruction related exception |
| | 0 | Command access exception (EC_ACCESS_FAULT) |
| | 1 | Command translation exception (EC_TRANS_FAULT) |
| | 2 | Instruction misaligned (EC_MISALIGNED) |
| | 3 | Illegal command (EC_ILLEGAL) |
| | 4 | Command authority exception (EC_PERM) |
| | 5 | Illegal command page (EC_PF) |
| | 6 | Bus exception (EC_BUS) |
| | 7 | Illegal parameter (EC_PARAM) |
| | 8 | Illegal operation (EC_NV) |
| | 9 | Divide by Zero (EC_DZ) |
| | 10 | Overflow (EC_OF) |
| | 11 | Underflow (EC_UF) |
| | 12 | Imprecise (EC_NX) |
| **E_DATA(1)** | | Data access related exception. When this exception occurs, system register[TRAPARG0](../register/ssr/TRAPARG0.md) is always equal to the address of the data being accessed. |
| | 0 | Memory read exception (EC_LOAD) |
| | 1 | Memory read misalignment (EC_MISALIGNED) |
| | 2 | Memory read page exception (EC_LOAD_PAGE) |
| | 3 | Memory write access exception (EC_STORE_A_ACCESS) |
| | 4 | Memory write address misalignment (EC_STORE_A_MISALIGNED) |
| | 5 | Illegal page for write operation (EC_STORE_A_PF) |
| | 6 | Illegal access range (EC_RANGE) |
| | 7 | Bus exception (EC_BUS) |
| **E_BLOCK(4)** | | Block format exception |
| | 0 | Output unspecified output register (EC_INVAL_SET) |
| | 1 | Read unspecified input register (EC_INVAL_GET) |
| | 2 | Illegal parameter (EC_INVAL_PARM) |
| | 3 | In-block repeat setting register (EC_INVAL_DOUBLESET) |
| | 4 | Incorrect subfix block parameter (EC_INVAL_FIXUP) |
| | 5 | Incorrect block type (EC_TYPE) || 5-14 | | Reserved |
| **E_ASSERT(15)** | | Assert exception (see [assert](../inst/misa_s/ASSERT.md) command for details) |
| **E_SCALL(16)** | | Software active exception (system call) |
| **E_BREAKPOINT(17)** | | software breakpoint |
| 18-61 | | Reserved |
| **E_ISSR(62)** | | Illegal SSRexception |
| **E_NIL(63)** | | exception classification is invalid |

The category of the reason parameter is not specified, and the reason parameter is always 0.

For more specific `陷入参数` that are not generic, please refer to the description context of the specific exception behavior.

## exception routing

The default exception `路由` policy is defined by the following table:

| exception type | Currently executing at ACR0 | Currently executing at ACR1 | Currently executing at ACR2 |
|----------|---------------|---------------|----------------|
| E_INST | ACR0 | ACR1 | ACR1 |
| E_DATA | ACR0 | ACR1 | ACR1 |
| E_BLOCK | ACR0 | ACR1 | ACR1 |
| E_ASSERT | ACR0 | ACR1 | ACR1 |
| E_BREAKPOINT | ACR0 | ACR1 | ACR1 |
| E_ISSR | ACR0 | ACR1 | ACR1 |
| E_SCALL | ACR0 | - | - |

The routing strategy of E_SCALL is determined by the service_type of the request instruction (reference: [acrc](../inst/misa_s/ACRC.md)):

* When service_type is SCT_SYS, ACR2 is routed to ACR1.
* All other valid types are routed to ACR0.

Some extensions may modify the default routing behavior. If this type of extension is enabled, the definition of the extension shall prevail. (There are currently no extensions that modify the default routing behavior)