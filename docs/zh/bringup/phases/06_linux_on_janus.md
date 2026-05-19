# 第 6 阶段：FPGA 上的 Linux 启动（Janus 最终目标）

最终目标：**Janus Core** 上的 Linux + BusyBox shell 通过 UART 在 ZYBO Z7-20 上运行。

## 目标

使用分阶段的 Linux 启动：

1. FPGA 上的 灵犀（NOMMU 里程碑）
2. FPGA 上的 Janus（NOMMU 里程碑）
3. FPGA 上的 Janus（MMU Linux 里程碑，最终版）

## 阶段 D1：灵犀 NOMMU Linux

### 参赛标准

- 第 5 阶段 灵犀 FPGA 烟雾测试通过。
- 内核、rootfs/initramfs 和启动映像流程是可重现的。

### 接受

- 内核到达 UART 上的 BusyBox shell。
- 烟雾命令通过（至少）：`uname -a` 和内存/cpuinfo 健全性。

## 阶段 D2：Janus NOMMU Linux

### 参赛标准

- D1 完整且可重复。
- Janus FPGA 烟雾测试通过。

### 接受

- Janus 使用相同的烟雾命令到达 UART 上的 BusyBox shell。
- 引导路径和有效负载生成可编写脚本且可重复。

## 阶段 D3：Janus MMU Linux（最终）

### 参赛标准

- D2 完成。
- MMU/TLB/page-walk实现和异常行为满足架构要求。

### 接受（最终门）

- 完整的 MMU Linux 在 Janus 上启动到 BusyBox shell。
- 启动在重复运行/电源周期中保持稳定。
- 与所有者明确跟踪已知不受支持的功能。

## 回归要求

- 保留最少的 Linux 启动回归脚本和日志捕获过程。
- 将门结果和阻断器存储在 `docs/bringup/PROGRESS.md`（D1/D2/D3 行）中。