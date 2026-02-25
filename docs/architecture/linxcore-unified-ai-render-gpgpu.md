# LinxCore Unified AI + Rendering (GPU-class) Co-Design Draft

> Status: draft / working doc
> 
> Goal: define a software+hardware co-design that lets **LinxISA + LinxCore** run
> - AI applications (inference first, training later)
> - graphics rendering (Vulkan/OpenGL)
> 
> by compiling shader/compute kernels to a **Linx SIMT model** deployed onto a **vector (VEC) execution backend**, while hardening selected hot paths into dedicated **LinxCore “engines”**.

---

## 0. Design goals (what “GPU-class” means)

### Goals
- **One ISA + one runtime model** to serve both graphics + AI compute.
- **Vulkan as the primary user-facing ABI** (graphics + compute).
- Support OpenGL via **Zink** (OpenGL-on-Vulkan) if acceptable.
- Compiler pipeline: **SPIR-V → NIR → LinxSIMT IR → LinxVEC uops**.
- Hardware: add/extend LinxCore with a **command processor + shader/compute core + fixed-function engines**.

### Non-goals (initially)
- Perfect parity with a top-tier discrete GPU across all workloads.
- Full DirectX user-mode stack.

### Performance reality check
“Not worse than GPU” is only achievable if we define (and measure) a baseline:
- baseline **GPU compute core** model (e.g. NVIDIA *SM*, AMD *CU/WGP*, Apple GPU core) and the **per-core** throughput we want to match
- target workloads (AI: GEMM/conv/attn? graphics: forward? deferred? RT?)
- per-core memory hierarchy targets (register file + L1/texture + LDS/shared) and the **chip-level** bandwidth / power / area envelope

**Assumption from discussion:** we are designing a **core** comparable to a GPU SM, and scaling out via **many cores** to form a new-style GPGPU.

---

## 1. Proposed top-level stack

### 1.1 User-facing APIs
- **Vulkan**: primary graphics+compute API.
- **OpenGL** (optional): via Mesa **Zink** (Gallium OpenGL frontend → Vulkan).
  - Advantage: avoid writing a full OpenGL driver; focus on Vulkan + compute.

### 1.2 User-mode driver plan (Mesa)
Use Mesa (now vendored as `lib/mesa3d`) and add a Linx Vulkan driver:
- Mesa areas you’ll touch:
  - `src/vulkan/` (common Vulkan runtime, WSI, layers/util)
  - `src/compiler/spirv/` (SPIR-V parsing → NIR)
  - `src/compiler/nir/` (NIR IR + optimizations)
  - (optional) `src/gallium/drivers/zink/` (OpenGL-on-Vulkan)

Create a new driver namespace (exact location TBD; typical patterns are vendor directories):
- `src/linx/vulkan/` or `src/vulkan/drivers/linx/` (depends on Mesa conventions)

Deliverables:
- `libvulkan_linx.so` ICD (Mesa)
- WSI path for Linux (DRM/KMS + Wayland/X11 as needed)

### 1.3 Kernel driver plan (Linux DRM)
A Linx GPU/NPU kernel driver providing:
- memory management (GEM/TTM or modern equivalent)
- submission queues
- sync primitives (timeline semaphores/fences)
- perf counters + debugging IOCTLs

This enables:
- Mesa Vulkan ICD talks to DRM
- user-space apps use standard Vulkan loader

---

## 2. Execution model: build on LinxISA v0.3 SIMT vector blocks

LinxISA already defines SIMT-style execution via **vector block types** (`MSEQ/MPAR/VSEQ/VPAR`) rather than a separate “GPU mode”.

Reference notes: `docs/architecture/research/linxisa-v0.3-simt-vector-model.md`

### 2.1 The core idea (ISA-grounded)
- Programmer-visible model: **SIMT** expressed as a *one-lane body* replayed over a lane space.
- Hardware backend: implement that replay efficiently on **VEC** pipelines.

Architectural mapping (strict v0.3):
- Lane space is defined by `LB0..LB2` (written by `B.DIM`), with lane counters `lc0..lc2` visible in the body.
- Canonical 1-D lowering:
  - `LB0 = lane_count` (lanes per group)
  - `LB1 = group_count`
  - linear lane index = `lc0 + lc1 * lane_count`
- Scalar instructions in a vector body are **uniform per group** (execute once per group replay), while vector instructions operate in the lane domain.

Execution families:
- `MSEQ/MPAR`: may use bridged global memory (`*.brg`) via the tile/TMA path.
- `VSEQ/VPAR`: **tile-only** (must not use `*.brg`).

### 2.2 `LB0` lane_count policy & VEC width
Critical decisions (implementation policy; ISA allows variability):
- Choose a **lane_count policy** (`LB0`, lanes per group). Common candidates: 8/16/32/64.
- Choose a **VEC width** (lanes per cycle) and how many VEC pipes per core.

Rules of thumb:
- Larger `LB0` amortizes scalar-uniform work and improves reduction/shuffle efficiency, but increases pressure from lane divergence that must be handled via **predication** (lane predicate values + `V.CSEL`/`V.PSEL`).
- VEC width should align with the `.brg` memory bridge/coalescing granularity and the tile-register banking scheme.

### 2.3 Memory execution reality: `.local` vs `.brg`
Architecturally, vector memory operations split into:
- **`.local`**: tile/local direction accesses (base: `TA/TB/TO/TS`), suitable for tile engines + scratch.
- **`.brg`**: bridged global memory accesses (base: `ri*` imported via `B.IOR`).

