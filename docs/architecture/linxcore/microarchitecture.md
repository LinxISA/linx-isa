# LinxCore v0.4 Microarchitecture Contract

## Baseline superscalar contract

LinxCore closure target is a superscalar out-of-order core with current structural limits captured by implementation parameters.

Current baseline limits (must be treated as architectural bring-up constraints until promoted):

- fetch width: 4
- dispatch width: 4
- issue width: up to 4
- commit width: up to 4
- LSU width: 1

These constraints are the current v0.4 closure baseline. Wider issue/commit and multi-LSU scaling are follow-on expansion tracks.

## Pipeline contract (LC-MA-PIPE-001)

- Stage ownership must be explicit (frontend/decode/rename/issue/execute/commit) with no hidden pass-through stage collapse.
- Commit behavior must remain precise and ordered by architectural retirement.
- ROB bookkeeping must remain coherent across multi-commit cycles.

## Hazard and replay contract (LC-MA-HAZ-001)

- Wakeup, scoreboard, and replay control must preserve deterministic issue legality.
- Redirect/flush/replay must not commit younger wrong-path state.
- Load-miss and replay paths must preserve correctness for dependent consumers.

## Block and recovery contract (LC-MA-BLK-001)

- Block-structured control flow is mandatory: `BSTART`/`BSTOP` semantics remain authoritative.
- Recovery targets must resolve to legal block boundaries.
- Invalid block-target recovery must be precise-trap observable.

Current LinxCore alignment details:

- architectural redirect is boundary-authoritative; execute-side `setc.cond`
  records pending correction metadata but does not directly rewrite architectural PC
- `BSTART` and `BSTOP` are ROB-visible boundary uops, and an in-body `BSTART`
  may terminate the previous block before reappearing as the next block head
- `RET`, `IND`, and `ICALL` require explicit `SETC.TGT` in the same block
- returning `BSTART.CALL` headers require adjacent `SETRET` or `C.SETRET`; there
  is no implicit `ra` rewrite on the call header itself
- `FENTRY`, `FEXIT`, `FRET.RA`, and `FRET.STK` are valid standalone macro block
  boundaries and must be treated as fall-through macro blocks in live committed
  block metadata
- dynamic correction and recovery targets must resolve to legal block starts;
  known non-block targets raise `TRAP_BRU_RECOVERY_NOT_BSTART (0x0000B001)`
- block queues and block-engine rollback remain BID-based: keep `bid <= flush_bid`,
  kill `bid > flush_bid`

## Privilege/trap contract (LC-MA-PRV-001)

- U->S trap entry and `SRET` return must preserve architected control/state transitions.
- Trap envelope and CSR side effects must be coherent with commit-visible behavior.
- Precise exception reporting is required under superscalar retirement.

## MMU contract (LC-MA-MMU-001)

- Translation success and failure (permission/page fault) must produce deterministic trap envelopes.
- MMU behavior must remain aligned with v0.4 privileged contract wording.
- MMU fault paths must preserve precise retirement and recovery ordering.

## Interrupt contract (LC-MA-IRQ-001)

- Timer interrupt delivery must be enabled in strict-system lanes (no silent global masking in closure runs).
- Interrupt entry/return must compose with block boundaries and replay/flush behavior.
- Interrupt handling must preserve forward progress under sustained mixed workload pressure.

## Memory-ordering contract (LC-MA-MEM-001)

- Load/store ordering, forwarding, and replay behavior must remain architecturally legal.
- Memory visibility at commit must remain consistent with recorded trace/memory metadata.
- Ordering checks must include block and redirect interactions.

## Forward-progress contract (LC-MA-FWD-001)

- Branch/flush/load-miss/replay/interrupt interactions must not deadlock.
- Required closure gates must include explicit forward-progress evidence lanes.

## Contract evidence mapping

| Contract ID | Primary gate evidence |
|---|---|
| `LC-MA-PIPE-001` | `LinxCore::stage/connectivity lint`, `Testbench::ROB bookkeeping` |
| `LC-MA-HAZ-001` | `LinxCore::trace schema and memory smoke`, `Testbench::ROB bookkeeping` |
| `LC-MA-BLK-001` | `LinxCore::runner protocol`, `Testbench::block struct pyc flow smoke` |
| `LC-MA-PRV-001` | `pyCircuit::QEMU vs pyCircuit trace diff`, `LinxCore::cosim smoke` |
| `LC-MA-MMU-001` | `pyCircuit::QEMU vs pyCircuit trace diff`, `LinxCore::cosim smoke` |
| `LC-MA-IRQ-001` | `LinxCore::cosim smoke`, `LinxCore::runner protocol` |
| `LC-MA-MEM-001` | `LinxCore::trace schema and memory smoke`, `pyCircuit::QEMU vs pyCircuit trace diff` |
| `LC-MA-FWD-001` | `Testbench::ROB bookkeeping`, `LinxCore::runner protocol` |

## Reference implementation detail sources

Implementation detail sources that feed this contract:

- `rtl/LinxCore/docs/architecture/linxcore_top_design.md`
- `rtl/LinxCore/docs/architecture/pipeline_stages.md`
- `rtl/LinxCore/docs/architecture/block_fabric_contract.md`
- `rtl/LinxCore/docs/architecture/branch_recovery_rules.md`
- `rtl/LinxCore/docs/architecture/lsid_memory_ordering.md`

LinxArch remains normative when wording diverges.
