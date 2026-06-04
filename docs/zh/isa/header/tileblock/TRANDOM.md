# TRANDOM

## 说明

**数据块随机数生成（Tile Random Number Generation）**

`TRANDOM` 使用基于计数器的密码学伪随机数生成算法在输出 Tile 中生成均匀分布的伪随机数。

实现伪代码示意如下：
```pseudocode
// 伪随机数生成操作（基于计数器/密钥）
state = InitState(key, counter)                        // 初始化状态
for i in 0..(NumElements-1):                           // 遍历所有元素
  state = PRF_Round(state)                               // 伪随机轮变换
  dst[i] = ExtractOutput(state)                          // 提取输出值
```

---

## 汇编语法

```asm
TRANDOM <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, Rounds>, SrcKeyTile<.reuse>, SrcCtrTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输出 Tile 元素的数据格式，支持 `U32`、`S32`。
- **Rounds**：PRF 轮数，可选：`7` 或 `10`（轮数越多，安全性越高，吞吐量越低）。
- **SrcKeyTile**：密钥 Tile 寄存器（2 个 U32 元素），支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **SrcCtrTile**：计数器 Tile 寄存器（4 个 U32 元素），支持 `T`/`U`/`M`/`N` 队列输入。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TRANDOM, DataType`
- [B.DATR](../../header/B.DATR.md) `Rounds`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcKeyTile<.reuse>, SrcCtrTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **密钥与计数器**：
    - `SrcKeyTile` 为 2 个 U32 元素（64 位密钥）。
    - `SrcCtrTile` 为 4 个 U32 元素（128 位计数器/Nonce）。
- **算法**：基于类 ChaCha 四分之一轮变换的密码学 PRNG。
- **输出分布**：生成均匀分布的 `U32` 伪随机数。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：输出为行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TRANDOM <LB0:64, LB1:1, U32, 7>, T#1.reuse, U#2, ->T<256B>
```

1. **操作内容**
    - 使用 `T#1` 提供的密钥和 `U#2` 提供的计数器生成 64 个 U32 随机数
    - 输出：结果存入 `T` 队列 Tile 寄存器（1×64）
2. **数据处理范围**
    - 有效列数 `64`
    - 有效行数 `1`
3. **参数**
    - 7 轮 PRF（较快），每个元素为 `U32` 类型

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
