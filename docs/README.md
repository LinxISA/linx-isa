# Documentation

This directory contains the complete documentation suite for LinxISA.

## Structure

```
docs/
├── architecture/           # ISA specification and manual
│   ├── v0.3-architecture-contract.md    # ISA v0.3 contract
│   └── isa-manual/                      # Full ISA manual (AsciiDoc)
│
├── bringup/               # Bring-up and validation
│   ├── GETTING_STARTED.md              # Onboarding guide
│   ├── PROGRESS.md                     # Bring-up status tracker
│   ├── CHECK26_CONTRACT.md             # 26-point ISA contract
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
│   ├── examples/v0.3/     # Assembly sample pack
│   ├── linxisa-call-ret-contract.md   # ABI contract
│   └── encoding_space_report.md       # Encoding analysis
│
├── project/                # Repository governance
│   ├── navigation.md      # Canonical path map
│   └── repository-flow.md # Development workflow
│
└── migration/             # Historical path maps
```

## Quick Links

| Topic | File |
|-------|------|
| **New Contributors** | [bringup/GETTING_STARTED.md](bringup/GETTING_STARTED.md) |
| **ISA Specification** | [architecture/v0.3-architecture-contract.md](architecture/v0.3-architecture-contract.md) |
| **Current Status** | [bringup/PROGRESS.md](bringup/PROGRESS.md) |
| **Navigation Policy** | [project/navigation.md](project/navigation.md) |

## Key Concepts

### Bring-up Gates

The bring-up uses a gate-based validation system:

- **check26**: 26-point ISA contract validation
- **AVS (Architecture Validation Suite)**: Compile and runtime tests
- **Model Differential**: QEMU vs pyCircuit trace comparison
- **Multi-agent**: Cross-repo closure validation

See [bringup/PROGRESS.md](bringup/PROGRESS.md) for current gate status.

### Architecture Contract

The ISA v0.3 contract defines mandatory behaviors:

1. Block-structured execution is mandatory
2. Control-flow targets MUST resolve to legal block boundaries
3. Template blocks are architecturally defined contracts
4. Two-layer state model (global + block-local)

Run validation:
```bash
python3 tools/bringup/check26_contract.py --root .
```
