# Incremental scalar alignment with PTO

## Authority and verified baseline

PTO is the scalar semantic authority. This work uses the exact development
golden `f0a876e449a95d26841c5ee7affb4c905ebc5f5b`, tree
`fe9e8e050375fbce3f526d08acca13c37cd15830`, recorded in
`isa/v0.58/pto-scalar-proposal.lock.json`. Upstream main was inspected at
`a5551dbb6c5ea48a8db7913eaf26140fc4caf2e9`: its `asl/`, `spec/catalog/` and
`spec/development-manifest.json` have no changes relative to that golden.

The full scalar source comparison passes for all 473 forms:

| Family | Forms |
| --- | ---: |
| AGU | 183 |
| ALU | 107 |
| AMO | 59 |
| BRU | 58 |
| SYS | 36 |
| FSU | 30 |

This proves catalog, field, constraint and encoding-identity alignment. It does
not prove all executable semantics. The bounded execution audit confirmed the
ADDTPC page-offset defect corrected here and the remaining reservation defects
below. It also found incorrect flat-GPR treatment of Reg5 queue/discard codes;
the changed paths now implement discard and reject unsupported queues before
effects. Sail's existing PCR arithmetic already matches the executable ASL when
the current-instruction PC state is mapped coherently; this increment guards
and factors that arithmetic without claiming a PCR behavior fix in Sail.
Sampled word-result normalization, load extension and right-modifier families
did not reveal another mismatch; unsampled behavior remains unverified.

No catalog bytes, instruction encodings, component pins or ELF identities are
changed by this increment. DMA.FREE.S/L and MCOPY.DS/DL remain encoding-only,
NOT IMPLEMENTED, as previously agreed.

## Executable ASL cross-check

The owning PTO tests were actually executed with the pinned ASLRef commit
`5873cbb69312d92b4b97131cff840ec621b12ddf` (tested binary SHA-256
`a80d9821a7e3b084ee87f32fda01161d943201869b1d9c91b01102dcee14568e`).
The targeted group passed 9/9; the PCR group passed 24/24, covering all 22
PCR direct-execution tests and word/doubleword boundary representatives.
Those groups overlap in one LBU.PCR test, for 32 unique owning test points.
ADDTPC/HL.ADDTPC page and signed-boundary tests and SC.W miss/success/precise
fault tests are included. The selected IDs are checked in at
`tools/isa/scalar_asl_reference_tests.txt`.

The checked-in `isa/sail/tests/pto_scalar_address_reference.asl` also executes
the real PTO decoder/handlers on a shared coherent-PC probe: at `_PC=0x1002`,
LBU.PCR immediate 1 reports the computed address `0x1004` through its expected
data-page fault, and ADDTPC immediate 1 writes `0x2002` to GPR3. It also checks
the reference dispatch's retirement advance. Sail checks compare the address
and register results, not complete memory/fault/retirement state equivalence.
A negative control changing the expected ADDTPC result to `0x2003` failed with
ASLRef's dynamic assertion error and exit status 1, confirming execution rather
than type-checking alone. The shared probe passed with two existing Tile
MOD/DIVRM constraint warnings from the full upstream model.

Reproduce from the exact PTO checkout after preparing its pinned ASLRef. Set
`LINX_ROOT` to this checkout and `PTO_ASLREF_ROOT` to the prepared interpreter
source cache when it is outside the PTO checkout's default cache:

```sh
cd "$PTO_GOLDEN_ROOT"
mkdir -p build
scripts/print-asl-test-matrix --page-count 1 \
  --ids-file "$LINX_ROOT/tools/isa/scalar_asl_reference_tests.txt" \
  > build/linx-scalar-matrix.json
scripts/run-asl-page --matrix build/linx-scalar-matrix.json -j 4 --timeout-seconds 900
make build/pto-spec.asl
scripts/assemble-asl build/linx-scalar-reference.asl build/pto-spec.asl \
  "$LINX_ROOT/isa/sail/tests/pto_scalar_address_reference.asl"
scripts/aslref --type-check-strict build/linx-scalar-reference.asl
```

## Increment 1: scalar address materialization from architectural TPC

The 22 affected forms are `{LB,LBU,LH,LHU,LW,LWU,LD,SB,SH,SW,SD}.PCR` and their
`HL.` equivalents. Every one has `agu.offset_scale = 2`, including byte and
doubleword accesses. The scale is not inferred from access size.

