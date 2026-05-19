# virtio-9p 启动状态 (灵犀 virt)

## 总结

我们正在使用 **virtio-9p over virtio-mmio** 为 灵犀 Linux 启动提供主机→来宾文件共享。

目前状态：

- virtio-mmio 传输：**工作**（来宾枚举 virtio 设备）
- virtio-mmio 上的 virtio-blk：**工作**（访客看到 `vda`）
- virtio-9p 安装：运行 `mount -t 9p render-share /opt/share ...` 时出现 `EPROTO (-71)` **失败**

## 最小复制

### QEMU

使用 灵犀 virt DT 提供的传输（当 DT 已声明 virtio-mmio 节点时，不要**添加 `virtio_mmio.device=...`）。

示例：

```bash
QEMU=~/linx-isa/emulator/qemu/build/qemu-system-linx64
KERNEL=~/linx-isa/kernel/linux/build-linx-render/vmlinux
INITRD=~/linx-isa/kernel/linux/build-linx-fixed/linx-initramfs/initramfs.cpio
SHARE=~/linx-isa/out/render-share

$QEMU \
  -machine virt -m 1024M -smp 1 \
  -kernel "$KERNEL" -initrd "$INITRD" \
  -append "console=ttyS0 lpj=1000000 loglevel=7" \
  -nographic -monitor none \
  -fsdev local,id=fsdev0,path="$SHARE",security_model=none,multidevs=remap \
  -device virtio-9p-device,fsdev=fsdev0,mount_tag=render-share
```

### 嘉宾

在 initramfs 中，运行 `m9p`（调试小程序）来尝试挂载并打印原始返回代码：

- 今天预计：`9p_mount=ffffffffffffffb9`（== -71，EPROTO）

## 已知的陷阱/注释

- 如果在 DT 已包含 virtio-mmio 节点时传递 `virtio_mmio.device=0x200@0x30001000:1`，Linux 可能会尝试注册*第二个* virtio-mmio 传输并命中探测冲突（例如 `-16`）。
- 字节序假设：virtio 和 9p 协议字段的 **little-endian**。

## 相关 PR

- QEMU：用于 linx virt 的多种现代 virtio-mmio 传输（用于 virtio 启动的基础设施）
  - https://github.com/灵犀指令集/qemu/pull/19
- Linux：initramfs `m9p` 小程序和 `/opt/share` 目录用于来宾内复制
  - https://github.com/灵犀指令集/linux/pull/15

## 接下来的调试步骤

- 为第一个 9p 交换（Tversion/Rversion）添加最小 QEMU 端日志记录，以确定故障是否为：
  - 功能协商不匹配
  - virtqueue描述符解析问题
  - 有效负载字节序/长度解码问题