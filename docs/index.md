# LinxISA Documentation

<div class="isa-hero">

## Published Manual Surface

This site now uses the imported LinxISA manual hierarchy as the primary public
surface. English lives at the root, Chinese lives under `/zh/`, and both share
the same Material theme, information architecture, and language mapping.

### What Changed

| | |
|---|---|
| **Primary doc layout** | Patch-derived manual hierarchy |
| **Canonical normative source** | [v0.56 contracts + AsciiDoc manual](architecture/README.md) |
| **Machine-generated appendix** | [ISA appendix reference](isa/index.md) |
| **Chinese version** | `/zh/` with path parity |

</div>

---

## Start Here

<div class="quick-links">

[:fontawesome-solid-circle-info: **Design Background**](background/index.md) {.quick-link-card}
: Why LinxISA exists, what block instructions are, and how the architecture differs from mainstream CPU and GPU ISA designs.

[:fontawesome-solid-diagram-project: **Overall Architecture**](isa/arch/bisa.md) {.quick-link-card}
: Block structure, execution model, program order, branching, ACR, and exception behavior in the public manual hierarchy.

[:fontawesome-solid-memory: **Architectural State**](isa/register/common/intro.md) {.quick-link-card}
: GGPR, SSR, block-local state, and the layered execution-state model used by LinxISA.

[:fontawesome-solid-table-cells-large: **Data Types**](isa/datatype/intro.md) {.quick-link-card}
: The scalar, vector, floating-point, integer, and microscaling type system used across the ISA.

[:fontawesome-solid-microchip: **Instruction-Set Overview**](isa/instset/baseInstrs.md) {.quick-link-card}
: The current public view of base, compressed, standard, long, vector, and template instruction families.

[:fontawesome-solid-book-open: **Programming Manual**](compiler/manuals.md) {.quick-link-card}
: Assembly/programming workflow, heterogeneous execution model, and host/device toolchain guidance.

[:fontawesome-solid-book: **Normative Contracts**](architecture/v0.56-architecture-contract.md) {.quick-link-card}
: The live v0.56 contract pages and the English AsciiDoc manual remain the normative architecture source.

[:fontawesome-solid-list: **ISA Appendix Reference**](isa/index.md) {.quick-link-card}
: The current machine-generated appendix remains published for exact A–Z instruction, group, and encoding lookup.

</div>

---

## Reading Model

1. Use the public manual hierarchy under `background/`, `compiler/`, and the
   new `isa/` subsections for the primary published narrative.
2. Use the [canonical architecture pages](architecture/README.md) and the
   [AsciiDoc ISA manual](architecture/isa-manual/README.md) for normative
   English contract text.
3. Use the [ISA appendix reference](isa/index.md) for exact generated
   instruction/group detail.

---

## Key Surfaces

| Surface | Purpose |
|---|---|
| [background/index.md](background/index.md) | High-level rationale and positioning |
| [isa/arch/bisa.md](isa/arch/bisa.md) | Primary imported architecture narrative |
| [isa/register/common/intro.md](isa/register/common/intro.md) | Published register/state overview |
| [isa/datatype/intro.md](isa/datatype/intro.md) | Published data-format overview |
| [compiler/manuals.md](compiler/manuals.md) | Programming/manual workflow guidance |
| [architecture/v0.56-architecture-contract.md](architecture/v0.56-architecture-contract.md) | Normative v0.56 contract |
| [architecture/isa-manual/README.md](architecture/isa-manual/README.md) | Normative English manual source/build |
| [isa/index.md](isa/index.md) | Generated appendix/reference surface |

> The root site is intentionally split into a primary manual hierarchy and a
> generated appendix. The appendix is not retired; it is demoted from “home
> page” status to “reference backplane” status.
