# Documentation

This directory contains the complete documentation suite for LinxISA.

The current machine-readable ISA authority is
`isa/v0.58/linxisa-v0.58.json`. Start architecture work from that catalog and
`architecture/v0.58-architecture-contract.md`.

## Structure

```
docs/
├── architecture/           # ISA specification and manual
│   ├── v0.58-architecture-contract.md    # Current ISA v0.58 contract
│   └── isa-manual/                      # Full ISA manual (AsciiDoc)
│
├── bringup/               # Bring-up and validation
│   ├── GETTING_STARTED.md              # Onboarding guide
│   ├── rendering_vulkan_bringup.md     # Rendering userspace bring-up plan
│   ├── PROGRESS.md                     # Bring-up status tracker
│   ├── AVS_CONTRACT.md                 # AVS public contract
│   ├── MATURITY_PLAN.md               # Long-term roadmap
│   ├── agent_runs/                     # Multi-agent gate manifests
│   │   ├── manifest.yaml              # Gate ownership map
│   │   ├── waivers.yaml                # Explicit waiver ledger
│   │   └── checklists/                 # Per-domain checklists
│   ├── gates/                          # Gate execution artifacts
│   │   ├── latest.json                # Canonical gate report
│   │   └── logs/                       # Per-run evidence
│   └── phases/                         # Phased bring-up plans
│
├── reference/              # Examples and guides
│   ├── examples/v0.57/    # Assembly sample pack
│   ├── linxisa-call-ret-contract.md   # ABI contract
│   └── encoding_space_report.md       # Encoding analysis
│
├── matmul/                 # Matrix multiplication implementation notes
│   ├── README.md                         # Directory index
│   └── low-precision-inner-vs-outer-product.md # Low-precision dataflow tradeoff study
│
├── project/                # Repository governance
│   ├── navigation.md      # Canonical path map
│   ├── repository-flow.md # Development workflow
│   ├── omx-linxisa-playbook.md # OMX operator playbook for LinxISA
│   ├── omx-linxisa-prompt-templates.md # Reusable OMX prompt templates for LinxISA
│   ├── new-agent-sop.md   # Short SOP for new agents
│   ├── maintainer-repin-checklist.md # Repin checklist for maintainers
│   ├── linxisa-superproject-methodology-zh.tex # Chinese LaTeX manual source
│   ├── linxisa-superproject-methodology-zh.pdf # Chinese PDF manual
│   ├── superproject-whitepaper-zh.tex # Chinese methodology whitepaper source
│   ├── superproject-whitepaper-zh.pdf # Chinese methodology whitepaper PDF
│   └── superproject-bringup-methodology.md # Superproject bring-up methodology and runbook
│
└── migration/             # Historical path maps
```

## Quick Links

| Topic | File |
|-------|------|
| **New Contributors** | [bringup/GETTING_STARTED.md](bringup/GETTING_STARTED.md) |
| **ISA Specification** | [architecture/v0.58-architecture-contract.md](architecture/v0.58-architecture-contract.md) |
| **Encoding Space** | [reference/encoding_space_report.md](reference/encoding_space_report.md) |
| **Matmul Research** | [matmul/low-precision-inner-vs-outer-product.md](matmul/low-precision-inner-vs-outer-product.md) |
| **AVS Contract** | [bringup/AVS_CONTRACT.md](bringup/AVS_CONTRACT.md) |
| **Rendering Bring-up** | [bringup/rendering_vulkan_bringup.md](bringup/rendering_vulkan_bringup.md) |
| **Current Status** | [bringup/PROGRESS.md](bringup/PROGRESS.md) |
| **Navigation Policy** | [project/navigation.md](project/navigation.md) |
| **OMX Playbook** | [project/omx-linxisa-playbook.md](project/omx-linxisa-playbook.md) |
| **OMX Prompt Templates** | [project/omx-linxisa-prompt-templates.md](project/omx-linxisa-prompt-templates.md) |
| **Superproject Methodology** | [project/superproject-bringup-methodology.md](project/superproject-bringup-methodology.md) |
| **New Agent SOP** | [project/new-agent-sop.md](project/new-agent-sop.md) |
| **Maintainer Repin Checklist** | [project/maintainer-repin-checklist.md](project/maintainer-repin-checklist.md) |
| **Chinese PDF Manual** | [project/linxisa-superproject-methodology-zh.pdf](project/linxisa-superproject-methodology-zh.pdf) |
| **Chinese White Paper** | [project/superproject-whitepaper-zh.pdf](project/superproject-whitepaper-zh.pdf) |

## Key Concepts

### Bring-up Gates

The bring-up uses a gate-based validation system:

- **AVS Contract**: canonical matrix + profile/tier closure checks
- **AVS (Architecture Validation Suite)**: Compile, runtime, Linux, libc, workload, and SPEC tests
- **Model Differential**: QEMU vs pyCircuit trace comparison
- **Multi-agent**: Cross-repo closure validation

See [bringup/PROGRESS.md](bringup/PROGRESS.md) for current gate status.

### Architecture Contract

The active v0.57 contract defines the complete mandatory architecture:

1. Block-structured execution is mandatory
2. Control-flow targets MUST resolve to legal block boundaries
3. Template blocks are architecturally defined contracts
4. Two-layer state model (global + block-local)

Run validation:
```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr
```
