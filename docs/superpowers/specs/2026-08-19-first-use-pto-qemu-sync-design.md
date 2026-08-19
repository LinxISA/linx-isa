# VECTOR/CUBE First-Use PTO/QEMU Synchronization Design

Date: 2026-08-19

Status: approved direction; implementation review pending

## 1. Goal

Land the LinxISA VECTOR/CUBE first-use exception contract from PR #178, add an
executable QEMU implementation and regression suite, and publish the matching
profile boundary in PTO-SPEC without creating a new release or changing the
existing PTO ELF identity.

The final LinxISA `main` tree must have one machine-readable first-use contract,
one exact PTO profile-hook provenance record, one merged QEMU implementation
pin, and a green model freshness gate.

## 2. Non-goals

- No LinxISA release, version bump, release note, or tag.
- No PTO release, tag, or mutation of the immutable PTO ISA 0.58.2 tag.
- No change to the active `.note.pto.isa` descriptor in this change.
- No LLVM, Linux, glibc, musl, PTOAS, LinxCore, or pyCircuit first-use
  implementation.
- No renumbering of existing non-first-use exceptions.
- No reinterpretation of TEPL `BSTART.VEC` or `BSTART.SFU` as VECTOR first-use
  trigger headers.

## 3. Authority split

### 3.1 Portable PTO release authority

PTO ISA 0.58.1 remains the common released encoding/ELF authority already
locked by LinxISA. PTO ISA 0.58.2 is not imported as the common release in this
change because doing so would change the PTO ELF identity and require an atomic
LLVM, linker, Linux, libc, PTOAS, QEMU, and model release train.

### 3.2 PTO profile-hook authority

PTO-SPEC `main`, currently based on the immutable PTO ISA 0.58.2 tag, receives
a target-profile extension hook for first-use context traps. The portable
default is disabled and carries no Linx-specific trap numbers or ECONFIG bit
positions. The hook requires a target profile to define:

- the covered extension kinds;
- the enabling system-register fields;
- the source and manager ACRs;
- the exact pre-effect ordering point;
- the trap envelope and argument mapping;
- retry and zero-effect guarantees;
- context-save forward-progress obligations.

The LinxISA repository remains the owner of the concrete Linx profile values:
`E_INST(0)`, `EC_PERM(4)`, `TRAPARG0=0/1`, `ECONFIG.V/C=bits32/33`, and
ACR2-to-ACR1 routing.

### 3.3 Exact synchronization record

LinxISA adds a separate machine-readable PTO profile-hook lock containing:

- PTO-SPEC repository URL;
- exact merged PTO-SPEC commit and tree;
- path and SHA-256 of the profile-hook machine contract;
- stable profile-hook identifier;
- the concrete Linx mapping hash.

The existing `isa/v0.58/pto-spec.lock.json` remains byte-identical. This keeps
the common PTO release and ELF identity immutable while proving that the Linx
first-use contract consumes the exact merged PTO profile hook.

## 4. QEMU architecture

### 4.1 State

QEMU stores the complete 64-bit banked `ECONFIG_ACRn` values using the Linx
field layout. Writes mask reserved bits to zero. Reset initializes each bank to
`0x0000000300000008`. Existing banked SSR migration covers the values; a
focused VMState regression proves V/C survive migration and reserved bits do
not.

### 4.2 Trigger classification

VECTOR first-use applies exactly to:

- `BSTART.MPAR`, `BSTART.MSEQ`, `BSTART.VPAR`, `BSTART.VSEQ`;
- `C.BSTART.MPAR`, `C.BSTART.MSEQ`, `C.BSTART.VPAR`, `C.BSTART.VSEQ`.

CUBE first-use applies to canonical operations whose PTO catalog rows have
`family=CUBE` and `engine=CUBE`. QEMU must derive or validate this set against
the LinxISA machine contract rather than maintain an unconstrained second list.

### 4.3 Ordering

For an ACR2 source instruction, QEMU performs:

1. legal decode;
2. block-target and ACR permission validation;
3. first-use enable check against `ECONFIG_ACR1.V/C`;
4. resource allocation and architectural effects.

If enabled, the instruction raises a synchronous precise exception before any
BARG/BSTATE change, tile/vector allocation, queue mutation, memory request, or
completion-state update. The saved execution point is the original block
header so returning software retries the same instruction.

### 4.4 Trap envelope

QEMU writes the managing ACR1 state exactly as follows:

| Field | VECTOR | CUBE |
| --- | ---: | ---: |
| `TRAPNO.E` | `1` | `1` |
| `TRAPNO.ARGV` | `1` | `1` |
| `TRAPNO.TRAPNUM` | `E_INST (0)` | `E_INST (0)` |
| `TRAPNO.CAUSE` | `EC_PERM (4)` | `EC_PERM (4)` |
| `TRAPARG0` | `0` | `1` |
| `ECSTATE.BI` | `0` | `0` |

Handling one kind and clearing its enable bit must not disable the other kind.

## 5. Tests

### 5.1 PTO-SPEC

Add ASL/profile tests that first fail because the profile hook does not exist,
then prove:

- the portable default is disabled;
- a target override observes the required ordering and zero-effect boundary;
- VECTOR and CUBE kinds are distinct;
- the hook is present in requirements, profile-hook metadata, generated docs,
  and repository closure.

### 5.2 QEMU

Add executable tests for:

- exact VECTOR and CUBE trap envelopes;
- all eight VECTOR headers;
- all twelve canonical CUBE operations or a generated catalog-bound matrix;
- invalid decode/target priority over first-use;
- zero BARG/BSTATE/queue/tile/memory effects on trap;
- exact retry after clearing only V or only C;
- ACR1 enable ownership and ACR2 source restriction;
- ECONFIG reset, reserved-bit masking, banking, and VMState round trip;
- negative cases for ACR0/ACR1 execution and TEPL VEC/SFU aliases.

The executable test must inspect architectural state, not only source strings
or decoder metadata.

### 5.3 LinxISA and model

Extend LinxISA validation to require exact equality between the local first-use
contract and the merged PTO profile-hook lock. Update linx-model only to accept
and authenticate the new compiled LinxISA catalog bytes; codec tables and
counts must remain byte-identical because this change adds no encoding.

## 6. Integration order

1. Merge the PTO-SPEC profile-hook PR and capture its canonical commit/tree.
2. Implement and merge the QEMU leaf PR against canonical QEMU `master`.
3. Update linx-model catalog authentication and merge that leaf PR.
4. Update LinxISA PR #178 with the PTO profile-hook lock, merged QEMU/model
   gitlinks, component-lock rows, and focused cross-repo gates.
5. Require all hosted checks on the exact reviewed LinxISA head.
6. Mark PR #178 ready, squash-merge it, prove merge-tree equality, then delete
   only the merged topic branches.

## 7. Acceptance criteria

- PTO-SPEC and QEMU leaf work is merged, not merely present on topic heads.
- The common PTO 0.58.1 lock and ELF identity remain unchanged.
- The PTO profile-hook lock points to the exact merged PTO-SPEC commit/tree and
  validates its file hash.
- QEMU passes focused first-use tests, native unit tests, strict AVS, and full
  AVS sequentially.
- linx-model freshness passes against the updated compiled catalog without
  changing codec counts or generated opcode tables.
- PR #178 has no failed, skipped-required, pending, or stale-head checks.
- No release or tag is created.
