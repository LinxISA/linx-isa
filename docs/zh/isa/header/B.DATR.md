# B.DATR

## 说明

**块数据属性（Block Data Attribute）**

`B.DATR` 用于描述数据块指令的执行参数信息。如果一个块不具有本指令定义的任何属性，则可以选择不添加该指令。这种情况下块按照默认属性执行。

## 汇编语法

```asm
B.DATR {Layout.{canon, normal}, DataType, PadValue, ByteId, CMode, RMode, Sat}
```

## 汇编符号

- **Layout**：数据存储格式转换标识，可选类型见下表。该参数可以有两种可选后缀：
    - **canon(canonicalize)**: 将输入矩阵转换成标准左矩阵格式，基于不同的数据格式需要将输入原分形进行合并或者拆分。具体请见[ACCCVT](../header/tileblock/ACCCVT.md)指令介绍。
    - **normal**：不对输入矩阵的原分形做变换，可缺省。
- **DataType**：用于[TCVT](../header/tileblock/TCVT.md)和[ACCCVT](../header/tileblock/ACCCVT.md)等指令中表示数据格式转换后的目标类型。
- **PadValue**：表示输出Tile寄存器的填充值。无填充时可缺省。
- **ByteId**：指定要统计的目标字节，可选参数 Byte0、Byte1、Byte2、Byte3。
- **CMode**：比较模式，用于[TCMP](./tileblock/TCMP.md)和[TCMPS](./tileblock/TCMPS.md)指令。
- **RMode**：舍入模式参数，通常用于[TCVT](./tileblock/TCVT.md)指令。
- **Sat**：饱和运算标志，可缺省。（缺省表示不支持饱和运算或由实现/硬件针对特定类型定义饱和行为）

## 编码格式

![B.DATR](../../figs/bitfield/svg/BlockHeader_32bit/B.DATR.svg)

动态参数如下：

**C**标志位编码方式如下：

| C | 含义 |
|----|--------|
| 0 | 不执行canon操作 |
| 1 | 执行canon操作 |

**DataType**字段编码方式如下：

| 编码 | DataType | 编码 | DataType  | 编码 | DataType  | 编码 | Data  |
|------|----------|------|-----------|------|-----------|------|-----------|
| 0    | FP64     | 8    | e5m2      | 16   | S64       | 24   | U64       |
| 1    | FP32     | 9    | e3m2      | 17   | S32       | 25   | U32       |
| 2    | TF32     | 10   | e2m3      | 18   | S16       | 26   | U16       |
| 3    | HF32     | 11   | e2m1x2    | 19   | S8        | 27   | U8        |
| 4    | FP16     | 12   | e1m2x2    | 20   | S4x2      | 28   | U4x2      |
| 5    | BF16     | 13   | e8m0      | 21   | reserve   | 29   | reserve   |
| 6    | HiF8     | 14   | HiF4x2    | 22   | reserve   | 30   | reserve   |
| 7    | e4m3     | 15   | reserve   | 23   | reserve   | 31   | invalid   |

**Layout**字段编码方式如下：

| 编码 | format | 说明 | 编码 | format | 说明 |
|------|--------|------|-------|-------|--------|
| 0  | NORM  | 不转换        | 16 | reserve | 保留        |
| 1  | ND2DN | ND格式转DN格式 | 17 | ZN2ND | ZN格式转ND格式 |
| 2  | ND2ZZ | ND格式转ZZ格式 | 18 | ZN2DN | ZN格式转DN格式 |
| 3  | ND2ZN | ND格式转ZN格式 | 19 | ZN2ZZ | ZN格式转ZZ格式 |
| 4  | ND2NZ | ND格式转NZ格式 | 20 | ZN2NZ | ZN格式转NZ格式 |
| 5  | ND2NN | ND格式转NN格式 | 21 | ZN2NN | ZN格式转NN格式 |
| 6  | DN2ND | DN格式转ND格式 | 22 | NN2ND | NN格式转ND格式 |
| 7  | DN2ZZ | DN格式转ZZ格式 | 23 | NN2DN | NN格式转DN格式 |
| 8  | DN2ZN | DN格式转ZN格式 | 24 | NN2ZZ | NN格式转ZZ格式 |
| 9  | DN2NZ | DN格式转NZ格式 | 25 | NN2ZN | NN格式转ZN格式 |
| 10 | DN2NN | DN格式转NN格式 | 26 | NN2NZ | NN格式转NZ格式 |
| 11 | ZZ2ND | ZZ格式转ND格式 | 27 | NZ2ND | NZ格式转ND格式 |
| 12 | ZZ2DN | ZZ格式转DN格式 | 28 | NZ2DN | NZ格式转DN格式 |
| 13 | ZZ2ZN | ZZ格式转ZN格式 | 29 | NZ2ZZ | NZ格式转ZZ格式 |
| 14 | ZZ2NZ | ZZ格式转NZ格式 | 30 | NZ2ZN | NZ格式转ZN格式 |
| 15 | ZZ2NN | ZZ格式转NN格式 | 31 | NZ2NN | NZ格式转NN格式 |

关于数据存储布局的说明请见[Tile寄存器介绍](../register/common/tilereg.md)。

**PadValue**字段的编码方式如下：

| PadValue | 填充值 | 说明 |
|----------|------|---------|
| 0 | Zero | 零值 |
| 1 | Max  | 对应数据格式下最大值 |
| 2 | Min  | 对应数据格式下最小值 |
| 3 | Null | 不主动填充，保留随机值 |

**CMode** 字段编码方式如下：

| CMode | 比较方式 | 说明 |
|---------|----------|------|
| 0 | EQ | 相等比较 |
| 1 | NE | 不等比较 |
| 2 | LT | 小于比较 |
| 2 | GT | 大于比较 |
| 3 | LE | 小于等于比较 |
| 4 | GE | 大于等于比较 |
| >4 | reserve | 预留编码 |

**舍入模式（RMode）**字段编码如下表所示： 

| 编码 | 舍入模式 | 含义 |
|-----|----------|--------|
| 0 | NONE | No Rounding（不指定舍入模式，由硬件/实现决定默认行为） |
| 1 | RNE | Round to Nearest, ties to Even（向最近偶数舍入；最常见） |
| 2 | RTZ | Round Toward Zero（向零舍入，截断小数部分） |
| 3 | RDN | Round Down（向负无穷舍入） |
| 4 | RUP | Round Up（向正无穷舍入） |
| 5 | RNA | Round to Nearest, ties Away from Zero（远离零） |
| 6 | RTO | Round to Odd（向最近奇数舍入） |
| 7 | RHB | Hybrid Rounding（混合舍入模式） |
| >7 | reserve | 保留 |

**饱和标志位（S）**的编码方式如下：

| S | 含义  |
|----|--------|
| 0 | 无饱和运算（默认） |
| 1 | 支持饱和运算 |

**统计字节ID（ByteID）**字段的编码方式如下：

| ByteId | 含义/指定字节模式 |
|--------|------------------|
| 0 | Byte0 |
| 1 | Byte1 |
| 2 | Byte2 |
| 3 | Byte3 |
