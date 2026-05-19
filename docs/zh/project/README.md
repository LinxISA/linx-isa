# 项目文档

存储库级流程、治理和导航策略。

## 内容

- **[navigation.md](navigation.md)** - 规范路径图和禁止路径
- **[repository-flow.md](repository-flow.md)** - 开发工作流程和贡献指南
- **[omx-linxisa-playbook.md](omx-linxisa-playbook.md)** - OMX 操作员手册，用于门分类、重新固定、关闭和证据流
- **[omx-linxisa-prompt-templates.md](omx-linxisa-prompt-templates.md)** - 灵犀指令集 OMX 会话的可重用提示模板
- **[superproject-bringup-methodology.md](superproject-bringup-methodology.md)** - 代理友好的超级项目启动方法和操作手册
- **[new-agent-sop.md](new-agent-sop.md)** - 在超级项目中工作的新代理的简短 SOP
- **[maintainer-repin-checklist.md](maintainer-repin-checklist.md)** - 安全子模块 repin 的维护者清单
- **[linxisa-superproject-methodology-zh.tex](linxisa-superproject-methodology-zh.tex)** - 中文LaTeX手册源
- **[linxisa-superproject-methodology-zh.pdf](linxisa-superproject-methodology-zh.pdf)** - 中文PDF手册
- **[superproject-whitepaper-zh.tex](superproject-whitepaper-zh.tex)** - 中文白皮书LaTeX源码
- **[superproject-whitepaper-zh.pdf](superproject-whitepaper-zh.pdf)** - 中国方法论白皮书 PDF

## 导航政策

该工作空间遵循严格的导航契约。请参阅 [navigation.md](navigation.md)：

- 允许的顶级目录
- 特定任务的规范目的地
- 禁止/替换路径
- 子模块更新程序

## 快速参考|任务|路径|
|------|------|
|运行时测试 | `avs/qemu/` |
|编译测试 | `avs/compiler/linx-llvm/tests/` |
|独立式 libc | `avs/runtime/freestanding/` |
| Linux libc 源代码 | `lib/glibc/`，`lib/musl/` |
| PTO 内核 块头s | `workloads/pto_kernels/include/` |
|装配示例 | `docs/reference/examples/v0.56/` |

## CI 验证

在提交之前，验证存储库布局：

```bash
bash tools/ci/check_repo_layout.sh
```