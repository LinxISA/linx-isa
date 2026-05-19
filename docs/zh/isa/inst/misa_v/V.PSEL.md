# V.PSEL

## 说明

掩码选择(*Select with Predicate Mask*)<br>
将条件掩码寄存器中每一位作为Group内对应lane的条件掩码，根据条件掩码选择左源寄存器或右源寄存器的内容写到目的寄存器中。如果掩码为**1**，选择左源寄存器的内容；否则，选择右源寄存器的内容。

## 汇编语法

```asm
    v.psel SrcP<.ud>, SrcL<.reuse>.{T}, SrcR<.reuse>.{T}<.neg>, ->RegDst.{W}
```

## 汇编符号

- **SrcP**：条件掩码寄存器，可以索引**掩码寄存器P**或**标量寄存器**（标量寄存器内每一位作为一个lane的条件掩码）。
- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。SrcR可以选择带后缀：
    - **.neg**：将右源操作数按位取反加一。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.PSEL](../../../figs/bitfield/svg/Instruction_64bit/V.PSEL.svg)

其中，SrcRType域编码如下：

|  SrcRType  |  汇编标识  |  解释                       |
|-----------|-----------|-----------------------------|
|  00  |  无   |  无格式转换                        |
|  01  |  无   |  保留（reserve）  |
|  10  |  无   |  保留（reserve）  |
|  11  |  .neg  |  negative，将操作数位取反加一  |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码

integer {p, 64} = DecodeINT(SrcP); 
bits(64) cmask = V[p, 64];   // 获取条件掩码

// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srctype1, laneid];
        bits(64) operand2 = V[n, srctype2, laneid];

        if (SrcRType == 3)
            operand2 = Negative(operand2);

        bits(64) result = (cmask[laneid] == 1 ? operand1 : operand2);
        
        V[d, dstwidth, laneid] = result;  // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

实现示意图如下：

![PSEL](../../../figs/isa/inst/psel.png){ width="800" }

## 优化场景

程序执行if单边分支：进入if前有一组向量值，进入if后计算更新了该向量的一部分值，if结束后需要将更新部分与未更新的部分进行合并。

不使用V.PSEL指令：
```asm
# cond -> vu#1, a -> vt#3, b -> vt#2, c -> vt#1
if.entry:
     l.addi p, 0, -> u                 # 保存P寄存器掩码
     v.cmp.eqi vu#1, 1, -> p     # 判断if执行条件
if.then:
     v.add vt#2, vt#3, -> vu     # d = a+b

if.end:
     l.xori p, -1 -> p            # 对if分支掩码的取反
     l.and u#1, p, ->p           
     v.addi vt#1, 0, -> vt        # 获得原向量未更新部分
     l.addi u#1, 0, -> p          # 恢复进入if分支前的掩码
     v.or vt#1, vu#1, -> vt       # 用原向量未更新部分与if分支更新的部分拼接
     v.sd vt#1, [xx]
```

图示如下:

![PSEL](../../../figs/isa/inst/psel1.png){ width="800" }

使用V.PSEL指令：
```asm
# cond -> vu#1, a -> vt#3, b -> vt#2, c -> vt#1
if.entry:
     l.addi p, 0, -> u             # 保存P寄存器掩码
     v.cmp.eqi vu#1, 1, -> p       # 判断if执行条件
if.then:
     v.add vt#2, vt#3, -> vu       # d = a+b 
     v.psel p, vu#1, vt#1, ->vt    # 根据if分支掩码拼接原向量未更新部分与if分支更新的部分
if.end:
     l.addi u#1, 0, -> p           # 恢复进入if分支前的掩码
     v.sd vt#1, [xx]
```

图示如下：

![PSEL](../../../figs/isa/inst/psel2.png){ width="800" }

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
