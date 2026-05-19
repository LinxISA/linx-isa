# 第 3 阶段：模拟器 (QEMU) 启动

QEMU 实现的真实来源是子模块：

- `emulator/qemu/`

灵犀 补丁谱系保留在 灵犀指令集 QEMU 分支历史记录中，然后通过子模块 SHA 固定在此处。

## 基本流程

1. 构建 灵犀 测试对象/可执行文件。
2. 使用 `qemu-system-linx64 -machine virt -kernel <image>` 运行。
   对于合并的 灵犀64 恢复通道，直接内核/rootfs 运行是
   默认情况下无固件，应包含 `-bios none`，除非特定
   固件工件正在被有意测试。
3. 通过 AVS 套件验证输出和退出状态。

## 测试入口点

```bash
# Default suites
./avs/qemu/run_tests.sh

# Full suites
./avs/qemu/run_tests.sh --all --timeout 20
```

## 惯例

- UART MMIO底座：`0x10000000`
- 退出MMIO：`0x10000004`
- `0x10000004` 写入的退出值用作 QEMU 进程退出代码