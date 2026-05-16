# LinxISA Documentation

<!-- Hero Banner -->
<div class="isa-hero">

## Welcome to LinxISA

**Linx** is a modern, GPU-like instruction set architecture designed for rendering and compute workloads. This is the canonical reference documentation site, built from the [linx-isa](https://github.com/LinxISA/linx-isa) superproject.

### Architecture at a Glance

| | |
|---|---|
| **ISA Version** | v0.56.2 |
| **Total Instruction Forms** | 740 |
| **Instruction Groups** | 66 |
| **Formats** | 16-bit Compressed · 32-bit Base · 48-bit HL · 64-bit Vector |
| **Specification** | [v0.56 Contract →](architecture/v0.56-architecture-contract.md) |
| **Release Notes** | [v0.56.2 →](releases/v0.56.2.md) |

</div>

---

## Quick Navigation

<div class="quick-links">

[:fontawesome-solid-microchip: **ISA Reference** — Instruction Reference](isa/index.md) {.quick-link-card}
: The complete, searchable reference for all 740 instruction forms. Browse by chapter, group, or alphabetically.

[:fontawesome-solid-book: **Full ISA Manual** — AsciiDoc/PDF](architecture/isa-manual/README.md) {.quick-link-card}
: The authoritative human-readable manual with narrative chapters, examples, and design rationale.

[:fontawesome-solid-diagram-project: **Architecture Framework** — Concepts & Contracts](architecture/README.md) {.quick-link-card}
: Understand the AVS contracts, workload engine model, rendering kernel authoring, and PTO guarantees.

[:fontawesome-solid-layer-group: **LinxCore RTL** — Hardware Implementation](architecture/linxcore/overview.md) {.quick-link-card}
: LinxCore microarchitecture, module catalog, pipeline stages, and verification matrix.

[:fontawesome-solid-rocket: **Getting Started** — Bring-up Guide](bringup/GETTING_STARTED.md) {.quick-link-card}
: Set up your development environment, run the QEMU emulator, and compile your first program.

[:fontawesome-solid-code: **Assembly Guide** — Authoring Kernels](reference/linxisa-assembly-agent-guide.md) {.quick-link-card}
: Learn the assembly syntax, calling conventions, block-structured control flow, and call/ret ABI contract.

[:fontawesome-solid-shield-halved: **Call/Ret Contract** — ABI Guarantees](reference/linxisa-call-ret-contract.md) {.quick-link-card}
: The formal ABI contract for cross-stack calls: callee-saved registers, stack alignment, and return sequence.

[:fontawesome-solid-chart-line: **Bring-up Progress** — Status & Gates](bringup/PROGRESS.md) {.quick-link-card}
: Current gate status, integration checklist, ecosystem maturity roadmap, and validation matrix.

</div>

---

## Browse Instructions by Chapter

<div class="chapter-grid">

[![](assets/ch03.svg) **Ch 03 — Encoding Formats** — Bit numbering, instruction lengths, decode tags](isa/encoding.md) {.chapter-card style="--ch03-color:#64748b"}
[![](assets/ch04.svg) **Ch 04 — Block ISA** — BSTART, BSTOP, B.ARG, B.DIM, tile/SIMT control flow](isa/groups/block_split.md) {.chapter-card style="--ch04-color:#8b5cf6"}
[![](assets/ch11.svg) **Ch 11 — AGU** — Loads, stores, prefetch, all addressing modes](isa/groups/load_register_offset.md) {.chapter-card style="--ch11-color:#059669"}
[![](assets/ch12.svg) **Ch 12 — ALU** — ADD, SUB, MUL, DIV, shifts, bit manip, LUI, CSEL](isa/groups/arithmetic.md) {.chapter-card style="--ch12-color:#0891b2"}
[![](assets/ch13.svg) **Ch 13 — FSU** — Floating-point arithmetic, FMA, format conversion](isa/groups/floating_point_arithmetic.md) {.chapter-card style="--ch13-color:#0ea5e9"}
[![](assets/ch14.svg) **Ch 14 — AMO** — LR/SC, atomic fetch-op, CAS](isa/groups/atomic.md) {.chapter-card style="--ch14-color:#e11d48"}
[![](assets/ch15.svg) **Ch 15 — BBD** — C.BSTART, C.BSTOP, block delimiters](isa/groups/c_bstart.md) {.chapter-card style="--ch15-color:#8b5cf6"}
[![](assets/ch16.svg) **Ch 16 — BRU** — Branches, CMP, SETC, SETRET, ADDTPC](isa/groups/branch.md) {.chapter-card style="--ch16-color:#7c3aed"}
[![](assets/ch17.svg) **Ch 17 — CMD** — B.CATR, B.DATR, B.HINT, block attributes](isa/groups/block_control_attribute.md) {.chapter-card style="--ch17-color:#6366f1"}
[![](assets/ch18.svg) **Ch 18 — RSV** — HL.BFI, HL.MIADD, HL.MISUB](isa/groups/reserve.md) {.chapter-card style="--ch18-color:#a16207"}
[![](assets/ch19.svg) **Ch 19 — SYS** — FENCE, barriers, EBREAK, ACR\*, cache/TLB maintenance](isa/groups/execution_control.md) {.chapter-card style="--ch19-color:#dc2626"}
[![](assets/ch20.svg) **Ch 20 — VEC** — V.\* vector forms, shuffles, reductions, division](isa/groups/shuffle.md) {.chapter-card style="--ch20-color:#2563eb"}

</div>

---

## Key Documentation

| | |
|---|---|
| **ISA Version** | v0.56.2 (see [Hardening Policy](architecture/v0.56-hardening-policy.md)) |
| **Source** | [github.com/LinxISA/linx-isa](https://github.com/LinxISA/linx-isa) |
| **ISA Manual Source** | [docs/architecture/isa-manual/src](https://github.com/LinxISA/linx-isa/tree/main/docs/architecture/isa-manual/src) (AsciiDoc) |
| **QEMU Emulator** | [avs/qemu](https://github.com/LinxISA/linx-isa/tree/main/avs/qemu) |
| **LLVM Backend** | [avs/compiler/linx-llvm](https://github.com/LinxISA/linx-isa/tree/main/avs/compiler/linx-llvm) |
| **glibc Port** | [toolchains/glibc](https://github.com/LinxISA/linx-isa/tree/main/toolchains/glibc) |
| **musl Port** | [toolchains/musl](https://github.com/LinxISA/linx-isa/tree/main/toolchains/musl) |

> **Note:** This site is generated from `linxisa-v0.56.json`. To edit the ISA specification, update the JSON source; pages regenerate automatically.
