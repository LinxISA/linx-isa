# 比较，分支， 跳转
## 比较指令
通常有左源以及右源两个输入的操作对象，一个输出

```
Opcode Operand0,Operand1,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者UL_GPR中 */
```
在Opcode后面加上：{.eq, .ne, .lt, .ge, .and, .or}来表明判断成立的条件 <br>

- '.eq'表示相等则判断成立。<br>
- '.ne'表示不相等则判断成立。<br>
- '.lt'表示左源小于右源则条件成立。<br>
- '.ge'表示左源大于等于右源则条件成立。<br>
- '.and'表示左源和右源均非零时则条件成立。
- '.or'表示左源和右源中只要有一个非零则条件成立。
- 在'.eq, .ne, .lt, .ge'的基础上加上'u'表明做无符号比较。
- 在'.eq, .ne, .lt, .ge, .and, .or'的基础上加上‘i’表明右源操作对象为立即数`<br>

详细汇编微指令可以参见手册[比较指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/compare/)。

汇编示意：

```
cmp.lt t#1, t#2, ->t                  /**/
cmp.ltu t#1, t#2, ->t                 /**/
cmp.lti t#1, 5, ->t                   /**/
```

## 分支指令
通常有左源以及右源两个输入的操作对象，一个分支跳转目标

```
Opcode Operand0,Operand1,Operand2 
```

在Opcode后面加上：{.eq, .ne, .lt, .ge}来表明判断成立的条件 <br>

- '.eq'表示相等则判断成立<br>
- '.ne'表示不相等则判断成立<br>
- '.lt'表示左源小于右源则条件成立<br>
- '.ge'表示左源大于等于右源则条件成立<br>
- 在此基础上加上'u'表明做无符号比较。<br>

详细的汇编微指令可以参见[块内跳转指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/branch/)。

汇编示意：

Operand2 是个立即数，可以写成标签(0), 立即数(1) 两种形式。<br>
(0)
```
    .Ltogo:
    ...
    ...
    b.eq a1,a2,.Ltogo     /* 如果a1 == a2 成立，块内跳转到.Ltogo的位置  */
```

(1)
```
    b.eq a1,a2,0x20000    /* 如果a1 == a2 成立，块内跳转到0x20000的位置(0x20000为绝对地址) */
```

## 跳转指令

```
Opcode Operand0                    /*直接跳转，Operand0可以写成立即数或者符号*/
Opcode Operand0,Operand1           /*间接跳转*/
```

- 直接跳转时操作对象Operand0为立即数<br>
- 间接跳转时操作对象Operand0为寄存器，Operand1为立即数。<br>

详细的汇编微指令可以参见[块内跳转指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/branch/)。

汇编示例：

```
jr t#1, 4              /*跳转到t#1+4的位置*/
j .Ljump               /*直接跳转到.Ljump标签的位置*/
```
