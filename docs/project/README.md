# Project Documentation

Repository-level process, governance, and navigation policies.

## Contents

- **[navigation.md](navigation.md)** - Canonical path map and forbidden paths
- **[repository-flow.md](repository-flow.md)** - Development workflow and contribution guide
- **[omx-linxisa-playbook.md](omx-linxisa-playbook.md)** - OMX operator playbook for gate triage, repin, closure, and evidence flow
- **[omx-linxisa-prompt-templates.md](omx-linxisa-prompt-templates.md)** - Reusable prompt templates for LinxISA OMX sessions
- **[superproject-bringup-methodology.md](superproject-bringup-methodology.md)** - Agent-friendly superproject bring-up methodology and operator runbook
- **[new-agent-sop.md](new-agent-sop.md)** - Short SOP for a new agent working inside the superproject
- **[maintainer-repin-checklist.md](maintainer-repin-checklist.md)** - Maintainer checklist for safe submodule repins
- **[linxisa-superproject-methodology-zh.tex](linxisa-superproject-methodology-zh.tex)** - Chinese LaTeX manual source
- **[linxisa-superproject-methodology-zh.pdf](linxisa-superproject-methodology-zh.pdf)** - Chinese PDF manual
- **[superproject-whitepaper-zh.tex](superproject-whitepaper-zh.tex)** - Chinese white paper LaTeX source
- **[superproject-whitepaper-zh.pdf](superproject-whitepaper-zh.pdf)** - Chinese methodology white paper PDF

## Navigation Policy

This workspace follows a strict navigation contract. See [navigation.md](navigation.md) for:

- Allowed top-level directories
- Canonical destinations for specific tasks
- Forbidden/replaced paths
- Submodule update procedures

## Quick Reference

| Task | Path |
|------|------|
| Runtime tests | `avs/qemu/` |
| Compile tests | `avs/compiler/linx-llvm/tests/` |
| Freestanding libc | `avs/runtime/freestanding/` |
| Linux libc sources | `lib/glibc/`, `lib/musl/` |
| PTO kernel headers | `workloads/pto_kernels/include/` |
| Assembly examples | `docs/reference/examples/v0.56/` |

## CI Validation

Before committing, verify repository layout:

```bash
bash tools/ci/check_repo_layout.sh
```
