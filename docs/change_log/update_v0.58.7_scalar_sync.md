# PTO golden synchronization

PTO-SPEC is the sole authority. The active design consumes development golden
`f0a876e449a95d26841c5ee7affb4c905ebc5f5b`, not a mixture of the old published
commands and a downstream scalar amendment. The golden includes 473 scalar
forms, 105 command forms, 119 Tile operations, and 50 encoding reservations.

`tools/isa/import_pto_golden.py` verifies exact commit/tree and upstream file
bytes, then projects all common catalogs. `check_pto_scalar_proposal.py` checks
full scalar/command/Tile/reservation equality and the active encoding identity.
The historical filenames remain entry points; no independent scalar amendment
source remains. `gen_pto_binder_pages.py` generates English/Chinese B.IOT and
B.IOS references from the pinned PTO owning ASL contract, including independent
.reuse/last-use semantics.

The current development ELF identity has release `0.58.7`, ABI
`pto-isa-0.58.7-mode-function-v1`, and encoding projection
`a5f78ecd707bde4a014542158ea257c783796b95fa4fbcce37742e41fee6a881`.
It is not the published 0.58.7.0 identity; old objects must reject. The immutable
publication lock and its frozen 466/96/118 inventory remain historical evidence.

## Downstream work

- [PTO-SPEC #390](https://github.com/PTO-ISA/pto-spec/pull/390) owns scalar
  definitions, development identity, and source traceability.
- [QEMU #82](https://github.com/LinxISA/qemu/pull/82) synchronizes scalar
  masks, rejects removed fused32 CALL, checks frame legality before effects,
  and rejects unsupported resource/header/synchronization forms.
- [PTOAS #9](https://github.com/LinxISA/PTOAS/pull/9) pins the same golden and
  rejects retired names through shared verification. Name presence is not
  semantic conformance: 94 names are present, 25 golden operations are absent,
  and 87 retained operation catalogs changed since its previous source.
- [LLVM #126](https://github.com/LinxISA/llvm-project/pull/126) imports the
  derived codecs, authenticates the development manifest, and emits explicit
  `.reuse` for every generated B.IOT source until runtimes advertise last-use
  support. Manual assembly retains independent per-source lifetime choices.
- [linx-model #22](https://github.com/LinxISA/linx-model/pull/22) imports the
  exact derived catalog, repairs Reg5 destinations and the S0..S63 bank, and
  rejects unsupported instructions before PC/count/retirement effects.
- [TileOP API #279](https://github.com/LinxISA/Linx-TileOP-API/pull/279) pins
  the same golden, preserves sources with explicit `.reuse`, uses canonical
  TLSU/CUBE headers, and closes retired raw-selector wrapper paths.

## Cross-repository verification

The semantic source is the immutable PTO commit above. PTO PR #390 subsequently
repairs generated traceability and check metadata; those repairs do not change
the golden ASL, catalogs, or development manifest. The Linx design projection
used by leaf locks is `f77a8960f61f97c264a90b7aee757f99891b0943`; later documentation
and gate changes preserve its catalog bytes. Its catalog SHA-256 is
`51ca9be275518d29ec48bed570b7a9bd441a65b9c5e6d4f79072f650ee732925`.

| Consumer / evidence | Proven scope | Remaining boundary |
| --- | --- | --- |
| PTO-SPEC #390, `b00cad7f2ba10d9719dffd59798bff3719ad52d2` | Full `make pr-check`: 12 checks and 872 Python tests pass; hosted source-contract/tooling/validate pass | Development candidate, not a new publication |
| LinxISA direct import and parity checks | Exact scalar, command, Tile, reservation and development identity equality | Equality does not prove execution of all forms |
| LLVM #126, `edb65a7681de90874d0c1fe4e6098f9e55ff8a00` | 59 MC tests and linx32/64 IAS checks pass; all 79 VEC/SFU names, selectors and engines match golden; retired named/raw forms reject | Full CodeGen has 6 failures and 1 unresolved; baseline status is unclassified; hosted builds were skipped |
| QEMU #82, `4059c3eba0fc08b8a0382d16555dcb493e8172f6` | All 473 scalar decoder signatures agree; 121 Python tests, build, metadata audit and directed runtime groups pass in the recorded runs | High-count repeated launches still show rare TLOAD/TSTORE guest-fail exits; runtime promotion remains blocked |
| PTOAS #9, `1c72da5bfd50db3caa327e24ede5ea87af31e56c` | Golden identity/catalog authority and rejection of 15 retired operations | 94 names present, 25 absent; 87 retained catalog entries changed and have no complete semantic/schema parity proof |
| linx-model #22, `ba8f660749c944406e8e7e5bfcb76af506ff3d4b` | 12 CTest checks and applicable hosted CI pass | Execution is an explicit partial subset of its 794 decoded forms |
| TileOP API #279, `1d93a62cba5c39ed17ad63df142097b73f7dfbeb` | `make check`, exact golden generation, 60 engine-contract tests and MC/IAS checks pass; independent binding-string audit preserves masks/destinations/L | 118 source-referenced names, TLEA has no wrapper; exact candidate target C++ object validation lacks a local musl sysroot |

The final LLVM/API assembly oracle accepts all 119 golden block headers in
standalone MC and linx32/linx64 Clang IAS. LLVM now rejects the nine stale named
VEC/SFU aliases and their raw TEPL selectors. This rejection does not remove the
separate active TIMG2COL command. API checks also reject the retired
`TCONCAT_ASS` and `TTRANS_ASS` raw-emission paths.

The full LLVM CodeGen failures are `autovec_inner_mask_branch`,
`autovec_matmul_requires_cube`, `autovec_nested_mask_branch`,
`autovec_tsvc_control_flow`, `autovec_tsvc_extra`, and `codesize-balance-hlimm`;
the nested-mask assembly companion is unresolved. No matching baseline binary
was available, so these failures must not be labeled pre-existing.

QEMU's memory review repaired 64-byte LR/SC granules, natural-alignment priority,
probe-free SC misses, permission preflight, fault-preserving reservations,
successful-write invalidation across the four PEs, and overlapping DMA snapshot
semantics. Faultable writers enter QEMU's exception-safe exclusive replay before
effects. Exported helpers capture the actual TCG return address and pass it to
nested alignment, probe and replay paths. The LR.W/SW.ADD/SC.W fault tests check
the exact saved TPC, return to that same instruction after repairing its operand,
and detect duplicate RMW effects or a write from an SC monitor miss. FEXIT and
FRET.RA tests also check the saved TPC and successful same-template retry.
Process exit codes are checked explicitly; a forced-failure kind-5 guest returns
nonzero as expected, and fault kinds 2 through 8 each report a separate PASS.
Tile GM accesses likewise carry the real commit-helper return address. The
focused MMU runner disables asynchronous timer IRQs and isolates the faulting
TLOAD/TSTORE cases from unrelated warmup; synchronous fault assertions remain
active. The final evidence includes 20 consecutive MMU runs and five concurrent
MMU/reservation/Core4/fused-call rounds, all with zero exit status. Independent
review and a separate integration-owner rerun passed on the recorded head.
Subsequent higher-count process-launch stress nevertheless produced rare
TLOAD/TSTORE guest-fail exits. Their cause is not proven closed. An attempted
`-icount` runner change also failed to eliminate them and was reverted; it is
not part of the recorded commit. The passing bounded runs and source review do
not establish a flake-free MMU/Tile runtime. This unresolved result remains a
promotion blocker, alongside the separate LLVM and API validation gaps.

Run the common-source checks from the integration checkout, substituting exact
candidate checkout paths:

```sh
python3 tools/isa/import_pto_golden.py --source-root "$PTO_GOLDEN_ROOT" --check
python3 tools/isa/check_pto_scalar_proposal.py --pto-root "$PTO_GOLDEN_ROOT"
python3 tools/isa/check_qemu_scalar_golden.py --qemu-root "$QEMU_CANDIDATE_ROOT"
```

Hosted LinxISA run `39022007627` passes docs, lint and AVS contract checks.
Its guards job rejects the older pinned QEMU scalar decoder; its model job
rejects the older pinned model's release/catalog identity. These are visible
integration dependencies, not passing candidate-leaf evidence. Updating the
gitlinks requires the reviewed, merged leaf revisions.

The TileOP API audit uses the actual integration pin
`bd1ecca97ca47da0edc462c1ce19749c6940780e`, not the unrelated dirty primary
checkout. That pin contains 932 source-bearing B.IOT/B.IOS string occurrences
without explicit `.reuse`, and its engine contract still identifies the old
109-operation source. These are textual emitter occurrences, not instruction
coverage counts. Since LLVM now implements omission as last-use, the old text
changes its encoded lifetime behavior when assembled by the new toolchain.
The API synchronization therefore requires explicit per-source `.reuse`,
golden-compatible block headers, refreshed source locks and generated engine
documentation, and actual assembly checks. Destination bindings and the
independent sequence-ending L marker retain their meaning.

The API repair is based on its current `linx` branch at `315f397`, preserving
changes landed after the older integration pin. Its two inline-assembly headers
contain 1,638 source-bearing binder emissions, all with explicit reuse. Removing
only the added `.reuse` text produces exactly the original binding-string
multisets, so destination bindings, masks and L markers are preserved.

API hosted run `39025860551` was still building at the final local audit. That
workflow resolves LLVM branch `dev-llvm15_56`, while companion LLVM #126 targets
`main`; even a successful hosted run would not establish target C++ object
compatibility with the exact `edb65a7` candidate. The local MC/IAS evidence uses
that exact candidate. The sysroot-backed C++ lane remains an explicit promotion
dependency.

## Implementation boundaries

DMA.FREE.S/L and MCOPY.DS/DL are encoding-only, NOT IMPLEMENTED, in both golden
and consumers. No successful no-op, identity address, or resource behavior is
invented. New binder lifetime modes, nonzero ExecutionMask controls, and
SYNC.CORE are decoded but explicitly unsupported in the staged Sail/QEMU
subsets. This does not narrow the PTO architecture or claim full conformance.

Leaf revisions are promoted to superproject gitlinks only after their own
review and gates; old default pins remain a visible integration dependency.

Skill closeout: `skill-evolve: no-update` for installed skills in this task.
This development candidate does not publish a new stable skill authority.
Historical counts in installed skills (including the old 109-operation map)
must not override the exact PTO golden and its 119-operation development
catalog used here.
