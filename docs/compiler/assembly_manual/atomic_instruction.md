# System block private microinstructions

The private microinstructions of the system block include system register operations, execution control, cache management operations, atomic operations, etc. For detailed microinstruction description, please refer to the chapter [System Block Private Instructions] (../../isa/blockIntro/sys_block/instlist.md).

## Atomic instructions

### Atomic access calculation instructions

```
Opcode [Operand0],Operand1                        /* 无输出 */    
Opcode [Operand0],Operand1,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR的T/U寄存器 */
```

- Add the extension after Opcode: Opcode{.aq, .rl, .aqrl} to specify the access sequence restriction. <br>
	- '.aq': Sequential restrictions on subsequent instructions accessing storage. (0)<br>
	- '.rl': Sequential restrictions on accessing storage by previous instructions. (1)<br>
	- '.aqrl': The order in which post-order and pre-order instructions access storage is restricted. (2)<br>
- '[]' means using the register value as the address<br>

Example:<br>
(0)
```
ld.add.aq [a1],a2,->t      /* 以寄存器a2的值为地址的内存中加载64bit的数据与右源操作数相加，将结果写回到以左源寄存器的值为地址的内存中，将加载的数据写到目的T寄存器中  */
```

(1)
```
ld.add.rl [a1],a2,->t
```

(2)
```
ld.add.aqrl [a1],a2,->a2
```
### Atomic storage calculation instructions

```
Opcode [Operand0],Operand1               /* 无输出 */    
```

- Atomic storage calculation instructions can only use ‘.rl’ (0)<br>
- '[]' means using the register value as the address <br>

(0)
```
sw.add.rl [a1],a2           /* 从以寄存器a1的值为地址的内存原子加载32bit的数据，与右源寄存器低32bit的值相加后，将结果写回到以左源寄存器的值为地址的内存中 */
```

### Atomic memory access instructions

```
Opcode [Operand0], ->{LL_GPR, UL_GPR}                  /* 原子内存访问(0)  */
Opcode Operand0,[Operand1]                             /* 原子内存存储(1)  */
```

- '[]' means using the register value as the address <br>

(0)
```
lr.w.aqrl [t#1], ->t
```

(1)

```
sc.d.aqrl t#1,[t#2],->s2
```

## CMO (Cache Management Operation)

```
Opcode
Opcode Operand0                   /*带操作数的CMO指令*/
```

Assembly instructions:
```
dc.iva a0                        /*根据a0中的地址无效cache中地址对应的cacheline*/
ic.iall                          /*无效微指令cache中的数据*/
```

## system register operation

```
Opcode Operand0, ->{LL_GPR, UL_GPR}
Opcode Operand0, Operand1
```

Assembly example:

```
ssrget 0x0010, ->t             /*加载tp寄存器的值到t刻度尺寄存器
```

## Execution control class

```
Opcode
Opcode Operand0
Opcode Operand0, Operand1
```

Assembly instructions:

```
bse t#1                         /*发送t#1中的事件*/
```