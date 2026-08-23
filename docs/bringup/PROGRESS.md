# Bring-up Progress (v0.58.3)

Last updated: 2026-08-23

## Current architecture baseline

- `isa/v0.58/linxisa-v0.58.json` is the canonical LinxISA catalog: 723
  mnemonics and 757 legal forms.
- `isa/v0.58/pto-spec.lock.json` pins published PTO ISA v0.58.3 commit
  `e599a3d36ebfad43362ff591ea5e128816c684c7` and encoding projection
  `8a48b80e04484c70870f155bf9efc79d2a805cf99e809f4e4e8a7e6a7eb34172`.
- The semantic engines are `VEC`, `SFU`, `TLSU`, and `CUBE`; TEPL remains the
  Mode/Function encoding carrier for VEC/SFU and is not an engine.
- `docs/bringup/component-lock.v0.58.json` and the affected gitlinks pin the
  final merged v0.58.3 leaf SHAs atomically.

## Evidence policy

Only evidence produced from the final v0.58.3 component lock can be promoted.
Historical v0.57/v0.58.1 reports, stale SHAs, trace-only output, pending jobs,
skips, and missing-tool results are not passes. Generated status pages are
views; machine-readable locks and fresh run summaries take precedence.

## Current checked-in status

| Surface | Status | Current evidence |
| --- | --- | --- |
| ISA catalog, Sail, and PTO lock | Verified | Golden/catalog/manifest checks; Sail parser, directed semantics, coverage, and C backend; 723/757 authority |
| LLVM/LLD | Merged | `b7c83f68bf84125e696a70bec4b665c70a3b584d`; MC 55/55; compile AVS linx32 759/759 and linx64 723/723; fresh pure-CodeGen breadth 146/723 with aliases |
| QEMU | Merged leaf | `0d2f90de253ab6ccdaddf405da1bda7c3908dcf7`; reviewed HL.LUI/LIU/LIS trace metadata, CSEL, CUBE, and ACR2 TLSU CPU-MMU gates pass |
| Linx-TileOP-API | Merged leaf | `bd1ecca97ca47da0edc462c1ce19749c6940780e`; compute PadValue Zero and transport Null contracts pass |
| PTOAS | Merged | `cbfaefe6d3a42b6cb3de1482ef01663630d4b39e`; exact PTO/TileOP pins, source review, local gates, and all six applicable hosted wheel jobs pass |
| Linux, glibc, and musl | Merged leafs | Exact PTO identity and clean final-LLVM `vmlinux` build pass; full-system PTO workload is still a release gate |
| VECTOR/CUBE first use | Architecture complete; Linux disabled | ISA/Sail/QEMU pre-effect trap contract passes. Linux keeps V/C disabled until the cross-ACR EXTCTX ABI is specified in root issue 182 and Linux issue 32 |
| Queue-wired model and PTO kernels | Merged and repinned | Model `bf9d73cf`; pto-kernels `5f5cf061`; final HL.LUI/LIU/LIS semantics, model CTest 12/12, and six CUBE programs compile/link with exact identity |
| Full-system PTO CUBE | Verified cold-boot matrix | Six independent Linux/QEMU boots pass 6/6 with one exact component fingerprint; aggregate SHA-256 `3328caf983ae9f555b926b818d89795fb8e13650bd13a9ce0c925a6b8a29761a` |
| Broader nightly benchmarks | Open | Nightly breadth remains separate from the release-strict result and identity gates |

## Canonical commands

```bash
bash tools/ci/check_repo_layout.sh
python3 tools/ci/check_component_lock.py --root .
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/check_pto_v058_manifest.py --root .
python3 tools/isa/check_canonical_v058.py --root .
python3 tools/isa/check_agent_navigation.py --root .
python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend
make -C tools/Linx-TileOP-API check
python3 workloads/pto_kernels/scripts/check_supernpu_v058.py
python3 docs/check_documentation.py --root .
```

The final release additionally requires the exact PTO CUBE full-system gate,
fresh model/cross-stack evidence, green hosted checks on the final root head,
and equality between reviewed and merged trees.

The six-child sequential diagnostic is intentionally not a release pass: it
reproduces cross-process Tile context leakage while Linux keeps first-use
context management disabled. Cold-boot per-case evidence proves each maintained
program end to end; cross-process reuse remains tracked by root issue 182 and
Linux issue 32.
