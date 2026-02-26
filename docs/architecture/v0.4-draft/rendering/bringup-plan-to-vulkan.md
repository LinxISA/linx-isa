# v0.4 draft: Rendering bring-up plan (Mesa → emulator → Vulkan runs)

Goal: **in the Linx emulator**, reach a state where we can run **Vulkan applications** (at least headless/offscreen) using Mesa’s software Vulkan backend as the initial reference, and then iterate toward LinxGPGPU acceleration.

Assumptions (current direction):
- Start with Mesa **softpipe** bring-up first (lowest dependency path), then expand.
- Final milestone for this plan: **Vulkan runs** in emulator (feature completeness can be staged).
- Hardening decisions come *after* we have a working stack + profiling.

---

## Stage 0 — “platform sanity” prerequisites

**Deliverable:** emulator can boot Linux userspace and run dynamic binaries reliably.

Gate:
- can run: `uname -a`, `ldd --version`, `python3 --version` (or at least a minimal shell)
- filesystem has enough space for a Mesa install prefix + test binaries

Artifacts:
- a reproducible emulator launch config
- a reproducible Linx Linux rootfs/sysroot reference

---

## Stage 1 — Build Mesa for Linx (host-side cross build preferred)

**Deliverable:** Mesa built for Linx, installed into a sysroot/prefix used by emulator.

Recommendations:
- Use Meson + Ninja.
- Start with **OpenGL + Gallium softpipe** only (avoid LLVM dependency at first).

Gate:
- Mesa libraries present in the prefix (GL/EGL/GBM as needed)
- Can run `glxinfo` is optional; headless path is OK.

Notes:
- We keep WSI/window-system dependencies minimal (prefer surfaceless/pbuffer).

---

## Stage 2 — OpenGL “first pixels” via softpipe (headless/offscreen)

**Deliverable:** In emulator, a minimal GL program renders offscreen and dumps an image/checksum.

Suggested target:
- EGL surfaceless or pbuffer context
- Render a triangle/quad with a tiny shader
- Read back RGBA, dump PPM/RAW, or compute a deterministic checksum

Gate:
- deterministic output across runs (within a tolerance if needed)

Why this stage matters:
- Proves dynamic loader + libc + Mesa + shader compiler path can execute in Linx emulator.

---

## Stage 3 — Vulkan “first device” (software Vulkan in Mesa)

**Deliverable:** In emulator, Vulkan loader + a software Vulkan ICD works.

Suggested baseline Vulkan driver:
- Mesa **lavapipe (lvp)** as the reference software Vulkan implementation.

Gates (in increasing strength):
1) `vulkaninfo` runs and enumerates 1 physical device.
2) A headless Vulkan sample runs:
   - create instance/device
   - create a storage buffer / image
   - run a simple compute or graphics pipeline
   - copy results back, validate checksum

Note:
- This avoids needing X11/Wayland early.

---

## Stage 4 — Optional: WSI / presentation

**Deliverable:** a Vulkan app that presents frames (X11/Wayland/DRM).

Gate:
- `vkcube` or a minimal present demo runs.

This stage can be deferred until we need interactive demos.

---

## Stage 5 — Start replacing software pieces with LinxGPGPU kernels (future)

Out of scope for “Vulkan runs”, but the next step:
- introduce a Linx Vulkan driver path where shader kernels compile to MPAR kernels
- keep a fallback to software (lavapipe/softpipe) while verifying correctness

---

## Metrics to collect from day 1
- shader count and size
- instruction mix proxies (NIR stats / LLVM stats if applicable)
- memory bandwidth estimates (bytes read/write per frame)
- texture sample counts and formats (once we run real scenes)

---

## Open questions
- Mesa install prefix in emulator rootfs: **`/opt/mesa`** (chosen).
- Build mode: **cross-compile on host** (chosen).
- Do we need OpenGL at all after Vulkan is up, or keep it for debugging/regression?
