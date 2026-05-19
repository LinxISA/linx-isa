# 第 5 阶段：FPGA 平台启动 (Xilinx ZYBO Z7-20)

目标板：Digilent ZYBO Z7-20 (Zynq-7000)

## 目标

首先使用 PS DDR + AXI + PL 核心集成将 灵犀 CPU 和 Janus Core 引入稳定的 Zynq PS/PL 平台。

## 平台基线

- SoC集成路径：**PS DDR + AXI + PL核心**
- 核心在 PL 中实例化。
- Linux/测试映像和暂存缓冲区驻留在 PS DDR 中。
- UART 和通过/失败 MMIO 行为必须保持兼容
  `docs/bringup/contracts/fpga_platform_contract.md`。

## 硬件架构假设

- 跨 PS 和 PL 的确定性重置排序。
- 首先启动单个时钟域；多时钟扩展稍后进行。
- UART 控制台可用作主要启动可见性通道。
- PL 中的 AXI 主桥用于 DDR 访问。

## 提升阶梯

1. 最小 灵犀 PL 包装器：
   - 核心 + BRAM/引导路径 + UART + 定时器 + AXI 至 PS DDR
2. 板卡整合：
   - 时钟/重置接线、约束和可重复的项目构建
3.硬件冒烟测试：
   - 使用 UART 通过/失败协议执行 ROM/DDR 有效负载
4、Janus端口：
   - Janus Core 上相同的包装模式和烟雾协议

## 所需的烟雾场景

- UART hello 和确定性启动日志
- 内存写/读回健全性
- 分支/呼叫控制流健全性
- MMIO 通过/失败寄存器写入

## 退出标准

- 灵犀 和 Janus 都在 ZYBO Z7-20 上运行烟雾有效载荷。
- 结果在重复的电源循环中是可重现的。
- 使用与模拟相同的跟踪/事件约定对故障进行分类。