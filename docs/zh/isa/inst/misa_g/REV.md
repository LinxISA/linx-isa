# REV

## 说明

翻转(*Reverse*)  
在源操作数的每个 `M` 位范围内以 `N` 位为单位进行高低位翻转，结果写到目的寄存器中。

## 汇编语法

```
    rev SrcL, M, N, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **M**：表示每次进行翻转操作的操作域位宽，合法取值包括：{2, 4, 8, 16, 32, 64}。该参数减1后编码于immr字段。
- **N**：表示每个操作域内进行翻转操作的单位，合法取值包括：{1, 2, 4, 8, 16, 32}。该参数编码于imml字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![REV](../../../figs/bitfield/svg/Instruction_32bit/REV.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer M = UInt(immr) + 1;
    integer N = UInt(imml);

    // 以下情况报非法指令
    if M isnot in range{2, 4, 8, 16, 32, 64} then Exception(EC_ILLEGAL);
    if N isnot in range{1, 2, 4, 8, 16, 32}  then Exception(EC_ILLEGAL);
    if M <= N                                then Exception(EC_ILLEGAL);  

    bits(64) operand = R[s, 64];
    bits(64) result;

    integer fieldnum = 64 / M;
    integer elementnum = M / N;
    integer idx = 0;
    integer ridx;
    for i = 0 to (fieldnum - 1) {
        ridx = idx + (elementnum - 1) * N;
        for j = 0 to (elementnum - 1) {
            result[ridx+(N-1): ridx] = operand[idx+(N-1) : idx];
            idx += N;
            ridx -= N;
        }
    }

    R[d, 64] = result;
```

![REV](../../../figs/isa/inst/rev.png){ width="800" }

## 应用示例

场景一：在源操作数的整个64bit范围内进行字节翻转：`rev SrcL, 64, 8`。

![REV64](../../../figs/isa/inst/rev64.png){ width="800" }

场景二：在源操作数的每个32bit范围内进行字节翻转：`rev SrcL, 32, 8`。

![REV32](../../../figs/isa/inst/rev32.png){ width="800" }

场景三：在源操作数的每个16bit范围内进行字节翻转：`rev SrcL, 16, 8`。

![REV16](../../../figs/isa/inst/rev16.png){ width="800" }

场景四：在源操作数的每个32bit范围内进行比特位翻转：`rev SrcL, 32, 1`。

![RBITW](../../../figs/isa/inst/rbitw.png){ width="800" }

## 汇编索引模式

指令输出到块内t寄存器:
```asm
rev a1,  m, n,     ->t             /* 单寄存器绝对索引 */
rev t#1, m, n,     ->t             /* 单寄存器相对索引 */
rev u#1, m, n,     ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
rev a1,  m, n,     ->u             /* 单寄存器绝对索引 */
rev t#1, m, n,     ->u             /* 单寄存器相对索引 */
rev u#1, m, n,     ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
rev a1,  m, n,     ->a3            /* 单寄存器绝对索引 */
rev t#1, m, n,     ->a3            /* 单寄存器相对索引 */
rev u#1, m, n,     ->a3            /* 单寄存器相对索引 */
```

## 注意事项

M值大小必须大于N值，否则本指令触发 **非法指令异常**。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
