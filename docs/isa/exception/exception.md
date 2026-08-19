# Exceptions

An exception is a synchronous event detected while processing an instruction. Unless an instruction-specific rule states otherwise, the faulting instruction commits no architectural effects and the saved execution point identifies that instruction for retry.

`TRAPNO` carries the trap class and cause. `TRAPARG0` carries an additional argument when `TRAPNO.ARGV=1`. See [TRAPNO](../register/ssr/TRAPNO.md) for the wire format.

## Recoverable exceptions during block execution

When a recoverable exception occurs after a block has entered execution, hardware must freeze the faulting block and preserve every state element needed to continue it. Hardware must not overwrite or release those resources until software saves the state or explicitly terminates the block.

The retained state includes, at minimum:

- block-register contents;
- execution and sequence progress;
- predicate and control state;
- outstanding-operation state;
- any additional architectural cursor needed for restart.

Software may export the retained state with a state-save block such as `ESAVE`. Implementations must provide an independent save path or reserve enough registers, queue entries, and issue capacity for `ESAVE` to make progress even when the faulting block occupies all ordinary resources.

The current profile distinguishes block families as follows:

1. VECTOR blocks may raise architecturally defined recoverable internal exceptions.
2. CUBE blocks do not raise CUBE-owned recoverable exceptions after execution starts.
3. TLSU blocks do not raise TLSU-owned recoverable exceptions. Translation, permission, and bus faults raised by the memory system remain `E_DATA` exceptions.
4. VECTOR/CUBE first-use exceptions occur before block execution and are not internal block exceptions.

`TMA` is a historical name for TLSU and is not used by the active profile.

## VECTOR/CUBE first-use exception

The first-use mechanism lets an ACR1 kernel allocate and restore VECTOR or CUBE context only when an ACR2 task needs it. It is a precise pre-execution exception.

### Trigger set

VECTOR first-use checks apply to:

- `BSTART.MPAR`, `BSTART.MSEQ`, `BSTART.VPAR`, and `BSTART.VSEQ`;
- the corresponding `C.BSTART.*` forms.

`BSTART.VEC` and `BSTART.SFU` are TEPL assembly aliases and do not belong to this VECTOR first-use set.

CUBE membership is derived from canonical PTO operation rows whose `family` and `engine` are both `CUBE`.

### Exact trap envelope

| Field | VECTOR | CUBE |
| --- | ---: | ---: |
| `TRAPNO.E` | `1` | `1` |
| `TRAPNO.ARGV` | `1` | `1` |
| `TRAPNO.TRAPNUM` | `E_INST (0)` | `E_INST (0)` |
| `TRAPNO.CAUSE` | `EC_PERM (4)` | `EC_PERM (4)` |
| `TRAPARG0` | `TRAPARG0 = 0` | `TRAPARG0 = 1` |
| `ECSTATE.BI` | `0` | `0` |

Archived v0.55 material contains a misspelling of `EC_PERM`; that spelling is not an active alias.

### Ordering and precision

The processor performs legal decode and ACR permission checks before the first-use check. It performs the first-use check before BARG/BSTATE mutation, extension-context allocation, queue admission, memory issue, or any other effect.

An invalid encoding or invalid block target therefore keeps its normal exception priority. If first use traps, the saved PC identifies the original block header. After software handles the exception, the same header can be retried without duplicate effects.

### Kernel handling

For a never-used extension, the kernel allocates and initializes its task context, marks it resident, clears only the corresponding `ECONFIG_ACR1.V` or `.C` bit, and retries the original header.

For a previously used but nonresident extension, the kernel restores the saved context, marks it resident, clears only the corresponding bit, and retries. Handling VECTOR must not clear CUBE enable, and handling CUBE must not clear VECTOR enable.

Task software must distinguish:

| State | Context allocated | Resident in hardware | Enable bit |
| --- | --- | --- | --- |
| `NEVER_USED` | no | no | `1` |
| `SAVED_NOT_RESTORED` | yes | no | `1` |
| `LIVE` | yes | yes | `0` |

On context switch, software saves only used, resident contexts. Before returning to ACR2, it programs `ECONFIG_ACR1.V/C` for the next task; configuring the bits only once during kernel boot is insufficient.

## Routing

The first-use exception is synchronous (`TRAPNO.E=1`) and follows the normal `E_INST` route. In the current unreleased v0.58 main contract, an exception from ACR2 is delivered to ACR1.
