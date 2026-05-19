# TRAPNO

The exception reason register (Trap Number Register) is **readable and writable (RW)** system register, updated by the service request **SERVICE_REQUEST** process, and is used to store the initiation reason of the source ACR that initiated the service.

![TRAPNO](../../../figs/bitfield/svg/Sysregs/TRAPNO.svg)

- **TRAPNUM**: Indicates the trap code. This field is set by the service request **SERVICE_REQUEST** program.
- **CAUSE**: This field defines the detailed reason for the service request, see the Exception Cause section for all combinations of `Trap Number` and `TrapCause Number`.
- **E**: When synchronous exception occurs, E is set to 1, when asynchronous interrupt occurs, E is set to 0.

## exception Reason<table border="2">
<caption>exception reason list</caption>
  <tr>
    <th >Caught in code</th>
    <th >Meaning</th>
    <th colspan="2">Reason code</th>
    <th colspan="2">Meaning</th>
  </tr>
  <tr>
    <td rowspan="8">E_INST(0)</td>
    <td rowspan="8">Instruction related exception</td>
    <td colspan="2">EC_ACCESS_FAULT(0)</td>
    <td colspan="2">Instruction access exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_TRANS_FAULT(1)</td>
    <td colspan="2">Instruction translation exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_MISALIGNED(2)</td>
    <td colspan="2">Instructions are not aligned</td>
  </tr>
  <tr>
    <td colspan="2">EC_ILLEGAL(3)</td>
    <td colspan="2">Illegal command</td>
  </tr>
  <tr>
    <td colspan="2">EC_PERM(4)</td>
    <td colspan="2">Command permission exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_PF(5)</td>
    <td colspan="2">Illegal command page</td>
  </tr>
  <tr>
    <td colspan="2">EC_BUS(6)</td>
    <td colspan="2">Bus exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_PARAM(7)</td>
    <td colspan="2">Illegal parameters</td>
  </tr>
  <tr>
    <td rowspan="8">E_DATA(1)</td>
    <td rowspan="8">Data access related exception</td>
    <td colspan="2">EC_LOAD(0)</td>
    <td colspan="2">Memory reading exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_MISALIGNED(1)</td>
    <td colspan="2">Memory reads are not aligned</td>
  </tr>
  <tr>
    <td colspan="2">EC_LOAD_PAGE(2)</td>
    <td colspan="2">Illegal read operation page</td>
  </tr>
  <tr>
    <td colspan="2">EC_STORE_A_ACCESS(3)</td>
    <td colspan="2">Memory write access exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_STORE_A_MISALIGNED(4)</td>
    <td colspan="2">Incomplete memory write addresses</td>
  </tr>
  <tr>
    <td colspan="2">EC_STORE_A_PF(5)</td>
    <td colspan="2">Illegal write operation page</td></tr>
  <tr>
    <td colspan="2">EC_RANGE(6)</td>
    <td colspan="2">Illegal access scope</td>
  </tr>
  <tr>
    <td colspan="2">EC_BUS(7)</td>
    <td colspan="2">Bus exception</td>
  </tr>
  <tr>
    <td rowspan="5">E_BLOCK(4)</td>
    <td rowspan="5">Block format exception</td>
    <td colspan="2">EC_INVAL_SET(0)</td>
    <td colspan="2">Output unspecified output register</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_GET(1)</td>
    <td colspan="2">Read unspecified input register</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_PARM(2)</td>
    <td colspan="2">Illegal parameters</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_DOUBLESET(3)</td>
    <td colspan="2">Repeat setting register within block</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_FIXUP(4)</td>
    <td colspan="2">Incorrect sub-repair block parameters</td>
  </tr>
  <tr>
    <td rowspan="5">E_FLOAT(5)</td>
    <td rowspan="5">Floating point exception</td>
    <td colspan="2">EC_INVAL_OPERATION(0)</td>
    <td colspan="2">Illegal operation exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_DIVISION_BY_ZERO(1)</td>
    <td colspan="2">except except by 0</td>
  </tr>
  <tr>
    <td colspan="2">EC_OVERFLOW(2)</td>
    <td colspan="2">Overflow exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_UNDERFLOW(3)</td>
    <td colspan="2">Underflow exception</td>
  </tr>
  <tr>
    <td colspan="2">EC_INEXACT(4)</td>
    <td colspan="2">Inexact exception</td>
  </tr>
  <tr>
    <td rowspan="1">E_ASSERT (15)</td>
    <td colspan="6">Assert exception (please refer to the definition of the assert instruction for the generation principle)</td>
  </tr>
  <tr>
    <td rowspan="1">E_SCALL(16)</td>
    <td colspan="6">Software active exception (system call)</td>
  </tr>
  <tr>
    <td rowspan="1">E_BREAKPOINT(17)</td>
    <td colspan="6">software breakpoint</td>
  </tr>
  <tr>
    <td rowspan="1">18-61</td><td colspan="6">Reserved</td>
  </tr>
  <tr>
    <td rowspan="1">E_ISSR(62)</td>
    <td colspan="6">Illegal SSRexception</td>
  </tr>
  <tr>
    <td rowspan="1">E_NIL(63)</td>
    <td colspan="6">This value is used to indicate that the exception classification is invalid</td>
  </tr>
</table>

!!! note "note"

    The EC_prefix name is a exception cause name and is only valid in the specific `Trap Number`.

## Address space

The naming and addressing space of this register differs in each ACR, as follows:

| ACR level | Register name | Address space |
|---------|---------|---------|
| ACR0 | TRAPNO_ACR0 | 0x0f02 |
| ACR1 | TRAPNO_ACR1 | 0x1f02 |
| ACR2 | TRAPNO_ACR2 | 0x2f02 |
| ... | ... | ... |
| ACRn | TRAPNO_ACRn | 0xnf02 |

Among them, the "_ACR{m}" suffix indicates that the register is accessed from ACR{m}.