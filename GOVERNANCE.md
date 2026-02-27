# LinxISA Governance

This repository is the **LinxISA superproject**. It pins the ecosystem via submodules
and hosts the canonical documentation and bring-up gates.

## Roles

- **Maintainers** (`@LinxISA/maintainers`): final decision makers for this repository.
- **Domain owners**: responsible for specific areas via CODEOWNERS:
  - ISA: `@LinxISA/isa`
  - Compiler: `@LinxISA/compiler`
  - Emulator: `@LinxISA/emulator`
  - Kernel: `@LinxISA/kernel`
  - RTL: `@LinxISA/rtl`
  - Libc: `@LinxISA/lib`
  - Tools: `@LinxISA/tools`
  - Docs: `@LinxISA/docs`
  - Workloads: `@LinxISA/workloads`
  - AVS: `@LinxISA/avs`

## Decision making

Most changes are decided by PR review. If there is disagreement:

1. Seek consensus in the PR discussion.
2. Escalate to maintainers for a final decision.

## Change process

- Prefer **submodule-first** changes (land upstream, then bump SHA here).
- Keep `main` protected and require CI to pass.
- For ISA/spec changes, update documentation in `docs/` and validation gates in `tools/` as needed.

