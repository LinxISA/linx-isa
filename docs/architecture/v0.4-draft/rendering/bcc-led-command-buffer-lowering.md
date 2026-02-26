# v0.4 draft: BCC-led Vulkan command buffer lowering

## Decision
Vulkan command buffers are **lowered/expanded by BCC (or a BCC-adjacent runtime)** into a sequence of Linx blocks.

Rationale:
- keeps on-device CP simple early (fewer corner cases)
- allows aggressive scheduling/OOO composition using LinxCore’s existing block/BID machinery
- makes bring-up/debug easier in emulator/RTL

## What this implies
- The Vulkan driver is responsible for producing a **block stream** that encodes:
  - pipeline state bindings
  - resource bindings (descriptors)
  - kernel launches (MPAR shader kernels)
  - synchronization/barriers
  - fixed-function engine invocations (DMA/clear/etc)

## Open items
1) Which parts are in **user-mode driver** vs **kernel driver**?
2) How to represent state bundles (PSO) efficiently to avoid bloating block streams?
3) How to handle secondary command buffers / multi-thread recording?
4) How to map Vulkan sync primitives (timeline semaphores) to block/BID fences.

