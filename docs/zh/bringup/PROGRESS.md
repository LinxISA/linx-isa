# 启动进度（v0.58.6）

最后更新：2026-09-06

## 当前架构基线

- `isa/v0.58/linxisa-v0.58.json` 是规范 LinxISA catalog，共 744 个
  mnemonic、773 个合法 form。
- `isa/v0.58/pto-spec.lock.json` 固定已发布 PTO ISA v0.58.6 提交
  `dea0b75e803cffa873982c90f9aa0cd17c6d243b` 和编码投影
  `a757f2e50ec8050d2131b6b9ad38657511df80cf3f9424d5f009ea6e0cc35839`。
- 语义执行单元只有 `VEC`、`SFU`、`TLSU`、`CUBE`；TEPL 只是 VEC/SFU
  的 Mode/Function 编码载体，不是执行单元。
- `docs/bringup/component-lock.v0.58.json` 与相关 gitlink 已原子固定到
  当前分阶段 v0.58.3/v0.58.6 的已合入叶仓 SHA。

## 证据策略

只有绑定当前精确 component lock 的新鲜证据可以晋级。历史
v0.57/v0.58.1 报告、旧 SHA、仅 trace 输出、等待项、跳过项和缺少工具的结果
都不算通过。生成的状态页只是视图，机器可读 lock 和新鲜 run summary 优先。

## 当前签入状态

| 表面 | 状态 | 当前证据 |
| --- | --- | --- |
| ISA catalog、Sail、PTO lock | 已验证 | Golden/catalog/manifest；Sail parser、定向语义、coverage、C backend；744/773 权威 |
| LLVM/LLD | 已合入并重钉 | `3d79447f635b00feb68f5a6acaa2dae31dc43b7a`；PTO 0.58.6 投影身份及六套 Tile AVS 编译/运行通过；穷举 MC/编译证据仍按提交归属于 `b7c83f68bf84125e696a70bec4b665c70a3b584d` |
| QEMU | 叶仓已合入 | `bfd46ef40864cd3c0536c54722359e667babd8a1`；PTO 0.58.6 身份、精确解码覆盖、整数 GM 原子/归约与 Local TIMG2COL 门禁通过 |
| Linx-TileOP-API | 叶仓已合入 | `bd1ecca97ca47da0edc462c1ce19749c6940780e`；compute Zero、transport Null 契约通过 |
| PTOAS | 已合入 | `cbfaefe6d3a42b6cb3de1482ef01663630d4b39e`；精确 PTO/TileOP pin、源码审查、本地门禁及六个适用的托管 wheel 任务全部通过 |
| Linux、glibc、musl | 叶仓已合入 | 精确 PTO 身份和最终 LLVM 的干净 `vmlinux` 构建通过；全系统 PTO workload 仍是发布门禁 |
| VECTOR/CUBE 首次使用 | 架构完成；Linux 默认关闭 | ISA/Sail/QEMU 执行前异常契约通过。跨 ACR EXTCTX ABI 在 root issue 182 与 Linux issue 32 定义前，Linux 保持 V/C 关闭 |
| Queue-wired model 与 PTO kernels | 已合入并重钉 | Model `2913db72`；pto-kernels `5f5cf061`；PTO 0.58.6 codec、model CTest 12/12 以及六个 CUBE 程序精确身份编译/链接通过 |
| 跨模型 release-strict | 已验证 | 最终锁定的 QEMU/reference/compare 套件 7/7 通过；三份结果内存均匹配独立 golden；报告 SHA-256 `e7d927ba2418866d4352c7fa9bc9fa9670fd759efbcc86cc92e3387e461e486d` |
| 全系统 PTO CUBE | 冷启动矩阵已验证 | 六个独立 Linux/QEMU 启动 6/6 通过，并共享同一精确组件指纹；aggregate SHA-256 `3328caf983ae9f555b926b818d89795fb8e13650bd13a9ce0c925a6b8a29761a` |
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

最终发布还要求最终 root head 的托管检查全绿和独立审查，然后验证审查 tree 与
合入 tree 完全一致。

六子进程连续诊断不属于发布 PASS：在 Linux 关闭首次使用上下文管理时，它会复现
跨进程 Tile 上下文泄漏。逐用例冷启动证明六个维护程序各自端到端正确；跨进程复用
继续由 root issue 182 和 Linux issue 32 跟踪。
