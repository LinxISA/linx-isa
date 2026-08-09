# TPREFETCH

## 说明

**Tile 预取（Tile Prefetch）**

`TPREFETCH` 是 TLSU 访存提示操作。它与 `TLOAD` 使用相同的地址、
尺寸、布局和有效区域描述，但没有目标 Tile，也不产生架构可见的数据写回。硬件可
根据该描述提前把对应内存区域带入缓存或 Tile 访存路径；实现也可以把它作为提示处理。

`TPREFETCH` 的块头编码与 `TLOAD`/`TSTORE` 相邻：

| function | TileOp |
|----------|--------|
| 0 | TLOAD |
| 1 | TSTORE |
| 2 | TMOV |
| 3 | TPREFETCH |

## 汇编语法

```asm
TPREFETCH <LB0:row, LB1:col, LB2:stride, DataType, PadValue>, [RegSrc]
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|------|----------|
| **row** | 预取区域的行数，通过 `LB0` 传入。 | 否 |
| **col** | 每行预取的元素数，通过 `LB1` 传入。 | 否 |
| **stride** | 相邻两行之间的字节跨度，通过 `LB2` 传入。 | 是，默认按紧凑行宽推导 |
| **DataType** | 预取元素的数据类型/格式，用于计算访存粒度。 | 否 |
| **PadValue** | 与 `TLOAD` 共用字段；对 `TPREFETCH` 不产生目标写回。 | 是 |
| **RegSrc** | 输入全局寄存器 GGPR，保存预取内存基地址 `baseAddress`。 | 否 |

## 编码格式

该 TileOp 编码为以下指令：

- [BSTART.TPREFETCH](../../blockIntro/tlsu_block/header.md) `DataType`
- [B.DATR](../../header/B.DATR.md) `Layout, PadValue` *（与 TLOAD 共享描述字段）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`
- [B.IOR](../../header/B.IOR.md) `RegSrc`

`TPREFETCH` 不编码 `->DstTile<Size>`。如果汇编中出现目标 Tile，该形式非法。

## 执行模型

```c
void TPREFETCH(Scalar base) {
  for (int i = 0; i < row; ++i) {
    uintptr_t row_base = base + i * stride;
    for (int j = 0; j < col; ++j) {
      prefetch_hint(row_base + j * sizeof(DataType));
    }
  }
}
```

## 注意事项

- `TPREFETCH` 是目的地为空的 `TLOAD` 地址遍历形式。
- 它不分配、不写入、不释放任何目标 Tile。
- 预取是否实际改变缓存状态由实现定义；不得改变程序架构状态。
- 访存权限和地址转换异常策略必须与同地址 `TLOAD` 保持一致，除非实现明确把该操作作为不产生异常的纯提示处理。
