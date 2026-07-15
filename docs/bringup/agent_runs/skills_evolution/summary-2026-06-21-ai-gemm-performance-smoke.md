# AI GEMM Performance Smoke Skill Evolution

- Generated (UTC): `2026-06-21T20:24:30Z`
- Skills submodule: `skills/linx-skills`
- Skills SHA: `f5391e90da9b11cb6b1ccd3978eb616d6aad20ba`
- Updated skill: `linx-superproject`

## Reason

`pto-kernel-gemm_performance` is now promoted through source, compiler, QEMU,
and `tools/LinxCoreModel/bin/gfsim -f <elf>` using its `PTO_QEMU_SMOKE`
bit-pattern copy branch.

The reusable boundary is that this case keeps `repeat_tiles=3` but verifies the
final repeat through a precomputed expected-bit table. This avoids treating
model-side oracle arithmetic as the success criterion while preserving the
QEMU-to-model workload-output check.

## Evidence

- Targeted run: `ai-debug-pto-gemm-performance-03`, 1 selected, 1 final model green.
- Regression run: `ai-regression-pto-promoted-gemm-performance-01`, 22 selected, 22 final model green.
- Skill validation: `quick_validate.py linx-superproject`.
- Scope guard: `check_skill_change_scope.py --repo-root skills/linx-skills --base origin/main`.
- Install: `install_canonical_skills.sh`.

## Closeout

- skill-evolve: updated `linx-superproject` with the repeated GEMM smoke boundary and precomputed-oracle rule.
