# 数据格式转换

数据格式转换指令主要包含三类操作：

- 浮点数 与 浮点数之间的转换；
- 浮点数 向 有符号数或无符号转换；
- 有符号数或无符号数 向 浮点数转换。

| 指令 | 说明 | 舍入模式 |
|------|--------|---------|
| fcvt | 浮点数之间转换 | 受控于CSTATE（FRM），默认RNE |
| scvtf | 有符号整型转浮点 | 受控于CSTATE（FRM），默认RNE |
| ucvtf | 无符号整型转浮点 | 受控于CSTATE（FRM），默认RNE |
| fcvta | 浮点转有/无符号整型 | 默认RNA，向远离零的方向舍入 |
| fcvtm | 浮点转有/无符号整型 | 默认RDN，向负无穷舍入 |
| fcvtn | 浮点转有/无符号整型 | 默认RNE，向最近偶数舍入 |
| fcvtp | 浮点转有/无符号整型 | 默认RUP，向正无穷舍入 |
| fcvtz | 浮点转有/无符号整型 | 默认RTZ，向零的方向舍入 |

汇编格式如下：

```asm
    fcvt.{srcT2dstT}  SrcL, ->{t, u, Rd}
    fcvta.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtm.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtn.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtp.{srcT2dstT} SrcL, ->{t, u, Rd}
    fcvtz.{srcT2dstT} SrcL, ->{t, u, Rd}
    scvtf.{srcT2dstT} SrcL, ->{t, u, Rd}
    ucvtf.{srcT2dstT} SrcL, ->{t, u, Rd}
```

其中：srcT：代指输入数据类型，dstT：代指格式转换后的数据类型。
