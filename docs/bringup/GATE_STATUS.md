# Bring-up Gate Status (Canonical)

This file is generated from `docs/bringup/gates/latest.json` via `python3 tools/bringup/gate_report.py render`.

Last generated (UTC): `2026-07-15 15:26:30Z`

## Lane `pin` (`2026-07-15-v0565-maintenance`)

- Timestamp (UTC): `2026-07-15 15:26:30Z`
- Profile: `release-strict`
- Lane policy: `pin-only`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `785d1b51ecc2042a94873665ec4b745d85473504` (`${LINXISA_ROOT}/lib/glibc`)
  - `linux`: `1d79efccf6b41bc675342e1b283b5ffd55f474a4` (`${LINXISA_ROOT}/kernel/linux`)
  - `linx-isa`: `4a47f4ab548f49b991dd7f48e2760591ff0a512f` (`${LINXISA_ROOT}`)
  - `linx-skills`: `dda5018926e39b19d647d72edb30f2ce60215d46` (`${LINXISA_ROOT}/skills/linx-skills`)
  - `linxcore`: `191fec59addc89aea5ebb004cf0acc55def271ff` (`${LINXISA_ROOT}/rtl/LinxCore`)
  - `linxcore-model`: `3bc1e6e2ceb2d578204013220cb14f67043c8eb7` (`${LINXISA_ROOT}/tools/LinxCoreModel`)
  - `llvm`: `7eee9db590cf131fa0498b7808ae279d080e8433` (`${LINXISA_ROOT}/compiler/llvm`)
  - `mesa3d`: `11c1663090d31ee744059281c4fa8f347e10e023` (`${LINXISA_ROOT}/lib/mesa3d`)
  - `model`: `bab2223aa2c18c5aa79d60115981d94d2b23cea9` (`${LINXISA_ROOT}/tools/model`)
  - `musl`: `4ab3c65fc33279c4004f9821bebdd87e19f87c21` (`${LINXISA_ROOT}/lib/musl`)
  - `pto-kernels`: `43e606b6c90d8ffbc939f4f23c70fcc8b37080f0` (`${LINXISA_ROOT}/workloads/pto_kernels`)
  - `ptoas`: `939e9e0fe1a3a2349207e36d848fc6232faa135c` (`${LINXISA_ROOT}/compiler/ptoas`)
  - `pycircuit`: `1d7b6fcf42c0b59bb2c5b5bced220df90fb0f54f` (`${LINXISA_ROOT}/tools/pyCircuit`)
  - `qemu`: `97b08e4b67fb1291172bc703efcf880fbca867bf` (`${LINXISA_ROOT}/emulator/qemu`)
  - `supernpu-bench`: `497cf3f7ebf7c5c18c707b82481e2285d0b0e07f` (`${LINXISA_ROOT}/workloads/SuperNPUBench`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| compiler | Linx32 compiler AVS canonical codec and call/return | yes | no | `compiler` | `TARGET=linx32 avs/compiler/linx-llvm/tests/run.sh` | ✅ pass (`closed`) | `747/747 round trips; 734 assembled canonical forms; negative spelling and call/return tests passed` |
| compiler | Linx64 compiler AVS canonical codec and call/return | yes | no | `compiler` | `TARGET=linx64 avs/compiler/linx-llvm/tests/run.sh` | ✅ pass (`closed`) | `747/747 round trips; 734 assembled canonical forms; negative spelling and call/return tests passed` |
| docs | Normative English, Chinese mirror, generated pages, images, links, mirrors, and AsciiDoc | yes | no | `docs` | `python3 docs/check_documentation.py --root . && mkdocs build --strict && mkdocs build --strict -f mkdocs.zh.yml && bundle exec asciidoctor --failure-level WARN` | ✅ pass (`closed`) | `711 instruction pages; 66 group pages; 748 SVGs; strict English/Chinese MkDocs and AsciiDoc passed` |
| isa | v0.56.5 golden, schema, overlap, field/uop, and generator drift | yes | no | `isa` | `python3 tools/isa/build_golden.py --profile v0.56 --check && python3 tools/isa/validate_spec.py --profile v0.56 && python3 tools/isa/test_golden_contract.py && python3 tools/isa/report_encoding_space.py --check` | ✅ pass (`closed`) | `747 forms; 711 mnemonics; canonical/overlap/field/uop and all generator drift checks passed` |
| libc-spec | glibc, musl, canonical CRT, and SPEC runtime matrix | yes | no | `libc` | `tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`blocked-after-linux-hard-break`) | `Not run after the required BusyBox/Linux gate failed` |
| linux | BusyBox rootfs boot after TSVC closure | yes | no | `linux` | `python3 kernel/linux/busybox_rootfs/boot.py --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --timeout 120` | ❌ fail (`linux-mmu-no-uart`) | `Two explicit clean-QEMU attempts produced no UART output within 120 seconds` |
| model | Cycle model and LinxCoreModel full matrix | yes | no | `model` | `tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`deferred-after-runtime-hard-break`) | `Leaf compile/parity checks passed; full superproject matrix not run after BusyBox failure` |
| nightly | Same-manifest PR/nightly closure | yes | no | `superproject` | `python3 tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`blocked-required-gates-red`) | `Not run because BusyBox`; `MMU TTBR`; `HL SDIP`; `semantic breadth`; `and downstream matrices remain open` |
| qemu | Canonical ISA executable semantic breadth | yes | no | `qemu` | `python3 tools/bringup/report_qemu_isa_coverage.py --qemu-root emulator/qemu --require-full` | ⚠ partial (`coverage-gap`) | `620/711 mnemonics and 625/747 encoding-signature forms have source-backed QEMU implementation evidence; remaining 90 V.* plus XB` |
| qemu | Canonical opcode metadata and reserved encodings | yes | no | `qemu` | `python3 tools/bringup/check_qemu_opcode_meta_sync.py --strict` | ✅ pass (`closed`) | `strict opcode meta/id audit passed; unexpected decode-only=0; unexpected metadata-only=0` |
| qemu | Full architecture validation suite on clean explicit QEMU | yes | no | `qemu` | `QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 bash avs/qemu/run_tests.sh --all --timeout 10` | ✅ pass (`closed`) | `clean QEMU 97b08e4b67f: all selected AVS suites PASS; strict system provenance and semantic suite PASS` |
| qemu | HL SDIP directed semantic execution | yes | no | `qemu` | `python3 avs/qemu/run_tests.py --suite loadstore --require-test-id 0xC140 --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --timeout 20` | ✅ pass (`hl-sdip-directed-pass`) | `clean QEMU 97b08e4b67f: Test 0x0000C140 PASS; ELF contains hl.sdip` |
| qemu | MMU TTBR directed boot | yes | no | `qemu` | `QEMU_BIN=/tmp/linx-qemu-clean-build/qemu-system-linx64 LLVM_BUILD=compiler/llvm/build-linxisa-clang bash emulator/qemu/scripts/linxisa/run-mmu-ttbr-basic.sh` | ✅ pass (`et-rel-loader-abi-aligned`) | `clean QEMU 97b08e4b67f: current ET_REL HI20/LO12/R64 path PASS; RELATIVE and GOT HI/LO unsupported-type regressions PASS` |
| rtl | LinxCore RTL full regression | yes | no | `rtl` | `tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`deferred-after-runtime-hard-break`) | `Leaf decode parity and microarchitecture tests passed; full nightly RTL gate not run` |
| runtime | TSVC monolithic all-mode diagnostic | no | no | `runtime` | `python3 workloads/tsvc/run_tsvc.py --all-modes --timeout 240 ...` | ⚠ partial (`nonrequired-scaling-diagnostic`) | `off completed 151/151; monolithic mseq reached 94/151 before process timeout; isolated s316 mseq passed; required batched lane is green` |
| runtime | TSVC required batched auto-vector hard break | yes | no | `runtime` | `python3 workloads/tsvc/run_tsvc_batched.py --batch-size 20 --strict-fail-under 151 --vector-mode auto --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64` | ✅ pass (`closed`) | `8/8 batches; 151/151 vectorized and completed; 10.587 seconds; zero failed batches` |
| sail | Architectural semantic completeness | yes | no | `isa` | `python3 tools/isa/sail_coverage.py --check` | ⚠ partial (`semantic-subset`) | `decode-only=0; executable-subset=747; architecturally-complete=0; no subset form is claimed complete` |
| sail | Pinned parser, typecheck, decode coverage, directed semantics, and C backend | yes | no | `isa` | `opam exec --switch=sail-4.14.3 -- python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend` | ✅ pass (`closed`) | `Sail 0.20.2; 747/747 form IDs; parser/typecheck/directed tests/C backend passed` |
| topology | Fresh shallow recursive clone and exact clean gitlinks | yes | no | `superproject` | `git clone --depth=1 --shallow-submodules --recurse-submodules ... && bash tools/ci/check_repo_layout.sh` | ✅ pass (`closed`) | `Fresh /tmp clone reached all published top-level pins and nested QEMU pins; no +/-/U gitlinks; layout policy passed` |
