# 微指令汇编指令

微指令的汇编syntax,请见：[灵犀指令集手册](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/)。下面按照公有微指令及私有微指令进行详细说明：公有微指令指所有的基本块类型中均可以使用，私有微指令指只能在对应的块类型中使用。

**Note**: 在微指令汇编syntax的描述中<br>

- SrcL代表左源操作对象，语法类型为寄存器，可能是LL_GPR或者UL_GPR中的任意一个<br>
- SrcR代表右源操作对象，语法类型为寄存器，可能是LL_GPR或者UL_GPR中的任意一个<br>
- shamt代表偏移值，语法类型为立即数。
- simm 代表有符号立即数，语法类型为表达式（立即数或者标签）
- uimm 代表无符号立即数，语法类型为表达式（立即数或者标签）
