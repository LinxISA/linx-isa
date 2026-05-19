# 编译器/LLVM 清单

## 关闭类别

### 标量

- 状态：主动关闭车道
- 范围：
  - `avs/compiler/linx-llvm/tests/run.sh` 发出的通用独立 C
  - 源工作负载中没有显式 SIMT autovec 扩展表面
  - 直接返回 `CALL` 块头 必须保持源级熔断 (`..., ra=...`)
- 当前证据：
  - `LLVM-001` 和 `LLVM-002`
  - 调用/返回重定位+`avs/compiler/linx-llvm/tests/run.sh`中的模板检查
  - `avs/runtime/freestanding/src/crt0.s` 中的 标量 运行时启动 asm
- 剩余的 标量 特定间隙：
  - 手写融合 `ICALL ra=` 源语法尚未在
    当前分支，因此间接调用合约测试仍然使用显式相邻
    `setret/c.setret`

### SIMT

- 状态：仅部分/启动子集
- 范围：
  - LLVM SIMT autovec、分组车道发射编队、块体-本地 `p` 控制、
    和仅运行时证明的子集
- 规范状态文档：
  - `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`
  - `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`
- 剩余间隙：
  - 需要架构执行掩码保存/恢复的分组不同区域
    仍然在封闭编译器子集之外

### 瓷砖

- 状态：MC/asm 表面存在；未声明通用 C 闭包
- 范围：
  -tile/TEPL 操作码编码、汇编器/反汇编器拼写和手册
    同步
- 当前证据：
  - `LLVM-003`
  - AVS 套件中的 `41_v056_isa_forms.s` 编译/objdump 覆盖范围
- 剩余间隙：
  -tile/CUBE/TEPL循环体仍然在通用SIMT编译器之外
    子集并且不是 标量 闭包的一部分- [x] ID：LLVM-001 构建固定工具链并为当前编译器分支注册的目标传递活动的裸机 AVS 编译套件。
  命令：`cd avs/compiler/linx-llvm/tests && CLANG=compiler/llvm/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh`
  完成意味着：当前编译器分支中每个所需的活动裸机目标都可以干净地编译，并且日志存档在活动门运行目录下。实时编译器未注册的存档目标不是当前所需闭包的一部分。
  状态： ✅ 通过 (2026-05-14) - Bisheng LLVM `631961c3988f` 通过工作空间内 `linx64` AVS 编译套件。该分支中的 `clang --print-targets` 仅寄存器 `linx64`/`linx64be`，因此 `linx32` 不再是活动裸机栅极表面的一部分。

- [x] ID：LLVM-002 验证活动裸机 AVS 输出的助记符覆盖率保持在 100%。
  命令：`python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100`
  完成意味着：每个所需的活动裸机目标都报告 100% 助记符覆盖率，没有丢失助记符。
  状态： ✅ PASS (2026-05-14) - `analyze_coverage.py --fail-under 100` 报告 `Coverage: 100.0%` 为 `out-linx64`（710/710 独特助记符）。不需要当前的 `linx32` 输出，因为分支不注册该目标。

- [x] ID：LLVM-003 确认 LLVM 中的规范 v0.56 TEPL 磁贴操作码与手册和其他使用者保持一致。
  命令：`python3 tools/bringup/check_tepl_encoding.py --root .`
  完成意味着：脚本返回 `OK` 并且不存在旧版 TEPL 编码。
  状态：✅ 通过 (2026-02-23) - `check_tepl_encoding.py` 返回 `OK`（日志：`docs/bringup/gates/logs/2026-02-23-r2-pin-reassess/pin/compiler_tepl.log`）。- [x] ID：LLVM-004 当运行时门需要时，为目标模式重建 C++ 运行时覆盖。
  命令：`bash tools/build_linx_llvm_cpp_runtimes.sh --profile spec --mode phase-c`
  完成意味着：运行时覆盖工件存在于 sysroot 中并且可链接。
  状态：✅ 通过 (2026-02-23) - C++ 运行时覆盖构建以 `ok: ZXTERMEN45QXZ C++ runtimes ready` 完成（日志：`docs/bringup/gates/logs/2026-02-23-r2-pin-reassess/pin/compiler_cpp_runtime_phasec.log`）。

- [x] ID：LLVM-005 记录 LLVM 更改的提交 SHA 和子模块碰撞证据。
  完成意味着：SHA 在门报告通道清单中捕获并在变更注释中引用。
  状态：✅ PASS (2026-02-25) - 严格运行 `2026-02-25-r2-pin-lanefix` 捕获 `docs/bringup/gates/latest.json` (`runs[-1].sha_manifest.llvm.sha`) 中的 LLVM SHA 并在 `docs/bringup/GATE_STATUS.md` 中渲染通道清单。

- [x] ID：LLVM-006 保持固定工具构建足够完整，以便 Linux/libc 关闭。
  命令：`ninja -C compiler/llvm/build-linxisa-clang llvm-ar llvm-nm llvm-strip llvm-readelf`
  完成意味着：内核/libc 集成所需的辅助 LLVM binutils 出现在固定的 `clang` 和 `ld.lld` 旁边。
  状态： ✅ 通过 (2026-03-08) - 针对固定 LLVM `e6ce4b78faaa` 就地重建辅助工具，生成 `compiler/llvm/build-linxisa-clang/bin/llvm-ar`、`llvm-nm`、`llvm-readelf` 和 `llvm-strip`。- [ ] ID：LLVM-007 在融合的 `BSTART ... , ra=...` 上保留 标量 直接调用源关闭。
  命令：`cd avs/compiler/linx-llvm/tests && CLANG=compiler/llvm/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=avs/compiler/linx-llvm/tests/out-linx64 ./run.sh`
  完成意味着：标量 直接调用源和手写启动 asm 使用融合的 `ra=` 调用 块头，而对象级重定位检查仍然接受降低的相邻 `setret` 对。
  状态： ✅ 通过 (2026-05-15) - `run.sh` 在将 标量 手写直接调用转换为融合的 `BSTART.STD CALL, ..., ra=...` 源语法后通过。重定位/模板门仍然通过呼叫/返回 AVS 通道，包括 `18_setret_relax`、`33`-`40` 和 `41_v056_isa_forms`。