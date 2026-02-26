# v0.4 draft: Rendering bring-up using Mesa softpipe/llvmpipe (scaffold)

## Intent
Use Mesa’s **software rasterizers** as scaffolding to:
- validate the Linx Linux+libc runtime can run real-world rendering stacks in the emulator
- validate our driver/Winsys/WSI plumbing and test infrastructure
- produce traces + workload characterization before deciding what to harden

These software backends are **not** the end goal; they are the baseline/reference.

## Why softpipe + llvmpipe
- `softpipe`: pure C pipeline; simplest dependency story; slower but easiest to get running.
- `llvmpipe`: higher performance and wider feature coverage; depends on LLVM; good reference for shader/IR behavior.

## Phased plan

### Phase 0 — build & run Mesa in Linx emulator (headless first)
- Target: run a simple OpenGL program in emulator using software rasterizer.
- Prefer headless/surfaceless (EGL pbuffer / surfaceless) to avoid early window-system complexity.
- Deliverable: reproducible build scripts + minimal demo + image compare.

### Phase 1 — testing + workload characterization
- Run a small suite (vkmark/glmark2-like equivalents, micro scenes, shader-heavy scenes).
- Collect:
  - shader count/types, instruction mix
  - texture sampling frequency/modes
  - depth/stencil/blend usage
  - bandwidth footprints

### Phase 2 — start replacing pieces with LinxGPGPU kernels
- Introduce a Linx-target backend where shaders/compute are compiled into MPAR kernels (our SIMT kernel model).
- Keep fixed-function stages in software initially; ensure correctness.

### Phase 3 — limited hardening
- Use measurement-driven ranking to choose 1 engine at a time to harden.
- Maintain a strict fallback path to MPAR kernels.

## Notes / links
- Upstream Mesa driver locations:
  - `src/gallium/drivers/softpipe/`
  - `src/gallium/drivers/llvmpipe/`

