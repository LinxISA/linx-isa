# PC calculation instructions

```
Opcode Operand0,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR或者是UL_GPR */
```

- When calculating TPC, the operation object Operand0 is an immediate number, which supports the value operation of constant values and immediate numbers. Obtain the relative TPC value: '%tpcrel_hi(symbol)' means to obtain the symbol address that is 20 bits higher than the current TPC, and '%got_tpcrel_hi(symbol)' means to obtain the symbol's entry address in the GOT table that is 20 bits higher than the current TPC<br>
- For blocks with a jump type of 'call', the 'addpc' instruction needs to be added to body to update ra to indicate the return address of 'call'

For specific microinstruction descriptions, please refer to the chapter [PC Computing Instructions] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/common/pc_arithmetic/).

Assembly instructions

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