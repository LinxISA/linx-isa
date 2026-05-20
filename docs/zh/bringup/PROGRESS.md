# 显示进度（v0.56 工作区）

最后更新: 2026-04-25

## 关闭快照- `v0.56` 黄金/规格是规范且经过验证的。
- AVS 现在是唯一实时公开的培育合同。
- 最新签入的规范报告是 `2026-04-18 02:11:34Z` 生成的 `docs/bringup/gates/latest.json`；其最新运行是`2026-04-18-r9-pin-linuxlibc-refresh`。
- 主动治理阶段仍然是`G0`，并且`docs/bringup/agent_runs/waivers.yaml`仍然具有零豁免。
- 最新的 pin-lane 运行恢复了架构、编译器、模拟器、Linux `vmlinux`、initramfs Smoke/full boot、musl build/runtime、glibc G1a/G1b/runtime、灵犀Core/Testbench/Trace/pyCircuit leaf PR 门以及工作负载基准/polybench/portfolio/ctuning/PTO/TSVC 编译行。
- 2026 年 4 月 11 日抽查首次清除了陈旧的 March Sail/PTO 诊断； 4 月 18 日的规范报告现在将模型差异和 PTO 奇偶校验记录为绿色。
- 2026 年 4 月 18 日规范恢复工作关闭了陈旧的 PR 通道拦截器：
  - `python3 tools/bringup/check_avs_profile_closure.py --tier pr` 现在与 `required_tests=31` 一起为绿色。
  - `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json` 恢复兼容性包装后再次通过。
  - 规范的 `strict_cross_repo.sh` 行仍然失败，因为它包含所需的 BusyBox rootfs 门；没有 BusyBox 拦截器的临时直接重播并不是发布证据。
  - 阻塞引脚通道的 灵犀Core/Testbench/Trace/pyCircuit 叶回归再次在本地变为绿色：`test_runner_protocol.sh`、`test_trace_schema_and_mem.sh`、`test_konata_sanity.sh`、`test_cosim_smoke.sh`、`run_linx_cpu_pyc_cpp.sh` 和 `run_linx_qemu_vs_pyc.sh` 现在通过。
  - 固定的 `vmlinux` 构建门通过 `tools/bringup/run_linux_vmlinux_build_clean.sh` 再次变为绿色，并且引脚通道现在在 `tools/bringup/run_qemu_build_clean.sh` 中有一个匹配的干净 QEMU 帮助程序，因此运行时收敛不再依赖于脏模拟器工作树。- 当前的活跃拦截器现在集中在 Linux/用户空间运行时和夜间/运行时范围：
  - AVS 夜间宽度仍然是 `32/54` 已实施/通过。
  - BusyBox rootfs 运行时是刷新的 PR pin 通道中唯一剩余的必需叶子拦截器。
  - `musl` 和 `glibc` 运行时烟雾都再次通过干净固定的 QEMU 路径；过时的 `r8` 故障被 `r9` 重新运行所取代。
- BusyBox rootfs 仍然是活跃的 Linux 运行时拦截器，但重建内核路径再次向前推进：合并的 灵犀64 QEMU 恢复通道需要无固件启动 (`-bios none`)，`kernel/linux/tools/linxisa/busybox_rootfs/boot.py` 在本地与该通道对齐，仓库内集成汇编器现在接受 灵犀 `.option push/pop/norelax` 加上之前阻止 `arch/linx/include/asm/bug.h` 的 `.word/.half/.dword` 指令和本地后续操作还清除了早期的 SMP/VDSO/page-table/uaccess/ptrace/MM 兼容性不匹配，这些不匹配一直在 灵犀 架构代码中阻止 `vmlinux`。当前的重建内核停止点不再是 灵犀 VDSO/MM/NFS 表面：本地对象范围的 向量izer 解决方法使构建经历了早期的 `fs/nfs` 和 `fs/lockd` SelectionDAG 崩溃以及后续的 `lib/random32.o` 崩溃。最新验证的第一站是 `-O2` 下的 `lib/hexdump.o` (`hex_to_bin`) 中的相同 灵犀 后端崩溃系列。
  - `Regression::strict_cross_repo.sh` 是红色的，因为 BusyBox rootfs 在规范运行中是红色的。- SPEC Stage A 仍然是夜间/运行时阻止程序（`___slab_alloc` 中的 `9p` 内核 `E_BLOCK`；initramfs 子启动仍然损坏）。
  - TSVC QEMU 运行时在 `auto` 模式下的 标量 重放循环内核上仍然是夜间/运行时阻止程序； PR 闭包在 `148/151` 处使用仅编译严格覆盖。
  - 一些调用/ret 负契约和 C++ 运行时覆盖后续工作仍然在 PR 闭包子集之外。

