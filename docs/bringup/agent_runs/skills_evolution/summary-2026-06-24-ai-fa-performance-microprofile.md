# AI FA Performance Micro-Profile Skill Evolution

- Generated (UTC): `2026-06-24T03:21:47Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `0296c46c92d0967089d52554664b2c95368b1fc1`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-fa-performance` is now a proven
QEMU-to-LinxCoreModel prefix micro-profile after masked attention. The case
reuses the 1x attention and masked-attention shape flags, then stops at:

```text
PTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FA_PERFORMANCE
```

The reusable boundary is that this case proves the stage prefix through the
`fa_performance` digest and plain `tools/LinxCoreModel/bin/gfsim -f <elf>`.
The full smoke-sized `avs-pto-parity` row remains the maturity target.

## Evidence

- Targeted run: `ai-pr-parity-prefix-fa-performance-1x-01`, 1 selected, 1 final model green.
- Dry-run contract: `ai-pr-parity-prefix-fa-performance-1x-dry`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation: `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Skill validation: `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the
  model-green `fa_performance` prefix micro-profile rule.
