# Compression instructions

Compressed instructions are public microinstructions, which help optimize code density and cover some functions of 32-bit public microinstructions. All compressed microinstructions start with 'c.'. For a detailed list of compressed microinstructions, please refer to the chapter [Compressed Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/compress/) in the manual.

- Programmers can handwrite compression instructions on demand.
- Enable the compiler's compression instruction function, which can automatically optimize optimizable assembly into compression instructions. This function is currently enabled by default in the compiler.

## Assembly example:

```
c.add t#1, t#2, ->t     /*两个块内寄存器相加写到t标度尺寄存器上*/
c.lwi [t#1, 4], ->u     /*从地址为t#1+4的内存中加载一个字的数据到u标度尺寄存器上*/
```