## 阶段状态

|相|状态 |证据|
| --- | --- | --- |
| 1.Canonical `v0.56` 金色+手动冻结 | ✅ 通过 | `python3 tools/isa/build_golden.py --profile v0.56 --check`; `python3 tools/isa/validate_spec.py --profile v0.56` |
| 2. AVS公共合约割接 | ✅ 来源完整 | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| 3. LLVM MC/CodeGen 基线对齐 | ✅ 当前密码 | `avs/compiler/linx-llvm/tests/run.sh`; `analyze_coverage.py --fail-under 100`; `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| 4. QEMU 运行时/系统基线 | ✅ 当前密码 | `avs/qemu/check_system_strict.sh`； `avs/qemu/run_tests.sh --all`; `ninja -C emulator/qemu/build qemu-system-linx64` |
| 5. Linux用户空间启动路径| ⚠️ 恢复正在进行中 | Initramfs 冒烟/满保持绿色。 BusyBox rootfs 需要在合并的 灵犀64 通道上进行无固件 QEMU 启动，并且本地重建工作已经超越了旧的 `bug.h` 内联 asm 阻止程序、早期的 SMP/VDSO 冲突、最初的 灵犀 vDSO 干净构建失败、第一个 灵犀 MM/核心 API 漂移、 `fs/nfs` SelectionDAG 崩溃，`fs/lockd` SelectionDAG 崩溃，以及后续的 `lib/random32.o` 崩溃。当前的停止是稍后在 `lib/hexdump.o` 处的编译器后端稳定性中进行的，然后才能链接新的 `vmlinux`。 |
| 6. musl/glibc 基线运行时 | ✅ 当前的 clean-QEMU 通行证 | musl build/runtime 和 glibc G1a/G1b 是绿色的，`run_musl_smoke.py` 和 `run_glibc_smoke.py` 现在再次通过干净的固定 QEMU 路径。 |
| 7. 帆/模型验证 | ✅ 目前的 PR 通行证 |旧的 March Sail 解码生成器故障已被取代；目前PR车道记录model-diff为绿色，4月11日抽查`check_sail_model.py --require-parser`和`gen_sail_decode.py --check`均通过。 |
| 8. AVS 层关闭 | ✅ 目前的 PR 通行证 | `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr`现报告`required_tests=31`、`failure_count=0`；夜间宽度仍然是`32/54`。 |
| 9. 灵犀Core/Testbench/Trace/pyCircuit 关闭 | ✅ 当前密码 |运行程序协议、跟踪模式/内存烟雾、灵犀Trace 健全性、cosim 烟雾、ROB 簿记、块结构 pyc 流和 pyCircuit CPU/QEMU 烟雾在最新的规范引脚运行中传递。 |
| 10.工作量和SPEC硬闭合| ❌ 夜间/运行时拦截器 | Benchmark/PolyBench/portfolio/ctuning 工件发布、PTO 内核奇偶校验和 TSVC 仅编译 PR 覆盖范围在 PR 通道中为绿色，但 SPEC 阶段 A 仍然依赖于托管共享 musl 打包以及相同的后期 Linux 用户空间通道，并且 TSVC QEMU 运行时仍然单独受阻。 |

## 门快照

|门 |状态 |命令 |
| --- | --- | --- |
|黄金/规格验证 | ✅ | `python3 tools/isa/build_golden.py --profile v0.56 --check`; `python3 tools/isa/validate_spec.py --profile v0.56` |
| AVS 合约架构 | ✅ | `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml` |
| AVS矩阵状态审计| ✅ | `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json` |
| AVS 层关闭 | ✅ PR 子集绿色（需要 `31/31`）| `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr` |
|严格封闭的航行/模型路径| ⚠️ 陈旧的三月失败；需要重新运行 | `tools/isa/gen_sail_decode.py`的2026年3月15日报告中止，但`python3 tools/bringup/check_sail_model.py --require-parser`和`python3 tools/isa/gen_sail_decode.py --check`的2026年4月11日抽查均通过。 |
|编译器AVS (`linx64`/`linx32`) | ✅ | `./avs/compiler/linx-llvm/tests/run.sh` |
|编译器覆盖率（`linx64`/`linx32`）| ✅ | `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --fail-under 100` |
| LLVM辅助工具套件(`llvm-ar`/`llvm-nm`/`llvm-readelf`/`llvm-strip`) | ✅ | `ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf` |
| QEMU 运行时套件 | ✅ 当前密码 | `./avs/qemu/run_tests.sh --all` |
| QEMU 固定二进制构建 | ✅ | `ninja -C emulator/qemu/build qemu-system-linx64` |
| QEMU 解码覆盖率 | ❌ 开放工作 | `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full` |
| Linux `vmlinux` 构建关闭 | ✅ 当前辅助路径通过 | `bash tools/bringup/run_linux_vmlinux_build_clean.sh --linux-root $PWD/kernel/linux --out-dir $PWD/kernel/linux/build-linx-fixed --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang --gmake /opt/homebrew/bin/gmake --target vmlinux` |
| Linux initramfs 烟雾/完整 | ✅ | `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`； `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py` |
| musl 构建关闭 (`phase-b`) | ✅ | `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh` |
| musl 运行时 (`R1`/`R2`) | ✅ | `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both` |
| glibc (`G1a`/`G1b`) | ✅ | `bash lib/glibc/tools/linx/build_linx64_glibc.sh`； `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh` |
| Linux/QEMU 上的 glibc 动态运行时 | ✅ 当前的 clean-QEMU 通行证 | `python3 avs/qemu/run_glibc_smoke.py --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --timeout 30` |

## 当前关闭阻止程序- 在签入的规范报告中，PR 恢复通道几乎关闭； BusyBox rootfs 是剩余所需的失败叶行。
- `Library::glibc runtime dynamic hello` 在最新的规范运行中是绿色的。
- 灵犀Core/Testbench/Trace/pyCircuit 叶子拦截器在最新的规范运行中被清除，使 BusyBox rootfs 成为 `strict_cross_repo.sh` 变绿之前唯一需要的叶子拦截器。
- BusyBox rootfs 在 Python 包装器中不再失败；现在，即使针对干净固定的 QEMU 构建，它也始终会公开真实的内核 `E_BLOCK`，并且干净工作树 `switch_to` 实验会删除 EBARG 上下文保存/恢复，仅在详细引导下才到达 BusyBox shell。因此，剩余的错误位于 Linux 运行时路径中，而不是包装器或脏模拟器工件中。
- `Regression::strict_cross_repo.sh` 在 `2026-04-18-r9-pin-linuxlibc-refresh` 中保持红色，因为它包含 BusyBox rootfs 故障。
- SPEC 阶段 A 仍然是选择加入 PR 门背后的真正运行时阻碍因素：该通道现在应该默认使用无固件 QEMU 启动，但它仍然在托管 `phase-c` 共享 musl 打包（`libc.so` 不存在）和当前阻止 BusyBox 验证的相同后期 Linux 用户空间/rootfs 运行时路径上受到阻止。
- TSVC QEMU 运行时仍然是夜间/运行时阻止程序； PR 通道仅持有 `148/151` 的仅编译严格覆盖合约。

## 规范之门文物- `avs/linx_avs_v1_test_matrix.yaml` 是公共合约源。
- `avs/linx_avs_v1_test_matrix_status.json` 是规范的 AVS 状态工件。
- `docs/bringup/gates/qemu_isa_coverage_latest.json` 记录最新签入的 QEMU 解码覆盖率快照，包括助记符和执行形式间隙。
- `docs/bringup/gates/latest.json` 是当前每次运行的多门证据神器；最新签入的刷新是 `2026-04-18-r9-pin-linuxlibc-refresh`，尚未发布证据，因为 BusyBox rootfs 和聚合严格交叉行仍然失败。