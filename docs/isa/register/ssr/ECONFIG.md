# ECONFIG

`ECONFIG_ACRn` is a 64-bit readable/writable exception and interrupt configuration register. It is independent per hardware thread and per manager ACR.

## Field layout

| Field | Bit | Meaning |
| --- | ---: | --- |
| `E` | `0` | External-interrupt enable |
| `T` | `1` | Timer-interrupt enable |
| `S` | `2` | Software-interrupt enable |
| `A` | `3` | `ASSERT` instruction exception enable |
| Reserved | `31:4` | Must be written as zero; reads return zero |
| `V` | bit 32 | VECTOR first-use exception enable |
| `C` | bit 33 | CUBE first-use exception enable |
| Reserved | `63:34` | Must be written as zero; reads return zero |

Reset value: `0x0000000300000008`.

## First-use control

For the current unreleased v0.58 main contract, `ECONFIG_ACR1.V/C` controls first use by an ACR2 task:

- `V=1`: a covered VECTOR block header traps before execution;
- `C=1`: a covered CUBE block header traps before execution;
- `0`: the corresponding first-use trap is disabled.

Handling one extension clears only its own bit. Software rewrites both bits for the next task before returning to ACR2. The reset value does not replace per-task programming.

## Address space

| Manager ACR | Register | SSR ID |
| --- | --- | --- |
| ACR0 | `ECONFIG_ACR0` | `0x0F07` |
| ACR1 | `ECONFIG_ACR1` | `0x1F07` |
| ACR2 | `ECONFIG_ACR2` | `0x2F07` |
| ACRn | `ECONFIG_ACRn` | `0xnF07` |
