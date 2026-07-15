# AI Softmax Micro-Profile Skill Evolution

- Generated (UTC): `2026-06-24T02:40:52Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `1679840406ab3510f8a4593ff201b3633a6747d5`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-flash-attention-softmax` is now a proven
QEMU-to-LinxCoreModel softmax-prefix micro-profile. The runner selects opt-in
attention shape flags:

```text
PTO_ATTENTION_SMOKE_SEQ=1
PTO_ATTENTION_LARGE_SMOKE_SEQ=1
PTO_ATTENTION_SMOKE_QD=1
PTO_ATTENTION_SMOKE_VD=1
PTO_ATTENTION_SMALL_SMOKE_QD=1
PTO_FLASH_TILE_M=1
PTO_FLASH_TILE_K=1
```

The reusable boundary is that this case proves the stage prefix through the
`flash_attention_softmax` digest and plain `tools/LinxCoreModel/bin/gfsim -f
<elf>`, while the full smoke-sized `avs-pto-parity` row remains the maturity
target.

## Evidence

- Targeted run: `ai-pr-parity-prefix-flash-attention-softmax-1x-01`, 1 selected, 1 final model green.
- Dry-run contract: `ai-pr-parity-prefix-flash-attention-softmax-1x-dry`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation: `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Skill validation: `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the optimized
  `gfsim` build contract and the model-green softmax micro-profile rule.
