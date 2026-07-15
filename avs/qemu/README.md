# LinxISA QEMU test suite

This folder contains small, freestanding C tests compiled for LinxISA and run on the Linx QEMU `virt` machine.

Key constraints:

- The checked-in runner first builds a single aggregate `ET_REL` object with
  `ld.lld -r`, then links a firmwareless direct-boot `ET_EXEC` image at
  `0x10000` with an exported `__end_init_stack` symbol before invoking QEMU.
- No libc; keep tests freestanding and prefer the checked-in runtime/test helpers over ad-hoc external harnesses.
- UART output is via MMIO at `0x10000000`.
- Program termination is via the SiFive-style test finisher at `0x10009000`.
  The low 16 bits carry the finisher status (`0x5555` pass, `0x3333` fail,
  `0x7777` reset) and the upper 16 bits carry an optional failure code.

Runtime note:

- On the current Linx `virt` machine, Linux/system boots leave the test
  finisher disabled by default to avoid colliding with guest MMIO usage during
  init/userspace transitions.
- Freestanding AVS runners enable it explicitly with
  `LINX_VIRT_TEST_FINISHER=1`.

## Requirements

- LinxISA Clang: `compiler/llvm/build-linxisa-clang/bin/clang`
- LinxISA LLD: `compiler/llvm/build-linxisa-clang/bin/ld.lld`
- QEMU: `emulator/qemu/build-linx/qemu-system-linx64` for the current local
  bring-up line, or `QEMU=/path/to/qemu-system-linx64` for an explicit clean or
  external build.

Current bring-up helper for the live dirty-source QEMU line:

```bash
bash tools/bringup/run_qemu_build_local.sh
```

This prints the current rebuilt `qemu-system-linx64` path, which is the
boot-proof-passing local line as of the current bring-up state.

`run_tests.py` requires QEMU to be supplied through `--qemu` or `QEMU`.
Strict lanes additionally require a clean, HEAD-matched build provenance
marker; no in-tree or home-directory build is selected implicitly.

Override paths with environment variables:

```bash
export CLANG=/path/to/clang
export LLD=/path/to/ld.lld
export QEMU=/path/to/qemu-system-linx64
```

## Run

```bash
cd avs/qemu
./run_tests.sh
```

`run_tests.sh` is just a thin wrapper over `python3 run_tests.py`.

Active runtime note:

- the live QEMU runtime lane keeps the `system`, `callret`, scalar, and the
  still-supported handwritten `v03` SIMT/vector suites;
- the older handwritten `v04_vector_ops` runtime suite is removed from the
  active surface on this Bisheng branch because the current compiler/MC stack
  does not accept that handwritten asm dialect reliably enough for gating.

Run a specific suite:

```bash
./run_tests.sh --suite arithmetic
./run_tests.sh --suite branch
./run_tests.sh --suite move
./run_tests.sh --suite jumptable
./run_tests.sh --suite varargs
```

Run everything (includes float + atomic):

```bash
./run_tests.sh --all --timeout 20
```

List suites:

```bash
./run_tests.sh --list-suites
```

Compile-only:

```bash
./run_tests.sh --compile-only
```

Verbose build/run commands:

```bash
./run_tests.sh -v --suite arithmetic
```

Increase timeout:

```bash
./run_tests.sh --timeout 10
```

Enable host heartbeat during long runs (prints elapsed/idle/bytes):

```bash
./run_tests.sh --suite system --timeout 30 --heartbeat-sec 2
```

Fail early when QEMU has no stdout/stderr progress for too long:

```bash
./run_tests.sh --suite system --timeout 60 --heartbeat-sec 2 --no-progress-timeout 15
```

Rebuild from scratch (clear all intermediates):

```bash
rm -rf out
./run_tests.sh --all --compile-only
```

Custom output directory:

```bash
./run_tests.sh --out-dir /tmp/linx-qemu-tests --all --compile-only
```

## Outputs

- `out/linx-qemu-tests.o`: aggregate `ET_REL` object built with `ld.lld -r`.
- `out/linx-qemu-tests.elf`: firmwareless direct-boot `ET_EXEC` image passed to QEMU as `-kernel`.

## Linux musl smoke

