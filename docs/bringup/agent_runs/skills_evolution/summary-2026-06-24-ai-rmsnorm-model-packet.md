# AI RMSNorm Model Packet Skill Evolution

- Generated (UTC): `2026-06-24T08:40:34Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `69e61028ffbe2b4751b41468f33a27a178d9cb03`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-rmsnorm` is now an explicit hard-break case after
`sparse_attention_local`. The case stops after `PTO_PARITY_STAGE_RMSNORM` and
aligns the AVS parity arrays with the PTO RMSNorm smoke shape using:

```text
PTO_PARITY_RMS_TOKENS=1
PTO_PARITY_RMS_CHANNELS=1
PTO_RMSNORM_SMOKE_TOKENS=1
PTO_RMSNORM_SMOKE_CHANNELS=1
```

The reusable boundary is not model-green promotion. Current evidence proves
source, compiler, and QEMU, then emits a model-owned timeout packet for
LinxCoreModel. Keep this case in the model lane until plain
`tools/LinxCoreModel/bin/gfsim -f <elf>` exits naturally or newer static
legality evidence changes ownership.

## Evidence

- Run: `ai-pr-parity-prefix-rmsnorm-1x-01`, 1 selected, 0 final model green.
- QEMU: PASS after source and compiler contracts.
- Model: timeout under plain `gfsim -f <elf>`.
- Latest BROB head: `B219 STID0 BPC 0x11dfe [STD COND]`.
- Disassembly window:
  `workloads/generated/ai-pr-parity-prefix-rmsnorm-1x-01/ai-bringup/cases/avs-pto-parity-prefix-rmsnorm/model/last-bpc-0x11dfe.disasm.txt`.
- Fix packet:
  `workloads/generated/ai-pr-parity-prefix-rmsnorm-1x-01/ai-bringup/fix-packets/avs-pto-parity-prefix-rmsnorm.json`.
- Dry-run contract: `ai-pr-parity-prefix-rmsnorm-1x-dry-final`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation:
  `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Skill validation:
  `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`;
  `quick_validate.py linx-model`;
  `quick_validate.py linx-superproject`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the
  QEMU-passing, model-owned RMSNorm parity prefix packet.
