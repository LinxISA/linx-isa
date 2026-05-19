# 微指令列表

当前版本，浮点块块体中提供的微指令列表如下：

## 公共指令

浮点标量块内支持所有的公共指令，具体请见[公共指令列表](../std_block/instlist.md#puclicinsts)。

## 特有指令

浮点标量块内独有的32bit指令如下：

| 分类  | 指令列表  |
|-------|--------------|
| **浮点运算** | [FADD](../../inst/misa_f/FADD.md), [FSUB](../../inst/misa_f/FSUB.md), [FMUL](../../inst/misa_f/FMUL.md), [FDIV](../../inst/misa_f/FDIV.md), [FMADD](../../inst/misa_f/FMADD.md), [FMSUB](../../inst/misa_f/FMSUB.md), [FNMADD](../../inst/misa_f/FNMADD.md), [FNMSUB](../../inst/misa_f/FNMSUB.md) |
| **浮点比较** | [FEQ](../../inst/misa_f/FEQ.md), [FNE](../../inst/misa_f/FNE.md), [FLT](../../inst/misa_f/FLT.md), [FGE](../../inst/misa_f/FGE.md), [FEQS](../../inst/misa_f/FEQS.md), [FNES](../../inst/misa_f/FNES.md), [FLTS](../../inst/misa_f/FLTS.md), [FGES](../../inst/misa_f/FGES.md) |
| **最大最小值** | [MAX](../../inst/misa_f/MAX.md), [MIN](../../inst/misa_f/MIN.md), [MAXU](../../inst/misa_f/MAXU.md), [MINU](../../inst/misa_f/MINU.md), [FMAX](../../inst/misa_f/FMAX.md), [FMIN](../../inst/misa_f/FMIN.md) |
| **数据格式转换** | [FCVT](../../inst/misa_f/FCVT.md), [SCVTF](../../inst/misa_f/SCVTF.md), [UCVTF](../../inst/misa_f/UCVTF.md), [FCVTA](../../inst/misa_f/FCVTA.md), [FCVTM](../../inst/misa_f/FCVTM.md), [FCVTN](../../inst/misa_f/FCVTN.md), [FCVTP](../../inst/misa_f/FCVTP.md), [FCVTZ](../../inst/misa_f/FCVTZ.md) |
| **浮点特殊运算** | [FABS](../../inst/misa_f/FABS.md), [FSQRT](../../inst/misa_f/FSQRT.md), [FRECIP](../../inst/misa_f/FRECIP.md) |

## 浮点数据类型

浮点标量块内的浮点指令支持4种格式的浮点型数据的运算和操作，包括双精度浮点数、单精度浮点数、半精度浮点数和低精度浮点数，并且都遵循IEEE 754-2008标准规范的定义。

浮点数据类型定义如下表:

|  浮点型格式  |  汇编符号  |  符号位位数  |  指数位数  | 尾数位数  |     解释   |
|-----------|------------|-----------|----------|---------------|------------|
|  FP8   |  FB  |  1 |  4  |  3   |  表示8bit低精度low precision浮点数        |
|  FP16  |  FH  |  1 |  5  |  10  |  表示16bit半精度half precision浮点数      |
|  FP32  |  FS  |  1 |  8  |  23  |  表示32bit单精度single precision浮点数    |
|  FP64  |  FD  |  1 |  11 |  52  |  表示64bit双精度double precision浮点数    |

各浮点数据类型示意图如下：

![format](../../../figs/isa/datatype/fp_format0.png)

## 备注

浮点块内暂时不支持超长指令。
