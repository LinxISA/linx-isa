# AI MLA Attention Micro-Profile Skill Evolution

- Generated (UTC): `2026-06-24T03:42:56Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `e6ac2aa437633170fc21fba434301d8ecbbd2f50`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-mla-attention` is now a proven
QEMU-to-LinxCoreModel prefix micro-profile after `fa_performance`. The case
reuses the 1x attention and masked-attention shape flags, then stops at:

```text
PTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_MLA_ATTENTION
```

The reusable boundary is that this case proves the stage prefix through the
`mla_attention` digest and plain `tools/LinxCoreModel/bin/gfsim -f <elf>`.
The full smoke-sized `avs-pto-parity` row remains the maturity target.

## Evidence

- Targeted run: `ai-pr-parity-prefix-mla-attention-1x-01`, 1 selected, 1 final model green.
- Model digest: `PTO_DIGEST mla_attention 0x13A77E60D8016A81`.
- Dry-run contract: `ai-pr-parity-prefix-mla-attention-1x-dry-01`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation: `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Skill validation: `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the
  model-green `mla_attention` prefix micro-profile rule.
