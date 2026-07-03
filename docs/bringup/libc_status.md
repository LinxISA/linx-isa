# Linx libc Bring-up Status

Canonical libc sources:

- `lib/glibc`
- `lib/musl`

## Repositories and pins

- `lib/glibc` @ `085874633efdb9125b6a843ab180962f9eb3a9af`
- `lib/musl` @ `4ab3c65fc33279c4004f9821bebdd87e19f87c21`

## Current policy

- Bring-up deltas live in fork history (`LinxISA/glibc`, `LinxISA/musl`).
- This repository provides orchestration, runtime smoke, and status tracking.
- Release-strict gating uses canonical artifacts from `docs/bringup/gates/latest.json`.

## Current status (2026-07-03)

- glibc `G1a`: pass (`configure` + `csu/subdir_lib` + startup objects)
- glibc `G1b`: pass (`out/libc/glibc/logs/g1b-summary.txt`)
- glibc full-system runtime hello matrix: fail on the current tree
  (`workloads/generated/flow-linux-libc-20260703-r1/report.json` hard-breaks
  at `glibc-runtime`). The runner now treats `LINX_USER_TRAP`, `LINX_PANIC`,
  and `LINX_EXIT_INIT` as terminal failure markers instead of reporting this
  lane as a timeout.
- musl `M1`: pass after syncing `arch/linx64` `float.h` to the compiler's
  64-bit `long double` ABI
- musl `M2`: pass in `phase-b`
- musl `M3`: pass in the current `phase-b` build/runtime lane
- musl static+shared Linux/QEMU smoke: pass
  (`avs/qemu/out/musl-smoke/summary.json`)
- active glibc runtime blocker: `ld.so.1` faults in early `_dl_start` before
  the glibc hello markers. Focused VM trace
  `avs/qemu/out/glibc-smoke-entry-exec-hello-vmtrace-20260703-r1/qemu_glibc_runtime_entry_main.log`
  records `LINX_VM_FAULT stage=no-vma` at `tpc=0x0000003fa3aaa7c4`,
  `bpc=0x0000003fa3aaa7c2`, `addr=0x0000007f4751aa20`, followed by
  `LINX_USER_TRAP`.

## Evidence pointers

- Canonical gate artifact: `docs/bringup/gates/latest.json`
- Rendered gate table: `docs/bringup/GATE_STATUS.md`
- glibc build logs: `out/libc/glibc/logs/summary.txt`, `out/libc/glibc/logs/g1b-summary.txt`
- musl build summary: `out/libc/musl/logs/phase-b-summary.txt`
- musl runtime logs: `avs/qemu/out/musl-smoke/summary.json`,
  `avs/qemu/out/musl-smoke/summary_static.json`,
  `avs/qemu/out/musl-smoke/qemu_malloc_printf_static.log`
- glibc runtime gate: `avs/qemu/run_glibc_smoke.py`,
  `avs/qemu/out/glibc-smoke/summary.json`
- Current libc hard-break report:
  `workloads/generated/flow-linux-libc-20260703-r1/report.json`

## Notes

- Release-strict sign-off does not allow blocked waivers for required libc gates.
- Runtime numeric/benchmark parity remains outside libc bring-up scope.
- `avs/qemu/run_glibc_smoke.py` is still the intended full in-tree glibc
  hello-matrix gate, but the current full-system lane is not green.
- The pinned `emulator/qemu` checkout currently exposes only
  `linx32-softmmu` and `linx64-softmmu`; `qemu-linx` linux-user flow is an
  optional external lane, not an in-tree validated artifact.
- The PID1 wrapper no longer writes directly to the virt UART MMIO page from
  Linux userspace. Runtime visibility now depends on kernel-mediated stdio and
  terminal Linx trap/panic markers.
- The active glibc lane needs loader/kernel ELF-startup diagnosis. The current
  failure is not a QEMU deadlock: the VM trace reaches a concrete loader
  `no-vma` user trap before glibc user code starts.
