# 系统块私有微指令

系统块的私有微指令包括系统寄存器操作、执行控制、cache管理操作、原子操作等。详细的微指令描述可以参见[系统块私有指令](../../isa/blockIntro/sys_block/instlist.md)这一章节。

## 原子指令

### 原子访问计算类指令

```
Opcode [Operand0],Operand1                        /* 无输出 */    
Opcode [Operand0],Operand1,->{LL_GPR, UL_GPR}     /* 输出到LL_GPR的T/U寄存器 */
```

- 在Opcode后面加上扩展：Opcode{.aq, .rl, .aqrl}来指明访存顺序限制。<br>
	- '.aq'：后序指令访问存储的顺序限制。(0)<br>
	- '.rl'：前序指令访问存储的顺序限制。(1)<br>
	- '.aqrl': 后序前序指令访问存储的顺序受限。(2)<br>
- '[]'表示使用寄存器值作为地址<br>

示例：<br>
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
### 原子存储计算类指令

```
Opcode [Operand0],Operand1               /* 无输出 */    
```

- 原子存储计算类指令，只能使用‘.rl’ (0)<br>
- '[]'表示使用寄存器值作为地址 <br>

(0)
```
sw.add.rl [a1],a2           /* 从以寄存器a1的值为地址的内存原子加载32bit的数据，与右源寄存器低32bit的值相加后，将结果写回到以左源寄存器的值为地址的内存中 */
```

### 原子访存指令

```
Opcode [Operand0], ->{LL_GPR, UL_GPR}                  /* 原子内存访问(0)  */
Opcode Operand0,[Operand1]                             /* 原子内存存储(1)  */
```

- '[]'表示使用寄存器值作为地址 <br>

(0)
```
lr.w.aqrl [t#1], ->t
```

(1)

```
sc.d.aqrl t#1,[t#2],->s2
```

## CMO(Cache Management Operation)

```
Opcode
Opcode Operand0                   /*带操作数的CMO指令*/
```

汇编示意：
```
dc.iva a0                        /*根据a0中的地址无效cache中地址对应的cacheline*/
ic.iall                          /*无效微指令cache中的数据*/
```

## 系统寄存器操作

```
Opcode Operand0, ->{LL_GPR, UL_GPR}
Opcode Operand0, Operand1
```

汇编示例：

```
ssrget 0x0010, ->t             /*加载tp寄存器的值到t刻度尺寄存器
```

## 执行控制类

```
Opcode
Opcode Operand0
Opcode Operand0, Operand1
```

汇编示意：

```
bse t#1                         /*发送t#1中的事件*/
```

