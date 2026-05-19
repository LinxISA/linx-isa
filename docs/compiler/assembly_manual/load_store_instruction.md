# Memory access instructions

## Memory loading instructions

```
Opcode [Operand0,Operand1],->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者UL_GPR寄存器 */
```

- Expand on Opcode: {b,h,w,d} to specify the size of load or store transfer, `b` represents bytes, `h` represents half word, `w` represents word, `d` represents double word. An additional `u` can be used to indicate a byte or halfword or word unsigned extension to 64bit (bu means unsigned byte, hu means unsigned halfword and wu means unsigned word)<br>
- Extend `i` on Opcode to indicate that the right source operation object Operaand1 is an immediate number: Opcode{i}, By default, the memory access address is shifted by a shift operation corresponding to the memory access size. When `h` accesses a half word, it shifts left by 1 bit by default. When `w` accesses a word, it shifts left by 2 bits by default. When `d` accesses a double word, it shifts left by 3 bits by default. **The immediate value in the assembly instruction needs to be an integer multiple of the access bit width, otherwise the assembler will report an error**. <br>
- Adding ‘.u’ after the Opcode indicates that the default shift operation will not be performed on the memory access address. When the offset is an immediate number, it does not need to be an integer multiple of the memory access bit width. <br>
- Address calculation operation: `[Oerand0,Operand1]`, Operand0 is a register, Operand1 can be a register or an immediate number, the address calculation result is Operand0 + Operand1 <br>
- When the right source operation object Operaand1 is a register, you can add {.sw, .uw} extensions. `sw` means intercepting the lower 32 bits of the operand and doing signed extension. `uw` means intercepting the lower 32 bits of the operand and doing unsigned extension<br>
- `<<`, perform shift operations (1), (2) on the right source register. shamt represents the amount of left shift. Possible values are {0, 1, 2, 3}. When shifting 0 bits to the left, it means no shift is performed. It can be defaulted to (0)<br>
- When the right source operation object Operaand1 is a 12-bit immediate number, expression operations are supported: `%lo(表达式)` means to obtain the lower 12 bits of the expression value, `%tpcrel_lo(symbol)` means to obtain the lower 12 bits of the symbol address value relative to the TPC offset value, and `%tprel_lo` means to obtain the high 12 bits of the TLS variable relative to the Thead Pointer register. <br>

For detailed microinstruction descriptions, please refer to the chapter [Memory Access Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/load_store/) in the manual.

Assembly instructions:

(0)<br>
```
lb  [a2, a3], ->t          /* 访存地址为 a2 + a3, 加载出来的数据输出到T寄存器 */
```

(1)
```
lb  [a2, a3<<2], ->t       /* 访存地址为 a2 + (a3*4), 加载出来的数据输出到T寄存器 */
```

(2)
```
lb  [a2, a3.sw<<2], ->t    /* 访存地址为 a2 + (a3截取寄存器的低32bit做有符号扩展*4), 加载出来的数据输出到T寄存器 */
```

(3)
```
lhi  [a2, 32], ->t          /* 访存地址为 a2 + 32, 右操作对象为立即数, 显示为默认左移1位后的值, 加载出来的数据输出到T寄存器 */
lhi.u [a2, 32], ->t         /* 访存地址为 a2 + 32, 加载出来的数据输出到T寄存器 */
```

(4)
```
lwi  [a2, 32],->t        /* 访存地址为 a2 + 32, 右操作对象为立即数, 显示为默认左移2位后的值, 加载出来的数据输出到T寄存器 */
lwi.u  [a2, 32],->t      /* 访存地址为 a2 + 32, 加载出来的数据输出到T寄存器 */
```

## Memory write command

```
Opcode Operand0, [Operand1,Operand2]           
Opcode Operand0, [Operand1,Operand2], ->{LL_GPR, UL_GPR}   /*.a结尾的内存写指令，地址输出到LL_GPR或者UL_GPR里*/          
```- Expand on Opcode: {b,h,w,d} to specify the size of load or store transfer, `b` represents bytes, `h` represents half-word, `w` represents word, `d` represents double-word. <br>
- Extend `i` on Opcode to indicate that the right source operation object Operand1 is an immediate number: Opcode{i}, by default, performs a shift operation on the access address corresponding to the access size. When `h` accesses a half word, it shifts left by 1 bit by default. When `w` accesses a word, it shifts left by 2 bits by default. When `d` accesses a double word, it shifts left by 3 bits by default. It is required that the offset in the assembly is an integer multiple of the memory access bit width when it is an immediate number, otherwise the assembler will report an error. <br>
- Adding `u` after the Opcode indicates that the default >shift operation will not be performed on the access address. When the offset is an immediate value, it is not required to be an integer multiple of the memory access bit width. <br>
- Address calculation operation: `[Oerand1,Operand2]`, Operand1 is a register, Operand2 can be a register or an immediate number, the address calculation result is Operand1 + Operand2 <br>
- When Operand2 is a register, add {.sw, .uw} extension at the end. `sw` means intercepting the lower 32 bits of the operand and doing signed extension. `uw` means intercepting the lower 32 bits of the operand and doing unsigned extension<br>
- When the right source operation object Operaand1 is a 12-bit immediate number, expression operations are supported: `%lo(表达式)` means to obtain the lower 12 bits of the expression value, `%tpcrel_lo(symbol)` means to obtain the lower 12 bits of the symbol address value relative to the TPC offset value, and `%tprel_lo` table is to obtain the lower 12 bits of the TLS variable relative to the Thead Pointer register <br>

For detailed microinstruction descriptions, please refer to the chapter [Memory Access Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/load_store/) in the manual.

Assembly instructions:

```
sb   a1, [a2, a3]             /* 访存地址为 a2 + a3                     */
sh   a1, [a2, a3<<1]          /* 访存地址为 a2 + (a3 << 1), 默认左移1位 */
shi  a1, [a2, 32]             /* 访存地址为 a2 + 32，立即数要求2的倍数  */
sw   a1, [a2, a3<<2]          /* 访存地址为 a2 + (a3 << 2), 默认左移2位 */
swi  a1, [a2, 32]             /* 访存地址为 a2 + 32，立即数要求4的倍数  */
sd   a1, [a2, a3<<3]          /* 访存地址为 a2 + (a3 << 3), 默认左移3位 */
sdi  a1, [a2, 32]             /* 访存地址为 a2 + 32，立即数要求8的倍数  */
sh.u   a1, [a2, a3]           /* 访存地址为 a2 + a3, 不做默认左移 */
shi.u  a1, [a2, 32]           /* 访存地址为 a2 + 32, 不要求立即数对齐 */
sw.u   a1, [a2, a3]           /* 访存地址为 a2 + a3, 不做默认左移 */
swi.u  a1, [a2, 32]           /* 访存地址为 a2 + 32, 不要求立即数对齐 */
sd.u   a1, [a2, a3]           /* 访存地址为 a2 + a3, 不做默认左移 */
sdi.u  a1, [a2, 32]           /* 访存地址为 a2 + 32, 不要求立即数对齐 */
```