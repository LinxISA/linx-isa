# AVS Compatibility Contract (v0.57)

`avs/linx_avs_v1_test_matrix.yaml` remains the public `v0.57` compatibility
matrix. It is regression evidence for the hard-break upgrade, not normative
evidence that LLVM, QEMU, Linux, or the other consumers implement `v0.58`.
Fresh `v0.58` AVS evidence must be produced as each downstream consumer is
upgraded; historical `v0.57` PASS results do not transfer.

## Canonical Files

- Matrix: `avs/linx_avs_v1_test_matrix.yaml`
- Status: `avs/linx_avs_v1_test_matrix_status.json`
- Current architecture authority: `isa/v0.58/linxisa-v0.58.json`
- Current architecture explanation: `docs/architecture/v0.58-architecture-contract.md`

## Required Entry Metadata

Every AVS entry in the canonical matrix carries:

- `state`: `active` or `archived`
- `profiles`: architecture or subsystem coverage buckets
- `must_pass_in_tier`: gate tiers such as `pr` and `nightly`
- `spec_refs`: the `v0.57` compatibility requirement covered by that matrix entry
- `requirement` and `pass_fail`: normative closure statements

Only `state: active` entries participate in tier closure.

## Contract Gates

Validate the matrix schema and references:

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
```

Generate and validate the canonical derived status artifact:

```bash
python3 tools/bringup/gen_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --source-status avs/linx_avs_v1_test_matrix_status.json --out avs/linx_avs_v1_test_matrix_status.json
python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json
```

Require tier closure for all active entries:

```bash
python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr
```

## Current Scope

The canonical AVS matrix now covers:

- scalar and vector ISA legality
- Tile and TEPL behavior using the v0.57 compatibility vocabulary
- Linux boot and runtime gates
- musl and glibc gates
- maintained workload runners
- SPEC stage gates

The matrix is the public compatibility contract for the previous profile. It
does not supersede `isa/v0.58/linxisa-v0.58.json` and cannot close a `v0.58`
consumer upgrade without fresh evidence.
