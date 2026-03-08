# v0.4 Notebook Migration Audit

Last updated: 2026-03-07

This file tracks whether each restored pre-canonical v0.4 notebook page has a
live canonical destination.

Deletion rule:

- Do not delete this notebook tree while any row below remains `Partial` or
  `Open`.
- A page can be removed only after its normative content is promoted into live
  canonical surfaces, or after it is explicitly reclassified as historical
  planning material that is intentionally retained outside the live contract.

Status meanings:

- `Canonicalized`: the normative content is present in live v0.4 contract/state
  surfaces.
- `Partial`: some core semantics are canonicalized, but the page still carries
  unresolved or draft-only material that is not yet frozen elsewhere.
- `Open`: no live canonical destination exists yet for the page's primary
  content.
- `Index`: navigation or retention metadata only.

## Audit Matrix

| Source | Live canonical destination(s) | Supporting reference(s) | Status | Remaining gap before deletion |
| --- | --- | --- | --- | --- |
| `README.md` | None required. This page is the notebook index and retention notice. | None. | `Index` | Keep as the notebook landing page while any audit row remains `Partial` or `Open`. |
| `notes/simt-kernel-body-controlflow.md` | `isa/v0.4/state/kernel_execution.json`; `docs/architecture/v0.4-architecture-contract.md`; `docs/architecture/isa-manual/src/chapters/03_programming_model.adoc`; `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc`; `docs/architecture/isa-manual/src/chapters/10_system_and_privilege.adoc` | None. | `Canonicalized` | None for the body-control-flow contract. |
| `notes/unified-lx64-kernel-encoding.md` | `isa/v0.4/state/kernel_execution.json`; `docs/architecture/isa-manual/src/chapters/03_programming_model.adoc`; `docs/architecture/isa-manual/src/chapters/05b_regid10_operand_encoding.adoc`; `docs/architecture/isa-manual/src/chapters/06_assembly_conventions.adoc`; `docs/architecture/isa-manual/src/chapters/09_memory_operations.adoc` | None. | `Canonicalized` | None for the unified `l.*`/`v.*` derivation rule, mixed-class broadcast/write legality examples, operand namespaces, and explicit-only `.brg` address-formation contract. |
| `notes/v0.4-deltas.md` | `docs/architecture/v0.4-architecture-contract.md`; `isa/v0.4/state/kernel_execution.json`; `isa/v0.4/state/rendering_profile.json`; `docs/architecture/isa-manual/src/chapters/03_programming_model.adoc`; `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc`; `docs/architecture/isa-manual/src/chapters/09_memory_operations.adoc` | None. | `Canonicalized` | None. The live architecture contract now carries the canonical `v0.4` delta summary, and rendering-stage follow-up items are either promoted into dedicated canonical pages or explicitly marked deferred there. |
| `rendering/arch-overview.md` | `docs/architecture/v0.4-architecture-contract.md`; `docs/architecture/v0.4-workload-engine-model.md`; `isa/v0.4/state/rendering_profile.json`; `docs/architecture/isa-manual/src/chapters/09_memory_operations.adoc` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the workload-target statement, VEC-first programmable execution role, and memory-boundary rule. |
| `rendering/bcc-led-command-buffer-lowering.md` | `docs/architecture/v0.4-rendering-command-contract.md` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md`; `rendering/linxgpgpu-core-arch.md` | `Canonicalized` | None for the BCC-led lowering ownership split and submission contract. |
| `rendering/bringup-plan-to-vulkan.md` | `docs/bringup/rendering_vulkan_bringup.md` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the staged Mesa, `softpipe`, `lavapipe`, and emulator-first bring-up sequence. |
| `rendering/hardening-experiment-plan.md` | `docs/architecture/v0.4-hardening-policy.md` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the measurement-driven hardening workflow, candidate priority classes, and acceptance criteria. |
| `rendering/linxgpgpu-core-arch.md` | `docs/architecture/v0.4-workload-engine-model.md`; `docs/architecture/v0.4-architecture-contract.md`; `docs/architecture/v0.4-rendering-command-contract.md`; `docs/architecture/linxcore/overview.md`; `docs/architecture/linxcore/microarchitecture.md`; `isa/v0.4/state/kernel_execution.json`; `isa/v0.4/state/rendering_profile.json`; `docs/architecture/isa-manual/src/chapters/03_programming_model.adoc`; `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc`; `docs/architecture/isa-manual/src/chapters/09_memory_operations.adoc` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the BCC-plus-engine composition rule, VEC fallback model, tile handoff rule, and LinxCore block/BID execution relationship. Pipeline partitioning, binning strategy, and cache policy remain intentionally unfrozen in the live contract. |
| `rendering/mesa-bringup-with-softpipe-llvmpipe.md` | `docs/bringup/rendering_vulkan_bringup.md` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the Mesa software-backend scaffold, `softpipe`/`llvmpipe` role split, and workload-characterization bring-up policy. |
| `rendering/pipeline-modes-cpu-plus-shadercore.md` | `docs/architecture/v0.4-rendering-command-contract.md`; `docs/architecture/v0.4-rendering-kernel-authoring.md`; `docs/architecture/v0.4-architecture-contract.md`; `docs/architecture/linxcore/microarchitecture.md`; `isa/v0.4/state/rendering_profile.json` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the immediate-style versus tile-based compatibility rule, the BCC-plus-VEC composition boundary, and the intentionally unfrozen first-acceleration stage boundary. |
| `rendering/pto-rendering-kernel-style.md` | `docs/architecture/v0.4-rendering-kernel-authoring.md` | `workloads/pto_kernels/README.md`; `docs/architecture/v0.4-rendering-pto-contract.md` | `Canonicalized` | None for the current rendering-kernel authoring guidance and workload-aligned engine split. |
| `rendering/pto-rendering-ops.md` | `docs/architecture/v0.4-rendering-pto-contract.md` | `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`; `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc`; `workloads/pto_kernels/README.md` | `Canonicalized` | None for the current rendering PTO carrier rules, canonical TEPL-backed set, and explicit non-assignment of planning-only ops. |
| `rendering/pto-rendering-tile-conventions.md` | `isa/v0.4/state/rendering_profile.json`; `docs/architecture/v0.4-architecture-contract.md`; `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc` | None. | `Canonicalized` | None for the first frozen `4KB` `1024x1` row-major profile. Future alternative layouts remain out of scope. |
| `rendering/render-state-conventions.md` | `isa/v0.4/state/rendering_profile.json`; `docs/architecture/v0.4-architecture-contract.md`; `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc` | None. | `Canonicalized` | The state-placement rule is canonicalized. Concrete `RenderStateTile` packing is still open by design, but that was not frozen in this note either. |
| `rendering/tau-as-hardening-substrate.md` | `docs/architecture/v0.4-hardening-policy.md`; `docs/architecture/linxcore/microarchitecture.md`; `isa/v0.4/state/rendering_profile.json`; `docs/architecture/v0.4-architecture-contract.md`; `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the TAU-as-substrate policy, tile-visible handoff contract, and LinxCore block/BID integration rules. Offload granularity and TEPL-versus-microkernel choice remain intentionally unfrozen in the live policy. |
| `rendering/tile-based-rendering-on-linx.md` | `docs/architecture/v0.4-rendering-command-contract.md`; `docs/architecture/v0.4-rendering-kernel-authoring.md`; `isa/v0.4/state/rendering_profile.json`; `docs/architecture/v0.4-architecture-contract.md` | `docs/architecture/linxcore-unified-ai-render-gpgpu.md` | `Canonicalized` | None for the optional tile-based strategy boundary, the early BCC-binning plus VEC tile-local shading baseline, and the explicit deferral of exact tile size, flush policy, and MSAA/compression staging. |

## Required Follow-up Before Any Notebook Deletion

- Promote or explicitly retire the `Partial` rows in this audit.
- Define canonical destinations for every `Open` row, or deliberately keep
  those pages as archived planning material outside the live contract.
- Re-run the canonical spec/docs validation gates only after the migration
  status above is updated.
