# Contributing to LinxISA

Thanks for contributing to **LinxISA**. This repository is a **superproject** that pins the full ecosystem:
compiler (LLVM), emulator (QEMU), Linux, RTL, libc, and validation suites.

## Project rules (superproject-first)

- Follow the repository navigation policy: `docs/project/navigation.md`
- Do **not** introduce new top-level directories (CI enforces layout)
- Prefer **submodule-first** changes:
  1. Land the change in the appropriate repo (e.g. `emulator/qemu`, `compiler/llvm`, `kernel/linux`)
  2. Bump the submodule SHA in this superproject

## Local checks (required for PRs)

```bash
bash tools/ci/check_repo_layout.sh
bash tools/ci/check_public_v03.sh
python3 tools/bringup/check26_contract.py --root .
mkdocs build --strict
```

Optional (slower):

```bash
bash tools/regression/run.sh
```

## Pull requests

- Use a clear title and include a short motivation/impact summary
- Keep diffs focused; avoid bundling unrelated submodule bumps
- Make sure CI is green before requesting review

