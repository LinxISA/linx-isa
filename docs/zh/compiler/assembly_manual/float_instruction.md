# 浮点块微指令

```
Opcode Operand0,Operand1,Operand2                        /* 无输出，浮点块内跳转 */    
Opcode Operand0->{LL_GPR，UL_GPR}                        /* 输出到LL_GPR或者UL_GPR */
Opcode Operand0,Operand1,->{LL_GPR，UL_GPR}              /* 输出到LL_GPR或者UL_GPR */
Opcode Operand0,Operand1,Operand2,->{LL_GPR，UL_GPR}     /* 输出到LL_GPR或者UL_GPR */
```

这些微指令仅限浮点块使用，微指令操作中不仅包括浮点操作，同时也包含一些整型操作。浮点相关的操作涉及的数据类型如下：

- '.fd' : 代表64bit双精度浮点类型 <br>
- '.fs' : 代表32bit单精度浮点类型 <br>
- '.fh' : 代表16bit半精度浮点类型 <br>
- '.fb' : 代表8bit低精度浮点类型
- '.ud' ：代表64bit无符号长整型数据 <br>
- '.uw' : 代表32bit无符号长整型数据 <br>
- '.uh' : 代表16bit无符号长整型数据 <br>
- '.ub' : 代表8bit无符号长整型数据 <br>
- '.sd' ：代表64bit有符号长整型数据 <br>
- '.sw' : 代表32bit有符号长整型数据 <br>
- '.sh' : 代表16bit有符号长整型数据 <br>
- '.sb' : 代表8bit有符号长整型数据 <br>

浮点块中的所有详细微指令参见[浮点块指令集](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/fp_block/intro/)。

- 一般情况下浮点操作，其Opcode基本以**f**开头，在Opcode后扩展{.fd,.fs,.fh,.fb,.ud,.uw,.uh,.ub,.sd,.sw,.sh,.sb}表明微指令操作的数据类型。
- **cvt**微指令可用于不同的数据类型之间的转换，支持整型to整型、整型to浮点，浮点to整型，浮点to浮点。
- 浮点操作的舍入模式，由[CSTATE](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/register/ssr/CSTATE/?h=cstate)控制，默认浮点的舍入模式为就近舍入，如需切换舍入模式，需要配置CSTATE。

##汇编示例：

```
feq.fs t#1, a0, ->t            /*单精度浮点比较操作*/
cvt.fs2sw t#1, ->a1            /*将单精度浮点值转换成有符号32bit整型*/
b.feq.fs t#1, t#2, .Ljump      /*t#1和t#2相等时，跳转到.Ljump的位置*/
```
