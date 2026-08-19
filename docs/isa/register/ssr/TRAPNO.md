# TRAPNO

The Trap Number Register is a readable/writable manager-ACR register populated during service-request delivery.

## Wire layout

| Field | Bits | Meaning |
| --- | --- | --- |
| `E` | `[63]` | `1`: synchronous exception; `0`: asynchronous interrupt |
| `ARGV` | `[62]` | `1`: `TRAPARG0` is valid |
| `CAUSE` | `[47:24]` | Cause encoding interpreted by the selected trap class |
| `TRAPNUM` | `[5:0]` | Trap major value |

Bits not listed above are reserved by the current profile.

The existing bring-up trap-number table remains unchanged by the VECTOR/CUBE first-use extension. In particular, PTO-defined `EBREAK` behavior and current ASSERT, E_DATA, E_BLOCK, syscall, and debug values are outside this change.

## VECTOR/CUBE first use

| Field | Value |
| --- | --- |
| `E` | `1` |
| `ARGV` | `1` |
| `TRAPNUM` | `E_INST (0)` |
| `CAUSE` | `EC_PERM (4)` |
| `TRAPARG0` | `0` for VECTOR; `1` for CUBE |
| `ECSTATE.BI` | `0` |

This complete tuple identifies the first-use event. Archived misspellings of `EC_PERM` are not active aliases.