Bring-up constraints:
- `VPAR/VSEQ` are tile-only and MUST NOT use `.brg`.
- `MSEQ/MPAR` may use `.brg` but the path is **bridged through tile/TMA**, so the “shader core” microarchitecture must treat global memory as an engine/bridge, not a free LSU.

Implementation goal:
- coalesce `.brg` accesses across lanes/groups (merge cacheline requests, handle scatter/gather efficiently, and define per-lane fault/disable behavior consistently with the restartability contracts).

---

## 3. Hardware partitioning inside “LinxCore GPU tile”

Think of this as adding a GPU-like tile next to/inside LinxCore, controlled by command streams.

### 3.1 Always needed engines (compute-first baseline)
1) **Command Processor (CP)**
   - parses command buffers, dispatches work
   - integrates with LinxCore block/BID completion rules (engine_done)

2) **Shader/Compute Core (SIMT front-end + VEC back-end)**
   - wave scheduler
   - register file(s) for vector/scalar
   - VEC ALU pipelines
   - LSU + coalescer
   - shared memory / LDS (optional but important for performance)

3) **DMA/BLT engine**
   - fast copies, format conversions, clears

### 3.2 Rendering acceleration engines (hardened fixed-function)
Add when moving from compute-only → full graphics:
- **Raster / tiler / binning engine** (triangle setup, tile list build)
- **Texture engine** (addressing, filtering, sampler cache)
- **ROP engine** (depth/stencil test, blending, color writeback/compression)

A good staged approach is:
- Phase A: compute + blit (enables AI + simple compute rendering paths)
- Phase B: texture engine (huge for real graphics perf)
- Phase C: raster + ROP (full pipeline)

### 3.3 How this fits LinxCore block semantics
Use LinxCore’s established “block” mechanism:
- a block issues CP/engine commands via CMD uops
- block completion:
  - `complete = scalar_done && engine_done`
- on flush/redirect: kill younger blocks by BID (`bid > flush_bid`)

This gives you CPU-style speculation/control + long-latency engine work with clean cancellation rules.

---

## 4. Compiler pipeline details (Mesa → Linx)

### 4.1 Front-end inputs
- SPIR-V for Vulkan shaders + compute kernels
- (optional) OpenCL C via clc → SPIR-V path, or MLIR → SPIR-V for AI

### 4.2 Mid-end: NIR
Use NIR as the optimization hub:
- algebraic opts, CSE, loop opts, vectorization/legalization passes
- subgroup lowering and divergence-friendly transforms

### 4.3 Back-end: NIR/SPIR-V → Linx vector-block body (+ VEC lowering)
Create/choose an internal IR that makes the **Linx vector-block model** explicit:
- lane counters (`lc0..lc2`) and the canonical mapping to invocation IDs
- group-uniform vs lane-varying values (scalar body ops vs `V.*` ops)
- lane predicate values + predication strategy (`V.CSEL`/`V.PSEL`) for divergent control flow
- subgroup ops: shuffles (`V.SHFL*`) and reductions (`V.RD*`)
- `.local`/`.brg` memory selection and coalescing strategy for the bridged path

Note: an **exec-mask** may still exist as a *microarchitectural* optimization, but it is not the primary architectural programming model in strict v0.3; the compiler should be correct using lane predicate values.

Then lower to a machine model:
- scalar ops (address calc, control)
- vector ops (lane-wise ALU)
- special function units (rcp/rsqrt/sin/cos) if you choose to harden

---

## 5. AI mapping strategy

### 5.1 Unify on Vulkan compute where possible
- Many AI stacks can target Vulkan compute (via IREE/MLIR, TVM, custom backends)
- Key Vulkan features for AI performance:
  - FP16/BF16/INT8
  - subgroup ops
  - cooperative matrix / MMA-like ops (if implemented)

### 5.2 Optional: dedicated Tensor/MMA engine
If “GPU-class AI” is strict, consider hardening:
- block GEMM / MMA datapaths
- accumulator precision
- shared memory/LDS bandwidth

---

## 6. Bring-up plan (recommended milestones)

1) **Functional model** in sim/emulator: execute simple SPIR-V compute kernels.
2) **Mesa Vulkan ICD** + Linux DRM minimal: `vkQueueSubmit` + fences + simple compute.
3) **Zink** on top (optional): get OpenGL apps running quickly.
4) Add **texture engine** + sampler cache.
5) Add **raster/ROP** for full graphics perf.
6) Perf pass: occupancy, register pressure, cache policy, tiling.

---

## 7. Open questions backlog (we will answer one by one)

### A. Product targets
- What baseline GPU are we comparing to (class + bandwidth)?
- AI: inference only or training too? which models (LLM, CNN, diffusion)?
- Graphics: target API (Vulkan 1.1/1.2/1.3?), target resolution/FPS?

### B. ISA / micro-architecture
- Preferred `LB0` lane_count policy (8/16/32/64)? Fixed or variable?
- Vector width / number of VEC pipes / clock target?
- How much tile/local storage (tile regs + scratch/LDS-like) per core?
- Do we want an ISA/profile extension for per-lane control flow (exec-mask + reconvergence), or commit to predication-first shaders?

### C. Fixed-function hardening
- Which graphics stages must be fixed-function vs programmable?
- Texture formats + filtering requirements?

### D. Software choices
- Vulkan-only acceptable? OpenGL via Zink acceptable?
- Do we need OpenCL/CUDA compatibility?

---

## 8. Next action
After each of your answers, we’ll update this doc into a concrete spec (interfaces + engine list + compiler contracts).
