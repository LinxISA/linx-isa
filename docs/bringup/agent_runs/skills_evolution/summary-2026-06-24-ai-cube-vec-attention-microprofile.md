# AI Cube And Vector Attention Micro-Profile Skill Evolution

- Generated (UTC): `2026-06-24T06:06:25Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `d776524a435dd053ce8cbdb862de788f4c1198b3`
- Updated skills: `linx-model`, `linx-superproject`

## Reason

`avs-pto-parity-prefix-flash-attention-cube` and
`avs-pto-parity-prefix-flash-attention-vec` are now proven
QEMU-to-LinxCoreModel prefix micro-profiles after `mla_attention`. The cube case
adds the 1x cube controls:

```text
PTO_PARITY_FLASH_CUBE_SEQ=1
PTO_PARITY_FLASH_CUBE_MAX_SEQ=1
PTO_PARITY_FLASH_CUBE_DIM=1
PTO_FLASH_CUBE_TILE_M=1
PTO_FLASH_CUBE_TILE_K=1
PTO_FLASH_CUBE_YDIM=1
```

The vector case reuses those controls and adds:

```text
PTO_FLASH_VEC_TILE_M=1
PTO_FLASH_VEC_TILE_K=1
PTO_FLASH_VEC_YDIM=1
```

The reusable boundary is that these cases prove the stage prefix through the
`flash_attention_cube` and `flash_attention_vec` digests under plain
`tools/LinxCoreModel/bin/gfsim -f <elf>`. The full smoke-sized
`avs-pto-parity` row remains the maturity target; GQA is the next unpromoted
attention boundary.

## Evidence

- Cube run: `ai-pr-parity-prefix-flash-attention-cube-1x-01`, 1 selected, 1 final model green.
- Cube digest: `PTO_DIGEST flash_attention_cube 0x98BCA600C3DC89F2`.
- Vec run: `ai-pr-parity-prefix-flash-attention-vec-1x-01`, 1 selected, 1 final model green.
- Vec digest: `PTO_DIGEST flash_attention_vec 0x420FC9FD14BA78FB`.
- Dry-run contract: `ai-pr-parity-prefix-cube-vec-1x-dry-final`.
- Runner validation: `python3 -m py_compile tools/bringup/run_ai_workload_flow.py`.
- Flow schema validation: `python3 -m json.tool docs/bringup/ai_workload_bringup_flow.json`.
- Layout validation: `bash tools/ci/check_repo_layout.sh`.
- Skill validation: `python3 scripts/check_skill_change_scope.py --repo-root . --base HEAD`.

## Closeout

- skill-evolve: updated `linx-model` and `linx-superproject` with the
  model-green cube and vector attention prefix micro-profile rules.
