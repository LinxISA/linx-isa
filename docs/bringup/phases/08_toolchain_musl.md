# Phase 8: Toolchain/musl Bring-up

Canonical source repository:

- `lib/musl` (`git@github.com:LinxISA/musl.git`)

## Objective

Bring up a reproducible Linx musl path for:

- `linx64-unknown-linux-musl` (`M1/M2/M3`)
- Linux initramfs runtime smoke with a real C program using `malloc/free/printf` (`R1/R2`)

## Entry points

- musl build entrypoint:
  - `lib/musl/tools/linx/build_linx64_musl.sh`
- runtime harness:
  - `avs/qemu/run_musl_smoke.py`
- runtime sample program:
  - `avs/qemu/tests/linux_musl_malloc_printf.c`

## Default artifact layout

- musl build/install/logs:
  - `out/libc/musl/build`
  - `out/libc/musl/install`
  - `out/libc/musl/logs`
- smoke outputs:
  - `avs/qemu/out/musl-smoke/initramfs.cpio`
  - `avs/qemu/out/musl-smoke/musl_smoke`
  - `avs/qemu/out/musl-smoke/qemu.log`
  - `avs/qemu/out/musl-smoke/summary.json`

## Modes

- `phase-b`:
  - strict mode (`LINX_MUSL_MODE=phase-b`)
  - no temporary excludes allowed
- `phase-a`:
  - optional compatibility mode for temporary exclusions via `LINX_MUSL_EXTRA_EXCLUDES`
  - records active excludes and crash signature in `out/libc/musl/logs/phase-a-exclusions.md`

## Commands

Build musl (`M1/M2/M3`):

```bash
cd lib/musl
MODE=phase-b ./tools/linx/build_linx64_musl.sh
```

Run end-to-end smoke (`R1/R2`):

```bash
cd .
python3 avs/qemu/run_musl_smoke.py --mode phase-b
```

## Current status (2026-02-16)

- `M1`: pass.
- `M2`: pass in `phase-b` (strict, no temporary excludes).
- `M3`: pass in `phase-b` (shared `lib/libc.so` produced).
- `arch/linx64` atomics: `a_cas`/`a_cas_p` now use a `swapw`-backed process-global lock (non-atomic load/store CAS removed).
- `R1`: pass (sample compiles/links statically with musl sysroot, no extra harness fallback objects).
- `R2`: pass (`MUSL_SMOKE_START` and `MUSL_SMOKE_PASS` observed in `avs/qemu/out/musl-smoke/qemu.log`).
- Linux no-libc initramfs baselines (`smoke.py` / `full_boot.py`): pass with default QEMU path selection.
  - signal applets currently emit fallback `sigill: ok` / `sigsegv: ok` markers while signal-return paths are being hardened.

## Baseline repro pointers

- baseline freeze:
  - `out/libc/musl/logs/baseline.md`
- latest Linux userspace boot results:
  - `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`
  - `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py`

## Exit criteria

- `M1/M2` pass in strict mode (`phase-b`) with no temporary excludes.
- `M3` passes in `phase-b` (`out/libc/musl/logs/phase-b-summary.txt` shows `m3=pass`).
- runtime sentinels are observed under QEMU:
  - `MUSL_SMOKE_START`
  - `MUSL_SMOKE_PASS`
