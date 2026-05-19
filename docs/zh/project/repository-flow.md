# 灵犀指令集 存储库流程 (v0.56)

工作区是规范优先和子模块优先的。

## 工作区引导程序

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

固定的生态系统存储库：

- `compiler/llvm`
- `emulator/qemu`
- `kernel/linux`
- `rtl/ZXTERMEN45QXZCore`
- `tools/pyCircuit`
- `lib/glibc`
- `lib/musl`
- `workloads/pto_kernels`

## 流程

1.`isa/v0.56/`中的ISA定义
2、`isa/v0.56/linxisa-v0.56.json`中编译目录
3.在`isa/generated/codecs/`中生成解码资产
4. AVS 中的验证（`avs/`）
5. 通过子模块固定进行跨存储库对齐
6. 使用 `tools/regression/run.sh` 进行回归门控