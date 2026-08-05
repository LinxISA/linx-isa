# LinxISA Profile Upgrade Guide

How to upgrade the active ISA profile across the superproject — what to change,
what to verify, and how to minimise version-specific references so the next
upgrade is smaller.

---

## Principles

1. **Most definitions are stable.** Instruction encodings, register names, state
   model structure, and tool interfaces rarely change between minor versions.
   Avoid sprinkling version numbers where a generic reference works.

2. **Prefer canonical references.** Instead of `isa/v0.57/linxisa-v0.57.json`,
   prefer phrasing like *"the canonical ISA catalog"* when the exact path is not
   load-bearing for the reader. When a concrete path is needed, use the
   versioned path and keep it in one obvious place per file.

3. **The ISA spec directory is the single source of truth.** All generators,
   validators, and codecs read from `isa/v<version>/`. Downstream consumers
   (docs, READMEs, scripts) should point there, not duplicate spec content.

---

## Directory Convention

```
isa/
├── v0.57/                      # ← current active profile
│   ├── linxisa-v0.57.json      #     compiled ISA catalog (golden)
│   ├── meta.json               #     profile identity
│   ├── release_manifest.json   #     release manifest
│   ├── encoding/               #     field definitions, retired encodings
│   ├── opcodes/                #     opcode tables
│   ├── registers/              #     register definitions
│   ├── state/                  #     architectural state, engine ops, PTO
│   ├── semantics_conventions.json
│   └── uop_classification_v0.57/
│
├── sail/                       # Sail formal model (consumes the catalog)
├── generated/                  # Generated codecs (consumes the catalog)
└── README.md
```

Retired profiles (v0.56 and earlier) are **not** shipped in the active
worktree. They are available through git history.

---

## Upgrade Checklist

When a new ISA profile (e.g. v0.58) becomes the active release, work through
these files. The list is ordered from most critical to least.

### Tier 1 — Must match the new profile exactly

| File | What to change |
|---|---|
| `isa/v<new>/` | Add the new profile directory with the compiled catalog, meta.json, release_manifest.json, and all state/encoding/register artifacts. |
| `tools/isa/build_golden.py` | Update `--profile` default and `choices` list. |
| `tools/isa/validate_spec.py` | Update `--profile` default and `choices` list. |
| `tools/isa/check_canonical_v057.py` | Rename to `check_canonical_v<new>.py`, update internal spec path and required mnemonics. |
| `tools/isa/test_golden_contract.py` | Update spec path and retired-encoding assertions. |
| `tools/isa/test_v057_profile.py` | Rename and update profile references. |
| `isa/generated/codecs/README.md` | Update the source-of-truth path. |
| `isa/README.md` | Update the "latest stable compiled catalog" path. |
| `isa/sail/README.md` | Update the compiled catalog path. |
| `tools/bringup/gate_registry.json` | Update all `isa/v0.57/` paths. |

### Tier 2 — Consumer references

| File | What to change |
|---|---|
| `rtl/README.md` | Update `isa/v0.57/linxisa-v0.57.json` to the new version. |
| `workloads/BENCHMARKING_METHOD.md` | Update the canonical spec path. |
| `docs/bringup/README.md` | Update spec paths in example commands. |
| `docs/README.md` | Update the architecture contract and ISA spec paths. |
| `tools/isa/` — gen_*.py defaults | Each generator's `--spec` default path. |
| `tools/bringup/` — report_*.py defaults | Each reporter's `--spec` default path. |
| `tools/analysis/` | Update spec paths in analysis scripts. |
| `avs/linx_avs_v1_test_matrix.yaml` | Update the spec file dependency path. |
| `avs/qemu/run_tests.py` | Update `LLVM_AVS_SPEC`. |
| `avs/compiler/linx-llvm/IMPLEMENTATION_CHECKLIST.md` | Update spec paths. |
| `skills/linx-skills/linx-qemu/SKILL.md` | Update retired-profile references if needed. |

### Tier 3 — Archive and historical references

| File | What to change |
|---|---|
| `docs/archive/design-updates/README.md` | Update "normative instruction catalog" path. |
| `docs/zh/archive/design-updates/README.md` | Same, Chinese version. |
| `rtl/LinxCore/docs/archive/v0.3/README.md` | Update the active uop classification pointer. |

### Tier 4 — Non-critical / best-effort

| File | What to change |
|---|---|
| `tools/LinxCoreModel/README.md` | Version string near the top. |
| `workloads/SuperNPUBench/.../build_data_obj.sh` | COMPILER_DIR default (remote path). |
| Agent run records under `docs/bringup/agent_runs/` | Add historical caveats; do not rewrite. |

---

## How to Minimise Version-Specific References

The best upgrade is the one that requires changing fewer files. When you write
or edit a file that references the ISA spec:

- **Use relative or conceptual references** where the exact version is not
  load-bearing:
  ```
  ✅ "the canonical ISA catalog"
  ✅ "the current active ISA profile"
  ❌ "isa/v0.57/linxisa-v0.57.json" (only where the exact path matters)
  ```

- **Consolidate the version string in one place per file.** If a README needs
  the path three times, put it in a prominent location once and reference it
  elsewhere.

- **Point to this guide** from version-bearing files so future maintainers know
  what to update:
  ```
  See `docs/project/isa-upgrade-guide.md` for the upgrade procedure.
  ```

---

## Verification

After every profile upgrade, run the full gate suite:

```bash
# ISA catalog integrity
python3 tools/isa/build_golden.py --profile v<new> --check
python3 tools/isa/validate_spec.py --profile v<new>
python3 tools/isa/check_canonical_v<new>.py --root .

# Generated artifact freshness
python3 tools/isa/gen_qemu_codec.py --profile v<new> --out-dir isa/generated/codecs --check
python3 tools/isa/gen_c_codec.py --profile v<new> --out-dir isa/generated/codecs --check
python3 tools/isa/gen_manual_adoc.py --profile v<new> --out-dir docs/architecture/isa-manual/src/generated --check
python3 tools/isa/gen_ssr_adoc.py --profile v<new> --out-dir docs/architecture/isa-manual/src/generated --check

# AVS and coverage
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr

# Architecture contract
python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict
```

Then grep for the old version string across the repo to catch stragglers:

```bash
git grep "v0\.<old>" -- ':!docs/archive/' ':!docs/change_log/' ':!docs/bringup/gates/logs/' ':!.omx/'
```

---

## Related Documents

- `docs/project/navigation.md` — superproject file map
- `docs/project/maintainer-repin-checklist.md` — submodule repin procedure
- `docs/bringup/README.md` — current bring-up gates
- `isa/README.md` — ISA catalog layout
