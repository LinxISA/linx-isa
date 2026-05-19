# 状态标志和条件执行

通过'setc'类的微指令用于修改CARG寄存器，在块指令提交时，根据块指令的跳转类型及CARG寄存器中的值，执行对应的路径。当块指令的跳转为'COND'、'IND'、'ICALL'时，块体需使用'setc'类微指令。

例如想要让一个块在满足条件时跳转到另一个块，不满足条件则fall through到下一个块运行。应该在块头指明跳转类型及跳转目标地址，可以用’BSTART.<type> COND, label’伪指令来表达，并且在块体微指令中加上条件类的‘setc’指令来设置条件状态,CARG寄存器的详细内容参见[CARG寄存器](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/register/common/bstate_com/?h=carg#carg)。下面给出一个个示例：

```
    ...
.Lblock1:
    BSTART COND, .Lblock2
    微指令
    setc.eq t#1, zero
    BSTART IND
    微指令
    setc.tgt t#1
    ...
    BSTART ICALL
    微指令
    addpc t#1,4,->ra
.Lblock2:
    BSTART
    ...
    BSTOP
    ...
```
