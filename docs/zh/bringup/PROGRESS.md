# 启动进度（v0.58.3）

最后更新：2026-08-23

## 当前架构基线

- `isa/v0.58/linxisa-v0.58.json` 是规范 LinxISA catalog，共 723 个
  mnemonic、757 个合法 form。
- `isa/v0.58/pto-spec.lock.json` 固定已发布 PTO ISA v0.58.3 提交
  `e599a3d36ebfad43362ff591ea5e128816c684c7` 和编码投影
  `8a48b80e04484c70870f155bf9efc79d2a805cf99e809f4e4e8a7e6a7eb34172`。
- 语义执行单元只有 `VEC`、`SFU`、`TLSU`、`CUBE`；TEPL 只是 VEC/SFU
  的 Mode/Function 编码载体，不是执行单元。
- 在所有相关 gitlink 与 `docs/bringup/component-lock.v0.58.json` 原子更新到
  最终合入 SHA 之前，组件锁仍是发布阻塞项。

## 证据策略

只有绑定最终 v0.58.3 component lock 的新鲜证据可以晋级。历史
v0.57/v0.58.1 报告、旧 SHA、仅 trace 输出、等待项、跳过项和缺少工具的结果
都不算通过。生成的状态页只是视图，机器可读 lock 和新鲜 run summary 优先。

## 当前签入状态

| 表面 | 状态 | 当前证据 |
| --- | --- | --- |
| ISA catalog、Sail、PTO lock | 已验证 | Golden/catalog/manifest；Sail parser、定向语义、coverage、C backend；723/757 权威 |
| LLVM/LLD | 已合入 | `b7c83f68bf84125e696a70bec4b665c70a3b584d`；MC 55/55；linx32 759/759、linx64 723/723 compile AVS |
| QEMU | 集成中 | v0.58.3 基线及已审查 HL.LUI/CSEL 修复已合入；TLSU CPU-MMU PR 与 CUBE issue 75 尚未进入最终 pin |
| Linx-TileOP-API | 集成中 | 精确 API/link 门禁通过；PR 27 将 CUBE compute PadValue 修正为 PTO 要求的 Zero |
| PTOAS | 集成中 | PR 8 源码审查和本地门禁通过；合入前仍需刷新最终 TileOP pin 和托管交付任务 |
| Linux、glibc、musl | 叶仓已合入 | 精确 PTO 身份和最终 LLVM 的干净 `vmlinux` 构建通过；全系统 PTO workload 仍是发布门禁 |
| VECTOR/CUBE 首次使用 | 架构完成；Linux 默认关闭 | ISA/Sail/QEMU 执行前异常契约通过。跨 ACR EXTCTX ABI 在 root issue 182 与 Linux issue 32 定义前，Linux 保持 V/C 关闭 |
| Queue-wired model 与 PTO kernels | 叶仓已合入，等待 root repin | Model `eee8fd57`；pto-kernels `322443ef`；六个 CUBE 程序精确身份编译/链接通过 |
| 全系统 PTO CUBE | 进行中 | r8 已到 PID1、fork/exec、三个 TLOAD source 和合法 CUBE preflight；下一分歧由 QEMU issue 75 跟踪 |
| 更广的 nightly benchmark | 未关闭 | Nightly 广度与 release-strict 结果/身份门禁分开跟踪 |

## 规范命令

```bash
bash tools/ci/check_repo_layout.sh
python3 tools/ci/check_component_lock.py --root .
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/check_pto_v058_manifest.py --root .
python3 tools/isa/check_canonical_v058.py --root .
python3 tools/isa/check_agent_navigation.py --root .
python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend
make -C tools/Linx-TileOP-API check
python3 workloads/pto_kernels/scripts/check_supernpu_v058.py
python3 docs/check_documentation.py --root .
```

最终发布还要求精确 PTO CUBE 全系统门禁、新鲜 model/跨栈证据、最终 root head
托管检查全绿，以及审查 tree 与合入 tree 完全一致。
