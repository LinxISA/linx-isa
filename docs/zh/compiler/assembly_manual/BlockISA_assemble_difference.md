灵犀指令集架构块指令为两层架构，由块头和可选的微指令部分组成见下面示例（1）。其他架构，通常一条汇编语句与一条指令一一对应见下面示例（2）

（1）*灵犀指令集汇编*<br>

通过块头的伪指令序列来表达当前块指令的属性（种类，跳转类型，输入，输出，微指令存储地址等信息）,灵犀指令集的块指令汇编layout有两种：

- 一体块or模板块：当块指令存在具体的计算时，块体指令紧接着块头指令排布。

```
BSTART.STD FALL
addi zero,32,->t
sll t#1, a0,->t
sra t#1,t#2,->t
addi zero,32,->t
sll t#2, t#1,->t
srli t#1,30,->a3
MCOPY [a0,a1,a2]
BSTART.STD FALL
...
```

- 分离块：当块指令存在具体的计算时，利用*B.TEXT*指令指定块体指令的起始地址，用*bstop*指示块体指令的结束位置。分离块为块体的排布提供了更大的自由度。
```
BSTART.STD FALL
B.TEXT .Ltmp0.bstart
BSTART.STD FALL
...

.Ltmp0.bstart:
addi zero,32,->t
sll t#1, a0,->t
sra t#1,t#2,->t
addi zero,32,->t
sll t#2, t#1,->t
srli t#1,30,->a3
bstop
```

（2）*其他架构汇编*<br>

```
x86:   add     eax, #100
68K:   ADD     #100, D0
ARM:   add     r0, r0, 100
```
