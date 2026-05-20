# 对齐矩阵

该矩阵跟踪当前工作空间范围内的跨域对齐。

|主题 |规格|编译器|模拟器|内核|型号|证据|
| --- | --- | --- | --- | --- | --- | --- |
| 灵犀 Linux libc ABI + 重定位合约（`EM_LINXISA`、`R_LINX_*`、`setjmp/signal/ucontext`）| ✅ ABI 指南/清单 + musl/glibc 块头 同步 | ✅ 工作区 clang 调用/ret 重定位+模板门通行证（`FENTRY/FRET.STK` 与 Musttail `FENTRY/FEXIT`）| ✅ 严格通道运行时门通行证（musl 运行时 + glibc G1b + 严格系统 + 模型差异）| ✅ 烟雾/已满/busybox/virtio-disk 启动门通过 | ✅ qemu-vs-pyc 提交差异传递 | `docs/bringup/gates/latest.json`; `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/lib_musl_both.log`; `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/lib_glibc_g1b.log`; `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/model_diff_suite.log` |
|区块/描述符合约 (`B.ARG/B.IOR/B.IOT/C.B.DIMI`) | ✅ 手册 + 生成的参考 | ✅ 描述符发射/测试 | ✅ 描述符执行 + AVS 门 | ✅ 用户空间启动未回归 | ✅ 跟踪兼容的启动子集 | `bash tools/regression/run.sh` |
| ACR/IRQ/异常 正确性 | ✅ 特权章+陷阱表| ✅ MC 符号 + 编码 | ✅ 严格的系统测试 | ✅ 烟/全/virtio 靴子通行证 | ✅ qemu-vs-pyc 提交差异传递 | `avs/qemu/check_system_strict.sh` |
| ISA 目录奇偶校验 (`v0.56`) | ✅ 黄金 + 当前 json | ✅ 编译覆盖率测试 | ✅ 解码/执行门 | ✅ 没有过时的活动表面参考 | ✅ 模型方合同检查 | `python3 tools/isa/check_canonical_v056.py --root .` |
| ISA 广度跟踪（规范与 QEMU 实现）| ✅ 规范规格目录（`710` 独特助记符）| ✅ 对于已实现的工具链表面，编译/解除覆盖率保持 100% | ⚠ 映射的 QEMU 覆盖范围为 `524/710`（间隙作为工件进行跟踪，未放弃）| ✅ 内核运行时闭包保持绿色，同时广度逐渐扩展 | ✅ 模型套件仍然是必需的，并传递已实现的子集 | `docs/bringup/gates/qemu_isa_coverage_latest.json`； `docs/bringup/gates/qemu_isa_coverage_latest.md` |
| AVS 整合 | ✅ `avs/` 中维护的矩阵 | ✅ 在 `avs/compiler/linx-llvm/tests` 下编译测试 | ✅ `avs/qemu` 下的运行时测试 | ✅ 不适用 | ✅ 不适用 | `bash tools/ci/check_repo_layout.sh` |