For Linux initramfs + musl runtime smoke, use the full sample set in gate
runs:

```bash
python3 avs/qemu/run_musl_smoke.py --mode phase-b --sample all
```

`run_musl_smoke.py` links the sample at a high userspace image base by default
(`--image-base 0x40000000`) to avoid low-VA overlap with the current kernel mapping.
The default runner is the full-system kernel/initramfs lane. The full sample
set covers malloc/printf, fork/wait, fork/exec, stdio flushing, and C++
startup. For a narrow local repro, pass one or more explicit `--sample` values;
omitting `--sample` keeps the lightweight `malloc_printf` smoke.

`--sample all` is the hosted libc gate group. System probes that intentionally
wait for kernel-side behavior, such as `ebarg_timer`, remain explicit samples;
use `--sample ebarg_timer` for that probe or `--sample system-all` when
intentionally running every runner entry.

When an external Linx linux-user QEMU build is available, run the same
compile/link smoke directly as a process ABI gate before entering the
full-system lane:

```bash
python3 avs/qemu/run_musl_smoke.py \
  --mode phase-b \
  --link static \
  --runner user \
  --qemu-user emulator/qemu/build-user/qemu-linx
```

The user-mode runner invokes `qemu-linx -L <sysroot> <sample.elf>` and checks
the same stdout pass markers. It is intentionally a pre-rootfs gate: it can
validate target ELF startup, libc syscalls, and QEMU linux-user dispatch, but
it does not replace the system-mode kernel/rootfs regression.

The pinned `emulator/qemu` checkout in this repository currently exposes only
`linx32-softmmu` and `linx64-softmmu` targets. Treat `--runner user` as an
optional external/recovered lane until a Linx linux-user target is added back
to the fork and validated here.

For the glibc static hello lane, use:

```bash
python3 avs/qemu/run_glibc_smoke.py \
  --runner user \
  --qemu-user emulator/qemu/build-user/qemu-linx
```

The glibc user-mode runner defaults to `hello_glibc_static`, matching the
direct `qemu-linx -L <glibc-root> <static-elf>` flow.

Artifacts are written under:

- `avs/qemu/out/musl-smoke/`

## Linux boot proof

For the canonical Linx Linux-on-QEMU boot proof lane, run:

```bash
QEMU="$(bash tools/bringup/run_qemu_build_local.sh)" \
python3 avs/qemu/run_linux_boot_proofs.py
```

This runs the two kernel-side proof scripts sequentially against the rebuilt
`vmlinux` and current Linx `virt` machine:

- `boot_userspace_proof.py`: boots a `tinytrap` initramfs and proves the guest
  reached userspace instruction fetch at `0x10000` / `0x10002`
- `boot_poweroff_proof.py`: boots a raw `tiny` PID1 and proves the guest
  reaches the native poweroff lane and exits QEMU cleanly

Run just one half when narrowing regressions:

```bash
python3 avs/qemu/run_linux_boot_proofs.py --userspace-only
python3 avs/qemu/run_linux_boot_proofs.py --poweroff-only
```

## Call/Ret contract gate

Run the positive call/ret runtime matrix:

```bash
python3 avs/qemu/run_tests.py \
  --suite callret \
  --require-test-id 0x140b \
  --require-test-id 0x140c
```

Run strict call/ret contract checks:
negative cases must trap with deterministic causes, and positive cases must
run without block-format faults.

```bash
python3 avs/qemu/run_callret_contract.py
```

Run Linux+musl call/ret sample with strict Linux cross-stack audit:

```bash
python3 avs/qemu/run_musl_smoke.py \
  --sample callret \
  --link both \
  --callret-crossstack strict
```

Enable additional whole-vmlinux contract audit (optional, slower):

```bash
LINX_AUDIT_VMLINUX=1 python3 avs/qemu/run_musl_smoke.py \
  --sample callret \
  --link both \
  --callret-crossstack strict
```

## Memory map (Linx virt machine)

| Address | Purpose |
|--------:|---------|
| `0x00008000` | failure record (`test_result_t`) |
| `0x00010000` | kernel load base (`.text/.data/...`) |
| `0x10000000` | UART data register |
| `0x10009000` | test finisher (write pass/fail/reset status) |
