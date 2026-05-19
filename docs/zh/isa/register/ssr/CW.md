# CW

随机状态寄存器（CW-Canary Word Register）主要用于软件配置随机数，在入栈和出栈时检查状态。

![CW](../../../figs/bitfield/svg/Sysregs/CW.svg)

其原理可以简单概括为：

在函数栈帧中，在函数上下文和局部变量栈之间存入一个canary值；在函数返回退栈时，读取并检查canary值是否被改写，从而判断程序是否发生栈溢出。
编译器通过全局变量方式存储canary word，实现**fstack-protector-strong**。

## 具体实现

- 硬件提供专用寄存器CW（Canary Word Register），在器件开工时，软件产生随机数配置寄存器。
- 开栈/退栈时从CW读取canary word，并进行栈保护相关防护。

## 具体要求

- 每个硬线程分配一个寄存器。
- 寄存器宽度为64bit。
- 轻核内部可配。
- 支持高频读：读寄存器不带Barrier，单独提供读指令不通过系统块访问。

## 备注

该寄存器为轻核自定义的 **可读写的(RW)** 系统寄存器，其SSRID为**0x0820**。
