# 灵犀指令集存储库流程（v0.58）

工作区是规范优先和子模块优先的。

## 工作区引导程序

```bash
git submodule sync -- <需要的子模块>
git -C <需要的子模块> fetch origin <已评审提交>
git -C <需要的子模块> checkout --detach <已评审提交>
```

固定的生态系统存储库：

- `compiler/llvm`
- `emulator/qemu`
- `kernel/linux`
- `rtl/LinxCore`
- `tools/pyCircuit`
- `lib/glibc`
- `lib/musl`
- `workloads/pto_kernels`

## 流程

1. `isa/v0.58/` 中的 ISA 定义
2. `isa/v0.58/linxisa-v0.58.json` 中的编译目录（当前规范权威）
3.在`isa/generated/codecs/`中生成解码资产
4. AVS 中的验证（`avs/`）
5. 通过子模块固定进行跨存储库对齐
6. 使用 `tools/regression/run.sh` 进行回归门控
