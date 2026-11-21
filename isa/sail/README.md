# LinxISA Sail Model (v0.58)

This directory contains the active **Sail** formal and executable model for the canonical LinxISA `v0.58` profile.

The modeled base-register addresses `0x0050` and `0x0051` expose the read-only
`BLOCKNUM` and `BLOCKID` ambient values. Block instructions continue to own
the internal dimensions and loop counters. The directed suite exercises
short and long SSR reads, illegal writes and swaps, and reserved-address faults.
The [PTO 0.59.1 adoption candidate](../../docs/architecture/v0.59.1-pto-alignment.md)
records the separate execution work for scoped Scalar and HSCB dispatch.

The generated `decode_pto_scoped_scalar` accepts a 64-bit word packed in
instruction-stream order and resolves the carrier to its locked inner Scalar
form. Directed tests check all 705 published witnesses and rejection of reserved
prefix fields, padding, excluded operations, and invalid operand encodings.
The scoped AGU candidate executes compressed, immediate, PC-relative and
register-offset loads and stores, including pre-index and post-index
writeback. `prepare_scoped_scalar` captures the outer TPC and operands.
Once GM allows the access, `issue_scoped_scalar` gives the platform a request
with the captured scope, context and token. `complete_scoped_scalar` applies
the backend result. A completed access retires eight bytes. Faults keep the
original TPC, and a blocked request can be reissued with the same operands and
token. The platform supplies applicability, holds the issuing context, and
owns memory translation, the GM obligation and store commit. Each issuance
requires one completion from the platform.

Base writeback is published only after memory completion. For paired accesses,
the memory request also carries the second address and data. The backend
checks both accesses before either effect and completes the pair together
through `complete_scoped_scalar_pair`, including which access faulted. Sail
publishes load destinations only after successful pair completion. Scoped
LR/SC, CAS and RMW forms use the same one-outstanding platform protocol with
an atomic transaction descriptor. It contains the operation, width, order,
far attribute, captured
operands, scope, Core and agent identity. The backend owns the indivisible
transaction and reservation monitor. A committed SC returns status zero or
one, while LR, CAS and result-producing RMW forms publish the PTO-normalized
old value. An atomic fault publishes no register result. The candidate entry
point is explicit while the v0.58 decode path is canonical.

The platform loads the architectural T/U queues for its selected Core, agent,
invocation and ACR with `bind_scoped_scalar_queues` and can read the resulting
data and validity from `scoped_t_queue` and `scoped_u_queue`. Queue context
changes require an idle request boundary. Sources with no captured value raise
Illegal Instruction. Successful Reg5 `->t` and `->u` destinations push their
respective queues. Compressed loads use `->t` and compressed stores read `T#1`.
The platform owns queue synchronization with its other instruction paths and
context transitions.

The MSGB transport models the released two-Core reference topology. Its
receive, admission, BSE and HSCB APIs operate on platform-configured endpoints
and active invocations. Directed tests cover claim/read/ACK/release, atomic
delivery, occurrence replay, drain, READY/LAUNCH/DONE, and identity exhaustion.
With a bound platform context, the encoded SSR paths configure and access
MSGB banks, BSE submits the staged payload, and BWE observes readiness.
Disabled BSE and BWE publish the architectural SendEvent and WaitEvent requests
with their exact source operands and request epochs.
Encoded SSRGET exposes per-worker launch geometry until matching DONE.
The instruction entry reads live ACR and TPC. Platform integration supplies
Core, PE, thread slot, invocation, execution domain, bundle attributes, and GM
admission evidence. It consumes the blocked flag before instruction retirement
and manages the lifetime of the bank and selector state.

Scope policy:

- The Sail model is an executable reference for `v0.58` semantics and legality checks.
- The v0.58 surface is built on the retained executable subset; new v0.58 forms are explicit deltas in `semantics_policy.json`.
- `toolchain.json` pins the required OCaml and Sail versions.
- Semantic readiness is graded by stable instruction form ID in `semantics_status.json`.
- Coverage is tracked as data in `isa/sail/coverage.json`.

## Coverage report

`isa/sail/coverage.json` is generated from:

- the compiled ISA catalog: `isa/v0.58/linxisa-v0.58.json`
- the generated form status map: `isa/sail/semantics_status.json`

Regenerate:

```bash
python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend
python3 tools/isa/gen_sail_status.py --check
python3 tools/isa/sail_coverage.py --spec isa/v0.58/linxisa-v0.58.json --check
```

## Layout

- `isa/sail/model/linxisa.sail`: top-level canonical Sail entry
- `isa/sail/model/linxisa.sail_project`: project wrapper pointing at the canonical entry
- `isa/sail/model/lib/`: shared helpers
- `isa/sail/model/state/`: architectural state definitions
- `isa/sail/model/decode/`: decode model
- `isa/sail/model/execute/`: per-unit execute semantics
- `isa/sail/tests/directed.sail`: executable block/return/trap/atomic/FP edge checks
- `isa/sail/semantics_status.json`: machine-readable semantic readiness status
- `isa/sail/semantics_policy.json`: default grade and explicit form-ID overrides
- `isa/sail/toolchain.json`: hermetic Sail/OCaml version pin
