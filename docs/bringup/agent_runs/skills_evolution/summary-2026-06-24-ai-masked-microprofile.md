# AI Masked Attention Micro-Profile Skill Evolution

- Generated (UTC): `2026-06-24T03:01:57Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `96e14169867e50d1f58f438a5d513d4b231414f5`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-flash-attention-masked` is now a proven
QEMU-to-LinxCoreModel masked-attention prefix micro-profile. The runner selects
the previously proven 1x attention flags and adds:

```text
PTO_ATTENTION_MASKED_SMOKE_SEQ=1
PTO_ATTENTION_MASKED_SMOKE_QD=1
PTO_ATTENTION_MASKED_SMOKE_VD=1
PTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION_MASKED
```

The reusable boundary is that this case proves the stage prefix through the
`flash_attention_masked` digest and plain `tools/LinxCoreModel/bin/gfsim -f
<elf>`, while the full smoke-sized `avs-pto-parity` row remains the maturity
target.

## Evidence

- Targeted run: `ai-pr-parity-prefix-flash-attention-masked-1x-01`, 1 selected, 1 final model green.
- Dry-run contract: `ai-pr-parity-prefix-flash-attention-masked-1x-dry`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation: `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Skill validation: `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the
  model-green masked-attention prefix micro-profile rule.
