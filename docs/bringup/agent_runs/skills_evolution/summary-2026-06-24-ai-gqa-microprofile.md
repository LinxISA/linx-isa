# AI GQA Micro-Profile Skill Evolution

- Generated (UTC): `2026-06-24T06:28:22Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `acd8022bdd89ad9ec06de33ff6fc0c9c65c9d420`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-gqa` is now a proven QEMU-to-LinxCoreModel prefix
micro-profile after `flash_attention_vec`. The case stops after
`PTO_PARITY_STAGE_GQA` and aligns the AVS arrays with the PTO kernel smoke shape
using:

```text
PTO_PARITY_GQA_SEQ=1
PTO_PARITY_GQA_Q_HEADS=1
PTO_PARITY_GQA_KV_HEADS=1
PTO_PARITY_GQA_DIM=1
PTO_GQA_SMOKE_SEQ=1
PTO_GQA_SMOKE_Q_HEADS=1
PTO_GQA_SMOKE_KV_HEADS=1
PTO_GQA_SMOKE_DIM=1
```

The reusable boundary is that this case proves the stage prefix through the
`gqa` digest under plain `tools/LinxCoreModel/bin/gfsim -f <elf>`. The full
smoke-sized `avs-pto-parity` row remains the sparse/full-shape maturity target.

## Evidence

- Run: `ai-pr-parity-prefix-gqa-1x-01`, 1 selected, 1 final model green.
- Digest: `PTO_DIGEST gqa 0x99D39E00C4C9CE38`.
- Dry-run contract: `ai-pr-parity-prefix-gqa-1x-dry-01`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation: `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Layout validation: `bash tools/ci/check_repo_layout.sh`.
- Skill validation: `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the
  model-green GQA prefix micro-profile rules.
