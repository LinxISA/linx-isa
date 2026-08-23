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
- `docs/bringup/component-lock.v0.58.json` remains a release blocker until it
  and every affected gitlink are atomically updated to final merged leaf SHAs.

## Evidence policy

Only evidence produced from the final v0.58.3 component lock can be promoted.
Historical v0.57/v0.58.1 reports, stale SHAs, trace-only output, pending jobs,
skips, and missing-tool results are not passes. Generated status pages are
views; machine-readable locks and fresh run summaries take precedence.

## Current checked-in status

| Surface | Status | Current evidence |
| --- | --- | --- |
| ISA catalog, Sail, and PTO lock | Verified | Golden/catalog/manifest checks; Sail parser, directed semantics, coverage, and C backend; 723/757 authority |
| LLVM/LLD | Merged | `b7c83f68bf84125e696a70bec4b665c70a3b584d`; MC 55/55; compile AVS linx32 759/759 and linx64 723/723 |
| QEMU | Integration in progress | PTO v0.58.3 base plus reviewed HL.LUI and CSEL fixes are merged; TLSU CPU-MMU PR and CUBE issue 75 remain before the final pin |
| Linx-TileOP-API | Integration in progress | Exact API/link gates pass; PR 27 corrects CUBE compute PadValue to the PTO-required Zero value |
| PTOAS | Integration in progress | PR 8 source review and local gates pass; final TileOP pin and hosted delivery jobs must be refreshed before merge |
| Linux, glibc, and musl | Merged leafs | Exact PTO identity and clean final-LLVM `vmlinux` build pass; full-system PTO workload is still a release gate |
| VECTOR/CUBE first use | Architecture complete; Linux disabled | ISA/Sail/QEMU pre-effect trap contract passes. Linux keeps V/C disabled until the cross-ACR EXTCTX ABI is specified in root issue 182 and Linux issue 32 |
| Queue-wired model and PTO kernels | Merged leafs, root repin pending | Model `eee8fd57`; pto-kernels `322443ef`; six CUBE programs compile/link with exact identity |
| Full-system PTO CUBE | In progress | r8 reaches PID1, fork/exec, three TLOAD sources, and legal CUBE preflight; QEMU issue 75 owns the next compute/publish divergence |
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
