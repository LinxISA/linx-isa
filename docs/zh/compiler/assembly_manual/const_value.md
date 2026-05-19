# 常量指令

```
Opcode Operand0,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者UL_GPR */
```

详细的微指令描述可以参见[常量指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/inst/misa_g/LUI/)这一章节。

汇编示例：

- Operand0为立即数，支持常量值和立即数的取值操作：%hi(表达式)来获得表达式的20bit的值, '%tpcrel_hi'表是获得全局符号相对于当前TPC的高20bit。

(0)
```
lui %hi(test), ->t    /* 获得标签’test‘地址，将其写入T寄存器  */
```

(1)
```
lui %hi(0x3fa80), ->t /* 获得0x3dfa80的高20bit，低12位默认为0，0x3f000写入T寄存器 */
```
