# Architecture / LinxArch Checklist

- [ ] ID: ARCH-001 Keep LinxArch LinxCore contract pages present and linked in mkdocs navigation.
  Command: `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict --require-mkdocs`
  Done means: LinxCore architecture pages exist, mkdocs nav includes them, and link targets resolve.

- [ ] ID: ARCH-002 Keep architecture verification matrix synchronized with required gate names.
  Command: `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict`
  Done means: verification matrix contains every required Architecture/LinxCore/Testbench/pyCircuit/LinxTrace gate key.

- [ ] ID: ARCH-003 Keep the live v0.4 architecture contract and LinxCore contract pages cross-linked.
  Done means: `v0.4-architecture-contract.md` references LinxCore pages and LinxCore overview references the v0.4 scope.

- [ ] ID: ARCH-004 Ensure architecture-affecting changes update LinxArch before implementation sign-off.
  Done means: architecture gate rows are green and no unresolved contract drift is present.
