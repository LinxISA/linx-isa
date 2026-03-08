# AVS Contract (v0.4)

`avs/linx_avs_v1_test_matrix.yaml` is the only live public bring-up contract for LinxISA `v0.4`.

## Canonical Files

- Matrix: `avs/linx_avs_v1_test_matrix.yaml`
- Status: `avs/linx_avs_v1_test_matrix_status.json`
- Architecture contract: `docs/architecture/v0.4-architecture-contract.md`

## Required Entry Metadata

Every AVS entry in the canonical matrix carries:

- `state`: `active` or `archived`
- `profiles`: architecture or subsystem coverage buckets
- `must_pass_in_tier`: gate tiers such as `pr` and `nightly`
- `spec_refs`: canonical `v0.4` spec, manual, or state references
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
- tile and TEPL behavior
- Linux boot and runtime gates
- musl and glibc gates
- maintained workload runners
- SPEC stage gates

The matrix is the public contract. Historical numeric contract materials are removed from active navigation and do not participate in closure.
