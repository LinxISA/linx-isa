# LinxISA 汇编示例包（v0.57.1）

本目录包含由锁定的 PTO ISA 0.57.1 kernel surface 生成的规范公共汇编示例。

## 目录布局

- `curated/`：经过审阅的手写标量与反汇编示例。
- `generated/`：由 `workloads/pto_kernels/tools/examples/` 确定性生成的编译器输出。
- `index.yaml`：精确记录源文件和工具链来源。

## 规范 Tile 示例

```asm
BSTART.TLOAD INT32
B.DIM        a3, 0, ->lb0
B.DIM        a3, 0, ->lb1
B.DIM        a3, 0, ->lb2
B.IOR        [a6,a7],[]
B.IOT        last, ->t<4KB>
```

0.57.1 示例不包含 `B.ARG`、通用 `BSTART.TMA` / `BSTART.CUBE`、
`MAMULB` 或已删除的 D 类操作。请使用 `index.yaml` 记录的 LLVM 与
PTO-Kernel 提交重新生成示例。

来源：`docs/reference/examples/v0.57/`
