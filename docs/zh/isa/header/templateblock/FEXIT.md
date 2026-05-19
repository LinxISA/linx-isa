# FEXIT

## 说明

**函数出口（Function Exit）**<br>
本指令更新栈指针寄存器（SP）后，从新指针指向的内存中连续加载 8 字节数据，写入由起止寄存器指定的连续寄存器组。

该指令用于函数出口的收栈操作(Function Epilogue)。

## 汇编语法

```asm
    FEXIT [DstBegin ~ DstEnd], sp!, uimm
```

## 汇编符号

- **sp!**：栈指针寄存器，块内部会更新该寄存器值。
- **uimm**：表示收栈空间大小的立即数（以8字节为单位），该参数编码于uimm[14:3]字段。
- **DstBegin ~ DstEnd**：指示出栈起止寄存器，表示R2至R23中一段连续的寄存器。

!!! note "注意！"

    当DstBegin的索引大于DstEnd的索引时，出栈寄存器顺序会发生卷绕。具体而言就是先将DstBegin至R23出栈，再将R2至DstEnd出栈。

## 编码格式

![FEXIT](../../../figs/bitfield/svg/BlockHeader_32bit/FEXIT.svg)

## 执行方式

- 产生指令并push到指令队列：[Generate()](../../inst/LibPseudoCode.md)
- 转换为十进制数：[UInt()](../../inst/LibPseudoCode.md)

硬件模板块状态机会将该指令展开为以下微指令去执行:
```c
bits(15) immediate = uimm << 3;

if immediate[14:12] != 0 then
    Generate(lui immediate[14:12], ->t);
    Generate(addi t#1, immediate[11:0], ->t);
    Generate(add sp, t#1, ->sp);
else
    Generate(addi sp, immediate[11:0], ->sp);

integer M = UInt(DstBegin);
integer N = UInt(DstEnd);
integer offset = -8;

// 如果DstEnd 编码小于 DstBegin，那么出栈寄存器发生卷绕
if M > N then N += 24;

foreach (i from M to N by 1 in dec)
    integer idx = i % 24;
    if idx == 0 || idx == 1 then continue;
    Generate(ldi [sp, offset], -> R[idx]);
    offset -= 8;
```

![stackspace](../../../figs/isa/inst/stackspace.png){ width="700"}

## 汇编示例

出栈寄存器顺序未发生卷绕的场景，以块指令 `f.exit [s0 ~ s6], sp!, 72` 为例：
```asm
addi sp, 72, ->sp

ldi [sp,  -8], ->s0     ; 从栈上load至R11
ldi [sp, -16], ->s1     ; 从栈上load至R12
ldi [sp, -24], ->s2     ; 从栈上load至R13
ldi [sp, -32], ->s3     ; 从栈上load至R14
ldi [sp, -40], ->s4     ; 从栈上load至R15
ldi [sp, -48], ->s5     ; 从栈上load至R16
ldi [sp, -56], ->s6     ; 从栈上load至R17
```

出栈寄存器顺序发生卷绕的场景，以块指令 `f.exit [x0 ~ a7], sp!, 104` 为例：
```asm
addi sp, 104, ->sp

ldi [sp,  -8], ->x0     ; 从栈上load至R20
ldi [sp, -16], ->x1     ; 从栈上load至R21
ldi [sp, -24], ->x2     ; 从栈上load至R22
ldi [sp, -32], ->x3     ; 从栈上load至R23
ldi [sp, -40], ->a0     ; 从栈上load至R2（发生卷绕）
ldi [sp, -48], ->a1     ; 从栈上load至R3
ldi [sp, -56], ->a2     ; 从栈上load至R4
ldi [sp, -64], ->a3     ; 从栈上load至R5
ldi [sp, -72], ->a4     ; 从栈上load至R6
ldi [sp, -80], ->a5     ; 从栈上load至R7
ldi [sp, -88], ->a6     ; 从栈上load至R8
ldi [sp, -96], ->a7     ; 从栈上load至R9
```

## 注意事项

- 本块指令的跳转类型为**顺延（Fall）**。

## 块指令展开微指令数计算

该模板块展开的微指令数计算公式为：`InstCount = cnt1(更新sp寄存器指令数) + cnt2（出栈指令数）`

```c
// 更新sp寄存器指令数
integer cnt1 = (uimm > 4088 ? 3 : 1);
// 出栈指令数
integer M = UInt(DstBegin), N = UInt(DstEnd);
integer cnt2 = (M <= N ? (N - M + 1) : (23 - M + N))
```

<!-- 
## 模板块状态机实现

模板块状态机执行F.EXIT块指令时会根据以下定义产生指令。

- **calculate_bits**：检查块头BSET MASK，从低位到高位累计置位1的bit位数。
- **gen(i)**：确定模板块状态机第i次产生哪条指令的函数。
- **generate(inst)**: 模板块状态机产生指令并向指令队列内push指令的函数。
- **ObtainSetBitID(mask, i)**：从低位到高位检查，返回输入掩码中第i个置位为1的bit位下标。

```c
size_t regNum = calculate_bits(header.bsetmask);
gen(i){
    if(uimm19 <= 4088){
        if(i == 0) generate(addi RegPtr, uimm19[11:0], -> RegPtr);
        else if(i == 1) generate(addi t#1, 0, -> RegPtr);
        else if(i >= 2 && i <= (regNum+1)){
            size_t n = ObtainSetBitID(Header.LocalGetMask, i-1);
            generate(ldi [RegPtr, -(i-1)], -> RegDst[n]);
        }
        else return;
    }
    else{
        if(i == 0) generate(lui uimm19[18:12]);
        else if(i == 1) generate(addi t#1, uimm19[11:0]);
        else if(i == 2) generate(add RegPtr, t#1, -> RegPtr);
        else if(i == 3) generate(addi t#1, 0, -> RegPtr);
        else if(i >= 4 && i <= (regNum + 3)){
            size_t n = ObtainSetBitID(Header.LocalGetMask, i-3);
            generate(ldi [RegPtr, -(i-3)], -> RegDst[n]);
        }
        else return;
    }
}

generate(inst){
    while(1){
        if(instBuffer.notFull){
            instBuffer.push(inst);
            break;
        }
    }
}

size_t ObtainSetBitID(Mask, i) {
    size_t cnt = 0;
    for(size_t k = 0; k <= LeftmostBit(Mask); ++k){
        if(Mask[k] == 1 && ++cnt == i){
            return k;
        }
    }
    MaskMissException();
}
```
 -->

## 备注

此指令属于模板块指令。
