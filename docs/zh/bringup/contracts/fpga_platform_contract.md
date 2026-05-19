# FPGA平台合同（ZYBO Z7-20）

目标板：基于 Xilinx Zynq-7000 的 Digilent ZYBO Z7-20。

## 固定平台默认值

- UART MMIO底座：`0x10000000`
- 通过/失败测试 MMIO 寄存器：`0x10000004`

这些默认值必须与现有的面向 QEMU 的软件启动路径保持兼容。

机器可读形式：

- `docs/bringup/contracts/fpga_platform_contract.json`

## SoC 集成基线

- 核心是在 PL 中实现的。
- PL 内核通过 AXI 互连/桥访问 PS DDR。
- Linux 映像和暂存缓冲区位于 DDR 中。

## 默认启动模式

- 第一个 Linux 里程碑使用直接内核引导路径。
- U-Boot 集成是可选的，首次通过/失败门不需要。

## 确定性要求

- PS 和 PL 之间的确定性重置排序。
- 用于重复启动测试的可再现时钟/约束。
- UART 输出是早期里程碑的主要接受渠道。