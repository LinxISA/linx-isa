# v0.4 draft: Limited hardening experiment plan (render + AI)

## Principle
- **Hardening is limited**: only the most common + best ROI + easiest-to-verify units become fixed-function engines.
- Everything else must have a **VEC-kernel fallback** (MPAR shader kernels) orchestrated by the command processor / BCC scheduling.
- The chip is a composition of **heterogeneous blocks**, allowed to run out-of-order, but retiring/visibility is managed by LinxCore block/BID rules.

## What we need to measure (to decide what to harden)
For representative workloads, collect:
- instruction mix (ALU, LDS/shared, memory, special ops)
- texture/sample count, filter modes, format usage
- depth/stencil/blend frequency
- bandwidth (bytes read/write), cache hit rates if modeled
- occupancy limits (regs/LDS)

## Candidate engines (initial list)
These are typical high-ROI candidates; we will rank them using the measurements above:
1) **DMA/BLT/Clear** (copies, resolves, clears, format conversion)
2) **Texture/Sampler** (addressing + filtering + cache)
3) **Depth/Stencil + Blend (ROP)**
4) **Raster/Tiler/Binner** (triangle setup + binning)
5) **Tensor/MMA micro-engine** (AI focus; optional)

## Experimental workflow (draft)
1) Baseline: everything in MPAR kernels + minimal DMA.
2) Add instrumentation:
   - Mesa driver counters (API-level and shader compiler-level)
   - kernel/driver submission stats
   - (later) hardware perf counters in RTL/emulator
3) Run a benchmark suite (to be defined) and produce a ranked heatmap.
4) Pick top-1 engine to harden; define its ISA/command interface + fallback path.
5) Iterate.

## Open questions
- Benchmark/workload suite definition.
- Which metrics are obtainable in each environment (emulator vs RTL vs silicon).
- Acceptance criteria for “worth hardening”.
