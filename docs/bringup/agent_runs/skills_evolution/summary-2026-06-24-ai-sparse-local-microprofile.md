# AI Sparse Local Attention Micro-Profile Skill Evolution

- Generated (UTC): `2026-06-24T06:54:43Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `744de93e2bda7bde668eb6d0edff0ef422a29a42`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-sparse-attention-local` is now a proven
QEMU-to-LinxCoreModel prefix micro-profile after GQA. The case stops after
`PTO_PARITY_STAGE_SPARSE_ATTENTION_LOCAL` and aligns the AVS arrays with the PTO
kernel smoke shape using:

```text
PTO_PARITY_SPARSE_SEQ=1
PTO_PARITY_SPARSE_HEADS=1
PTO_PARITY_SPARSE_DIM=1
PTO_PARITY_SPARSE_WINDOW=1
PTO_SPARSE_LOCAL_SMOKE_SEQ=1
PTO_SPARSE_LOCAL_SMOKE_DIM=1
```

The reusable boundary is that this case proves the stage prefix through the
`sparse_attention_local` digest under plain
`tools/LinxCoreModel/bin/gfsim -f <elf>`. The full smoke-sized
`avs-pto-parity` row remains the normalization and full-shape maturity target.

## Evidence

- Run: `ai-pr-parity-prefix-sparse-local-1x-01`, 1 selected, 1 final model green.
- Digest: `PTO_DIGEST sparse_attention_local 0x9A43A000C528D955`.
- Dry-run contract: `ai-pr-parity-prefix-sparse-local-1x-dry-01`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation: `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Layout validation: `bash tools/ci/check_repo_layout.sh`.
- Skill validation: `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the
  model-green sparse local attention prefix micro-profile rules.
