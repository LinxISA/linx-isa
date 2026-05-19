# PC计算指令

```
Opcode Operand0,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者是UL_GPR */
```

- TPC计算时操作对象Operand0为立即数，支持常量值和立即数的取值操作，获取相对TPC值：’%tpcrel_hi(symbol)‘表示获得symbol地址相对于当前TPC的高20bit, ’%got_tpcrel_hi(symbol)‘表示获得symbol在GOT表上的表项地址相对于当前TPC的高20bit<br>
- 对于跳转类型为'call'的块，块体中需要加上'addpc'指令更新ra，来指示'call'的返回地址

具体的微指令描述可以参见[PC计算指令](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/pc_arithmetic/)这一章节。

汇编示意

(0)

```
addtpc %tpcrel_hi(symbol),->t      /* 获得symbol的地址相对于当前微指令tpc的偏移值，高20位编码  */
```

(1)

```
addtpc %got_tpcrel_hi(symbol),->t  /* 获得symbol的GOT表的地址相对于当前微指令tpc的偏移值，高20位编码  */
```

(2)
```
addpc 4, ->ra                      /* 当前微指令的tpc+4写到ra寄存器中*/
```
