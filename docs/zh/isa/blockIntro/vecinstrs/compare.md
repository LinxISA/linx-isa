# 比较类指令

向量比较与置位类指令在每个执行通道（lane）内提供统一的相等/不等、逻辑与/或以及有符号与无符号的大小比较，覆盖寄存器-寄存器与寄存器-立即数两类操作数形式。指令对8/16/32/64位元素进行独立比较，并将比较结果按目的位宽写入 Dst，用于生成掩码、条件选择和分支判定等场景。

## 指令列表

寄存器与寄存器比较:

|     微指令    |             汇编格式       |     描述                                    |
|---------------|----------------------------|-------------------------------------------|
| V.CMP.EQ   | `v.cmp.eq SrcL.{T}, SrcR.{T}, ->Dst.{W}`   | 等于比较 |
| V.CMP.NE   | `v.cmp.ne SrcL.{T}, SrcR.{T}, ->Dst.{W}`   | 不等于比较 |
| V.CMP.AND  | `v.cmp.and SrcL.{T}, SrcR.{T}, ->Dst.{W}`   | 按位与比较 |
| V.CMP.OR   | `v.cmp.or SrcL.{T}, SrcR.{T}, ->Dst.{W}`   | 按位或比较 |
| V.CMP.LT   | `v.cmp.lt SrcL.{T}, SrcR.{T}, ->Dst.{W}`   | 有符号小于比较 |
| V.CMP.GE   | `v.cmp.ge SrcL.{T}, SrcR.{T}, ->Dst.{W}`   | 有符号大于等于比较 |
| V.CMP.LTU  | `v.cmp.ltu SrcL.{T}, SrcR.{T}, ->Dst.{W}`  | 无符号小于比较 |
| V.CMP.GEU  | `v.cmp.geu SrcL.{T}, SrcR.{T}, ->Dst.{W}`  | 无符号大于等于比较 |

寄存器与立即数比较:

|     微指令    |             汇编格式       |     描述                                    |
|---------------|----------------------------|-------------------------------------------|
| V.CMP.EQI  | `v.cmp.eqi SrcL.{T}, simm, ->Dst.{W}`   | 寄存器与有符号立即数等于比较 |
| V.CMP.NEI  | `v.cmp.nei SrcL.{T}, simm, ->Dst.{W}`   | 寄存器与有符号立即数不等于比较 |
| V.CMP.ANDI | `v.cmp.andi SrcL.{T}, simm, ->Dst.{W}`  | 寄存器与有符号立即数按位与比较 |
| V.CMP.ORI  | `v.cmp.ori SrcL.{T}, simm, ->Dst.{W}`   | 寄存器与有符号立即数按位或比较 |
| V.CMP.LTI  | `v.cmp.lti SrcL.{T}, simm, ->Dst.{W}`   | 寄存器与有符号立即数小于比较 |
| V.CMP.GEI  | `v.cmp.gei SrcL.{T}, simm, ->Dst.{W}`   | 寄存器与有符号立即数大于等于比较 |
| V.CMP.LTUI | `v.cmp.ltui SrcL.{T}, uimm, ->Dst.{W}`  | 寄存器与无符号立即数小于比较 |
| V.CMP.GEUI | `v.cmp.geui SrcL.{T}, uimm, ->Dst.{W}`  | 寄存器与无符号立即数大于等于比较 |

要点概括:

- 操作数形式：支持 SrcL.{T} 与 SrcR.{T} 的寄存器比较，以及 SrcL.{T} 与 simm/uimm 的立即数比较；T ∈ {8,16,32,64}，结果写入 Dst.{W}。
- 符号语义：提供显式的有符号与无符号大小比较指令；立即数变体区分有符号 simm 与无符号 uimm。
- 逻辑比较：支持基于位的与/或比较，用于按位关系检测与掩码构造。
- 行为边界：比较在各通道独立进行；未产生全局标志位或跨通道副作用；结果编码与截断/扩展遵循 Dst.{W} 的位宽规范。

## 指令编码

![CompareInstruction](../../../figs/bitfield/svg/Introduction_64bit/CompareInstructionVector.svg)
