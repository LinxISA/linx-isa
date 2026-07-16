# Bring-up Gate Status (Canonical)

This file is generated from `docs/bringup/gates/latest.json` via `python3 tools/bringup/gate_report.py render`.

Last generated (UTC): `2026-07-16 19:29:08Z`

## Lane `pin` (`2026-07-15-v0565-maintenance`)

- Timestamp (UTC): `2026-07-15 16:07:03Z`
- Profile: `release-strict`
- Lane policy: `pin-only`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `785d1b51ecc2042a94873665ec4b745d85473504` (`${LINXISA_ROOT}/lib/glibc`)
  - `linux`: `1d79efccf6b41bc675342e1b283b5ffd55f474a4` (`${LINXISA_ROOT}/kernel/linux`)
  - `linx-isa`: `f6a70f128404399a85fe3289ad85d6ec0ffb5fa8` (`${LINXISA_ROOT}`)
  - `linx-skills`: `39ef2773a6cbffc87f628d010e95f0abb162efb4` (`${LINXISA_ROOT}/skills/linx-skills`)
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
| linux | BusyBox rootfs boot after TSVC closure | yes | no | `linux` | `O=/tmp/fishtoucher-torvalds-linux-build KERNEL=/tmp/fishtoucher-torvalds-linux-build/vmlinux ROOTFS_IMG=/tmp/fishtoucher-cerf-rootfs-out/rootfs.ext2 QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 SKIP_BUILD=1 python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py` | ⚠ partial (`provisional-pass-source-incomplete`) | `Exploratory kernel reached userspace in 3.17s; BusyBox primary attempt passed with timer IRQ 30->34`; `Not reproducible from Linux SHA: 13 required local .S sources are ignored/untracked; blocked by LinxISA/linux#24` |
| model | Cycle model and LinxCoreModel full matrix | yes | no | `model` | `tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`deferred-after-runtime-hard-break`) | `Leaf compile/parity checks passed; full superproject matrix not run after BusyBox failure` |
| nightly | Same-manifest PR/nightly closure | yes | no | `superproject` | `python3 tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`blocked-required-gates-red`) | `Not run because BusyBox`; `MMU TTBR`; `HL SDIP`; `semantic breadth`; `and downstream matrices remain open` |
| qemu | Canonical ISA L1 decoder/source mapping breadth | yes | no | `qemu` | `python3 tools/bringup/report_qemu_isa_coverage.py --qemu-root emulator/qemu --require-full` | ⚠ partial (`coverage-gap`) | `L1 decoder/source mapping is 620/711 mnemonics and 625/747 forms; L2 runtime execution and L3 semantic-oracle counts are unavailable` |
| qemu | Canonical opcode metadata and reserved encodings | yes | no | `qemu` | `python3 tools/bringup/check_qemu_opcode_meta_sync.py --strict` | ✅ pass (`closed`) | `strict opcode meta/id audit passed; unexpected decode-only=0; unexpected metadata-only=0` |
| qemu | Full architecture validation suite on clean explicit QEMU | yes | no | `qemu` | `QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 bash avs/qemu/run_tests.sh --all --timeout 10` | ✅ pass (`closed`) | `clean QEMU 97b08e4b67f: all selected AVS suites PASS; strict system provenance and semantic suite PASS` |
| qemu | HL SDIP directed semantic execution | yes | no | `qemu` | `python3 avs/qemu/run_tests.py --suite loadstore --require-test-id 0xC140 --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --timeout 20` | ✅ pass (`hl-sdip-directed-pass`) | `clean QEMU 97b08e4b67f: Test 0x0000C140 PASS; ELF contains hl.sdip` |
| qemu | MMU TTBR directed boot | yes | no | `qemu` | `QEMU_BIN=/tmp/linx-qemu-clean-build/qemu-system-linx64 LLVM_BUILD=compiler/llvm/build-linxisa-clang bash emulator/qemu/scripts/linxisa/run-mmu-ttbr-basic.sh` | ✅ pass (`et-rel-loader-abi-aligned`) | `clean QEMU 97b08e4b67f: current ET_REL HI20/LO12/R64 path PASS; RELATIVE and GOT HI/LO unsupported-type regressions PASS` |
| rtl | LinxCore RTL full regression | yes | no | `rtl` | `tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`deferred-after-runtime-hard-break`) | `Leaf decode parity and microarchitecture tests passed; full nightly RTL gate not run` |
| runtime | TSVC monolithic all-mode diagnostic | no | no | `runtime` | `python3 workloads/tsvc/run_tsvc.py --all-modes --timeout 240 ...` | ⚠ partial (`nonrequired-scaling-diagnostic`) | `off completed 151/151; monolithic mseq reached 94/151 before process timeout; isolated s316 mseq passed; required batched lane is green` |
| runtime | TSVC required batched auto-vector hard break | yes | no | `runtime` | `CLANG=compiler/llvm/build-linxisa-clang/bin/clang QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 python3 workloads/tsvc/run_tsvc_batched.py --batch-size 20 --strict-fail-under 151 --vector-mode auto` | ✅ pass (`closed`) | `Current LLVM 7eee9db and clean QEMU 97b08e4: 8/8 batches; 151/151 vectorized and completed; 13.786 seconds` |
| runtime | ctuning Milepost freestanding C sentinel | no | no | `runtime` | `LINX_VIRT_TEST_FINISHER=1 python3 workloads/ctuning/run_milepost_codelets.py --target linx64-linx-none-elf --run --limit 5` | ✅ pass (`nonrequired-current-sha-sentinel`) | `Current LLVM 7eee9db and clean QEMU 97b08e4: selected=5 passed=5 failed=0; corpus a7136ec8` |
| sail | Architectural semantic completeness | yes | no | `isa` | `python3 tools/isa/sail_coverage.py --check` | ⚠ partial (`semantic-subset`) | `decode-only=0; executable-subset=747; architecturally-complete=0; no subset form is claimed complete` |
| sail | Pinned parser, typecheck, decode coverage, directed semantics, and C backend | yes | no | `isa` | `opam exec --switch=sail-4.14.3 -- python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend` | ✅ pass (`closed`) | `Sail 0.20.2; 747/747 form IDs; parser/typecheck/directed tests/C backend passed` |
| topology | Fresh shallow recursive clone and exact clean gitlinks | yes | no | `superproject` | `git clone --depth=1 --shallow-submodules --recurse-submodules ... && bash tools/ci/check_repo_layout.sh` | ✅ pass (`closed`) | `Fresh /tmp clone reached all published top-level pins and nested QEMU pins; no +/-/U gitlinks; layout policy passed` |

## Lane `pin` (`2026-07-17-fishtoucher-dev`)

- Timestamp (UTC): `2026-07-16 19:29:08Z`
- Profile: `dev`
- Lane policy: `pin-only`
- Trace schema version: `1.0`
- SHA manifest:
  - `glibc`: `785d1b51ecc2042a94873665ec4b745d85473504` (`${LINXISA_ROOT}/lib/glibc`)
  - `linux`: `90834082e829771ce29392e3be12ad2dc6d38716` (`${LINXISA_ROOT}/kernel/linux`)
  - `linx-isa`: `33304d81c8811f403be5dc698789a6b31fa59c8e` (`${LINXISA_ROOT}`)
  - `linx-skills`: `6a1007379be984d4eed9ba297e8541168bb0f9b5` (`${LINXISA_ROOT}/skills/linx-skills`)
  - `linxcore`: `5ecec7b9608de674738327f83e126ca7e9b31b16` (`${LINXISA_ROOT}/rtl/LinxCore`)
  - `linxcore-model`: `3bc1e6e2ceb2d578204013220cb14f67043c8eb7` (`${LINXISA_ROOT}/tools/LinxCoreModel`)
  - `llvm`: `b3ff7eee5cd091e04d292db781fd4d33980f3629` (`${LINXISA_ROOT}/compiler/llvm`)
  - `mesa3d`: `11c1663090d31ee744059281c4fa8f347e10e023` (`${LINXISA_ROOT}/lib/mesa3d`)
  - `model`: `e535af57b563cc3da0f1c9d3ae9c36be7d0dccec` (`${LINXISA_ROOT}/tools/model`)
  - `musl`: `4ab3c65fc33279c4004f9821bebdd87e19f87c21` (`${LINXISA_ROOT}/lib/musl`)
  - `pto-kernels`: `43e606b6c90d8ffbc939f4f23c70fcc8b37080f0` (`${LINXISA_ROOT}/workloads/pto_kernels`)
  - `ptoas`: `939e9e0fe1a3a2349207e36d848fc6232faa135c` (`${LINXISA_ROOT}/compiler/ptoas`)
  - `pycircuit`: `1d7b6fcf42c0b59bb2c5b5bced220df90fb0f54f` (`${LINXISA_ROOT}/tools/pyCircuit`)
  - `qemu`: `107cb00916f6cf3c30de6610a2a4ab36fc312511` (`${LINXISA_ROOT}/emulator/qemu`)
  - `supernpu-bench`: `497cf3f7ebf7c5c18c707b82481e2285d0b0e07f` (`${LINXISA_ROOT}/workloads/SuperNPUBench`)

| Domain | Gate | Required | Waived | Owner | Command | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| compiler | LLVM current-SHA mnemonic and C-CodeGen breadth | yes | no | `compiler` | `TARGET=linx32/linx64 avs/compiler/linx-llvm/tests/run.sh && report_llvm_c_codegen_coverage.py` | ✅ pass (`current-sha-codec-measured`) | `LLVM b3ff7eee; strict roundtrip=746/746; mnemonic breadth=710/710; pure C-CodeGen alias-closed=143/710; docs/bringup/gates/llvm_c_codegen_coverage_latest.json` |
| integration | ISA-LLVM-QEMU coverage closure | yes | no | `superproject` | `python3 tools/bringup/report_isa_llvm_qemu_coverage.py` | ❌ fail (`blocked-qemu-l1-form-gap`) | `ISA reserved-selector contract and LLVM/translation inventories are closed; QEMU L1 still misses the same issue-owned 91 legal forms; docs/bringup/gates/isa_llvm_qemu_coverage_latest.json` |
| isa | v0.56 legal selector and reserved-form contract | yes | no | `isa` | `tools/isa/test_golden_contract.py && tools/isa/validate_spec.py && avs/compiler/linx-llvm/tests/run.sh` | ✅ pass (`reserved-selector-contract-closed`) | `746 legal forms; 710 legal mnemonics; TMA Function 3..31 tracked as one reserved family with 29 values; 928 raw words reject; strict LLVM=746/746; LinxISA/linx-isa#152` |
| libc | musl phase-b static and shared runtime diagnostics | no | no | `libc-validation` | `run_musl_smoke.py --sample all --link static/shared` | ✅ pass (`out-of-order-diagnostic-pass`) | `static 16/16 runtime_pass; shared 16/16 runtime_pass; runtime_diagnostic_summary.json` |
| libc-spec | SPECint train matrix and focused speed-stack diagnostic | no | no | `spec-performance` | `run_stage_qemu_matrix.py --stage b --input-set train` | ❌ fail (`train-matrix-incomplete-live-timeout`) | `1/10 strict completion; 9 live-timeouts; 999 strict hash PASS; 523 300s=47B; 523 900s=130B and specdiff incomplete; runtime_diagnostic_summary.json` |
| linux | Current kernel smoke full boot and BusyBox rootfs | no | no | `linux-validation` | `smoke.py && full_boot.py && busybox_rootfs/boot.py` | ✅ pass (`out-of-order-diagnostic-pass`) | `BusyBox PASS in 3.174s; timer IRQ 31->36; rootfs preserved; runtime_diagnostic_summary.json` |
| nightly | Same-manifest nightly closure | yes | no | `superproject` | `python3 tools/bringup/run_benchmark_linux_flow.py --profile nightly` | ⏸ not_run (`blocked-at-qemu-l1-closure`) | `ISA issue #152 is fixed; nightly remains blocked by QEMU L1 655/746 with 91 issue-owned forms missing; downstream Linux/workload results remain diagnostics until the hard break closes` |
| qemu | AVS translation inventory | yes | no | `isa-validation` | `python3 tools/bringup/report_qemu_translation_coverage.py --require-full` | ✅ pass (`translation-inventory-complete`) | `710/710 mnemonics from current LLVM b3ff7eee objects; docs/bringup/gates/qemu_translation_coverage_latest.json` |
| qemu | Canonical ISA L1 decoder/source mapping breadth | yes | no | `qemu` | `python3 tools/bringup/report_qemu_isa_coverage.py` | ❌ fail (`coverage-gap`) | `QEMU 107cb009; L1=624/710 mnemonics and 655/746 legal forms; 91 forms missing; reserved TMA family excluded from denominator; docs/bringup/gates/qemu_isa_coverage_latest.json` |
| qemu | Executable semantic evidence subset | no | no | `qemu-validation` | `python3 tools/bringup/report_qemu_executable_coverage.py --require-nonzero --require-clean` | ✅ pass (`partial-l2-l3-subset`) | `QEMU 107cb009; current-SHA L2=60 forms; L3=60 forms; rejected=0; does not extend the incomplete L1 claim` |
| runtime | CoreMark Dhrystone and PolyBench MINI diagnostics | no | no | `workload-validation` | `run_benchmarks.py && run_polybench.py -DMINI_DATASET` | ✅ pass (`out-of-order-diagnostic-pass`) | `CoreMark RUN_PASS; Dhrystone RUN_PASS; gemm PASS; jacobi-2d PASS; runtime_diagnostic_summary.json` |
| runtime | TSVC differential and full batched diagnostics | no | no | `compiler-validation` | `run_tsvc_batched.py --strict-fail-under 150` | ✅ pass (`out-of-order-diagnostic-pass`) | `8/8 batches; 151/151 completed; 150 strict-lowered; s451 checksum mismatch=0; runtime_diagnostic_summary.json` |
