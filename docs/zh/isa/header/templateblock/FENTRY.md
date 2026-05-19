# FENTRY

## 说明

**函数入口（Function Entry）**<br>  
本指令首先更新栈指针寄存器（SP）的值，随后将压栈起止寄存器指定的连续寄存器值写入未更新的原始 SP 指向的内存空间。

本指令用于函数入口的开栈操作(Function Prologue)。

## 汇编语法

```asm
    FENTRY [SrcBegin ~ SrcEnd], sp!, uimm
```

## 汇编符号

- **sp!**：栈指针寄存器，块内部更新该寄存器值。
- **uimm**：表示开栈空间大小的立即数（以8字节为单位），该参数编码于uimm[14:3]字段。
- **SrcBegin ~ SrcEnd**：指示压栈起止寄存器，表示R2至R23中一段连续的寄存器。

!!! note "注意！"

    当SrcBegin的索引大于SrcEnd的索引时，压栈寄存器顺序会出现卷绕。具体而言就是先将SrcBegin至R23压栈，再将R2至SrcEnd压栈。因此软件可以更灵活的选择压栈寄存器序列。

## 编码格式

![FENTRY](../../../figs/bitfield/svg/BlockHeader_32bit/FENTRY.svg)

## 执行方式

- 产生指令并push到指令队列：[Generate()](../../inst/LibPseudoCode.md)
- 转换为十进制数：[UInt()](../../inst/LibPseudoCode.md)

硬件模板块状态机会将该指令展开为以下微指令去执行:
```c
bits(15) immediate = uimm << 3;
integer M = max(2, UInt(SrcBegin));
integer N = min(23, UInt(SrcEnd));
integer offset = -8;

// 如果SrcEnd 编码小于 SrcBegin，那么压栈寄存器发生卷绕
if M > N then N += 24;

if immediate[14:12] != 0 then
    Generate(addi sp, 0, ->t);
    Generate(lui immediate[14:12], ->t);
    Generate(addi t#1, immediate[11:0], ->t);
    Generate(sub sp, t#1, ->sp);

    foreach (i from M to N by 1 in dec)
        integer idx = i % 24;
        if idx == 0 || idx == 1 then continue;
        Generate(sdi R[idx], [t#3, offset]);
        offset -= 8;
else
    Generate(subi sp, immediate[11:0], ->sp);

    foreach (i from M to N by 1 in dec)
        integer idx = i % 24;
        if idx == 0 || idx == 1 then continue;
        Generate(sdi R[idx], [sp, immediate + offset]);
        offset -= 8;
```
![stackspace](../../../figs/isa/inst/stackspace.png){ width="700"}

## 汇编示例

以块指令 `f.entry [s1 ~ s8], sp!, 256` 为例，硬件会将该块指令展开成以下指令序列：
```asm
subi sp, 256, -> sp
sdi s1, [sp, 248]    ; 将R12的值压栈:SP+(256-8)
sdi s2, [sp, 240]    ; 将R13的值压栈:SP+(256-16)
sdi s3, [sp, 232]    ; 将R14的值压栈:SP+(256-24)
sdi s4, [sp, 224]    ; 将R15的值压栈:SP+(256-32)
sdi s5, [sp, 216]    ; 将R16的值压栈:SP+(256-40)
sdi s6, [sp, 208]    ; 将R17的值压栈:SP+(256-48)
sdi s7, [sp, 200]    ; 将R18的值压栈:SP+(256-56)
sdi s8, [sp, 192]    ; 将R19的值压栈:SP+(256-64)
```

上面示例为该指令经常使用场景，没有发生寄存器的卷绕，完成s1-s8按序压栈。
如果压栈的结束寄存器编码小于起始寄存器，则会发生寄存器的卷绕，以 块指令 `f.entry [x0 ~ a4], sp!, 96` 为例：
```asm
subi sp, 96, -> sp
sdi x0, [sp, 88]    ; 将R20的值压栈:SP+(96-8)
sdi x1, [sp, 80]    ; 将R21的值压栈:SP+(96-16)
sdi x2, [sp, 72]    ; 将R22的值压栈:SP+(96-24)
sdi x3, [sp, 64]    ; 将R23的值压栈:SP+(96-32)
sdi a0, [sp, 56]    ; 将R2 的值压栈:SP+(96-40) 
sdi a1, [sp, 48]    ; 将R3 的值压栈:SP+(96-48) 
sdi a2, [sp, 40]    ; 将R4 的值压栈:SP+(96-56) 
sdi a3, [sp, 32]    ; 将R5 的值压栈:SP+(96-64) 
sdi a4, [sp, 24]    ; 将R6 的值压栈:SP+(96-72) 
```

## 注意事项

- 本块指令的跳转类型为**顺延（Fall）**。

## 块指令数计算

该模板块展开的微指令数计算公式为：`InstCount = cnt1(更新sp寄存器指令数) + cnt2（压栈指令数）`

```c
// 更新sp寄存器指令数
integer cnt1 = (uimm > 4088 ? 4 : 1);
// 压栈指令数
integer M = UInt(SrcBegin), N = UInt(SrcEnd);
integer cnt2 = (M <= N ? (N - M + 1) : (23 - M + N))
```

## 备注

此指令属于模板块指令。