The owning PTO dispatch contract is
[`asl/scalar/model/dispatch/agu.asl`](https://github.com/PTO-ISA/pto-spec/blob/f0a876e449a95d26841c5ee7affb4c905ebc5f5b/asl/scalar/model/dispatch/agu.asl).
It requires:

```text
EA = ((TPC & ~3) + (sign_extend(encoded_immediate) << 2)) mod 2^64
```

| Form | Signed field | Representable byte displacement |
| --- | ---: | --- |
| L32 PCR | 17 bits | -262144 through 262140, in steps of 4 |
| HL48 PCR | 29 bits | -1073741824 through 1073741820, in steps of 4 |

The executable PTO `asl/arch/state/program-counter.asl` implements both
`ReadPC()` and `ReadTPC()` by reading the same `_PC` storage. A synthetic test
with different Sail `pc` and `tpc` values therefore cannot, by itself, establish
a PTO mismatch. This change preserves Sail's existing `read_pc_or_tpc()` adapter
and shares the already-correct PCR arithmetic across all 22 paths. Cross-model
cases bind the staged PC values coherently. Signed/unsigned load normalization
and store widths are preserved. Natural access alignment is separate; for
example, a doubleword access to an address that is 4 modulo 8 can still fault.

The new source-contract gate derives the inventory, displacement widths,
scales, decoded source/destination bindings, memory payloads and load
publication from the authenticated PTO catalog.
Mutation tests reject missing forms, unscaled offsets, use of the wrong PC,
wrong sign extension, wrong memory width/normalization, constant store payloads,
dropped load results and wrong destinations. Executed Sail
directed tests independently cover current TPC at 2 modulo 4,
positive/negative displacements, 17/29-bit boundaries and 64-bit wraparound.

Run both parts of the proof:

```sh
python3 tools/isa/check_pto_scalar_proposal.py --pto-root "$PTO_GOLDEN_ROOT"
python3 tools/isa/check_scalar_pcr_contract.py
python3 -m unittest tools.isa.test_scalar_pcr_contract
opam exec --switch=sail-4.14.3 -- python3 tools/bringup/check_sail_model.py \
  --require-parser --require-c-backend
```

ADDTPC and HL.ADDTPC incorrectly shifted their signed displacement by one.
PTO's `AddToPC` in
[`asl/scalar/model/bru/semantics.asl`](https://github.com/PTO-ISA/pto-spec/blob/f0a876e449a95d26841c5ee7affb4c905ebc5f5b/asl/scalar/model/bru/semantics.asl)
requires `TPC + (signed page displacement << 12)`. These two Sail paths now
use that formula through the existing PC adapter, preserve the low TPC bits and
write a supported GPR destination or discard destination. Directed execution
covers zero, both signs, 20/32-bit extrema,
wraparound and the raw ADDTPC word `0x00001087`. Unlike PCR, ADDTPC must not
align its TPC base down to four bytes.

The ASL operand implementation also exposes a pre-existing Sail limitation:
`read_reg5`/`write_regdst` treat codes 24..31 as flat GPR slots instead of
temporary queues or discard destinations. The changed 24 instruction paths
therefore explicitly support GPR sources 0..23, GPR destinations 0..23, and
discard destinations 24..29. Queue sources 24..31 and queue destinations 30/31
reject before memory/source/destination effects in this staged model. These are
valid golden encodings with unimplemented model behavior, not newly reserved
ISA encodings. Directed tests prove discard slots remain unchanged and queue
rejection does not reach host memory hooks. Other instructions' flat Reg5
handling remains part of the next increment.

The directed interpreter does not supply the host memory primops needed to
execute PCR memory effects. This increment proves address arithmetic and
source-level wiring for that supported operand subset, plus ADDTPC register
effects and decoding; it does not
claim PCR memory-event or fault conformance.

## Increment 2: complete scalar Reg5 operand semantics in Sail

Implement the owning
[`asl/scalar/model/types/operands.asl`](https://github.com/PTO-ISA/pto-spec/blob/f0a876e449a95d26841c5ee7affb4c905ebc5f5b/asl/scalar/model/types/operands.asl)
contract across scalar instruction families: sources 24..27 select T#1..T#4,
sources 28..31 select U#1..U#4, destinations 24..29 discard, destination 30
pushes U and destination 31 pushes T. Use the owning queue-state contract for
availability, ordering and capacity. Separate physical GPR access from Reg5
operand access, reject unavailable queue sources before any instruction effects,
and test source snapshots plus both push destinations. Replace the bounded
rejections above only when those semantics have independent execution evidence.

## Increment 3: paired LLVM/LLD and QEMU PCR repair

This remains open under [#206](https://github.com/LinxISA/linx-isa/issues/206).
The pinned LLVM `9dd03841e5758c8be7cc3d20be122413553becf1` and QEMU
`d451933b46ec7212a3e95514ee36d876d9c81f7b` still use unscaled PCR byte deltas.

- LLVM MC and LLD must convert symbolic addresses with
  `D = S + A - align_down(P, 4)`, reject `D % 4 != 0`, range-check `D / 4`, and
  retain the existing split-field packing. Explicit numeric operands remain
  encoded immediate units. Local fixups must account for final placement at
  `P % 4 == 2`; blindly dividing an existing `S + A - P` result by four is wrong.
- Update symbolic disassembly and relevant range checks. Keep dormant linker
  relaxation disabled; enabling it requires separate local-reference repair.
- QEMU must apply the same formula to all 22 paths using unsigned modular
  arithmetic. Preserve packed store-immediate reconstruction before scaling,
  original HL prefix PC, memory helpers and fault/commit behavior.
- ADDTPC's page-relative shift and branch/return halfword displacements are
  different contracts and must remain unchanged.
- Validate one independent raw corpus against Sail, QEMU and compiler output:
  both PC alignments, signed extrema, wraparound, load extension, doubleword
  alignment faults and exact saved fault TPC. Check numeric operands, local
  symbols, external relocations, addends and unrepresentable target rejection.

A distinguishing raw vector is SW.PCR with source code 1 and immediate 1:
`0x0010a069` (little-endian `69 a0 10 00`). At TPC `0x1002`, the address must be
`0x1004`; an unaligned, unscaled consumer computes `0x1003`. A symbolic target
`0x1004` at this PC must encode 1, while target `0x1006` must reject.

Land the paired consumer repairs and repin only their reviewed merged commits.
Rebuild old compiler-produced PCR binaries: an unchanged golden identity does
not make previously misencoded offsets correct. This is a consumer bug fix,
not a new ISA encoding ABI or publication.

## Increment 4: PC-state and captured-return audit

PTO's PC/TPC accessors alias one storage location, whereas staged Sail has two
registers. Validate their global mapping through jump, ACRE, trap recovery and
instruction retirement before changing one instruction's base accessor in
isolation. Also audit SETRET, HL.SETRET and C.SETRET against PTO's
`SetReturnAddress`, which uses an unsigned halfword displacement and updates
both R10 and captured return state. Test unsigned extrema, wraparound and
subsequent return behavior. These are unclosed state-model proof obligations,
not a claim that an accessor spelling alone proves an instruction defect.
Keep fused-call embedded return-base rules separate.

## Increment 5: Sail reservation and fault semantics

Two concrete Sail gaps remain relative to PTO memory and AMO semantics:

1. `state.sail` explicitly leaves ordinary stores without reservation
   invalidation. `LR.W` followed by a successful same-line `SW` must make the
   next `SC.W` fail, including same-value writes and writes to another byte in
   the same 64-byte granule. Non-overlapping and faulting writes must preserve
   the reservation. Relevant forms include `lr_w_32_efecc735bb75`,
   `sw_32_28ad317b1b41` and `sc_w_32_14b238f02bfd`.
2. `exec_sc_b/h/w/d` currently clears the reservation after the faultable store.
   PTO consumes it before the access probe, even when that access faults.
   Preserve the existing probe-free miss path.

This needs a fault-capable memory-hook regression harness, not only assertions
about source statement order. Cover faults, same-value writes, same-granule
overlap, adjacent granules, and hit/miss results independently. Saved-context
and cross-PE reservation modeling must have an explicit supported boundary;
the current single-local-monitor model cannot claim that coverage.

## Completion rule

Keep catalog equality, Sail executable subsets, compiler encoding, emulator
execution and cross-model memory/fault evidence as separate claims. Extend the
semantic audit by scalar family after these increments; do not mark all 473
forms semantically synchronized because their catalogs or decoders match.
The broader open work remains linked from
[#210](https://github.com/LinxISA/linx-isa/issues/210).
