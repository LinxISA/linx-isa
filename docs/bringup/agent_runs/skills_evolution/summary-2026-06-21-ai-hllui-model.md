# Skill Evolution Summary: AI HL Immediate Model Contract

- Generated (UTC): `2026-06-21T19:31:53Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `07d3ed013eaa054343ef54bd14ea191984829ca2`

## Touched Skills

- `linx-model`: added the reusable QEMU-pass/model-divergence triage rule for
  `HL.LUI`, `HL.LIS`, and `HL.LIU` immediate materialization.
- `linx-superproject`: updated the AI workload PTO promotion list so
  `pto-kernel-argmax_fp32` and `pto-kernel-unique_i32` are no longer stale
  model-lane maturity packets.

## Rationale

`pto-kernel-argmax_fp32` passed QEMU but previously timed out in
`tools/LinxCoreModel/bin/gfsim` because the model treated the 48-bit `LUI`
form as high-half materialization. Sail and QEMU define `HL.LUI` and `HL.LIS`
as sign-extending the decoded 32-bit immediate, while `HL.LIU` zero-extends it.
This contract is reusable for future scalar loop-divergence triage.

## Validation

- `python3 /Users/zhoubot/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/zhoubot/linx-isa/skills/linx-skills/linx-model`
- `python3 /Users/zhoubot/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/zhoubot/linx-isa/skills/linx-skills/linx-superproject`
- `python3 /Users/zhoubot/linx-isa/skills/linx-skills/scripts/check_skill_change_scope.py --repo-root /Users/zhoubot/linx-isa/skills/linx-skills --base origin/main`
- `bash /Users/zhoubot/linx-isa/skills/linx-skills/scripts/install_canonical_skills.sh`

## Closeout

- `skill-evolve: update linx-model, linx-superproject (HL immediate model contract and AI PTO promotion status)`
