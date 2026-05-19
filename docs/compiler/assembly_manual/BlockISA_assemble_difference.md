Linx Instruction Set Architectureblock instruction is a two-layer architecture, consisting of header and optional microinstructions (see example (1) below). For other architectures, usually one assembly statement corresponds to one instruction, see example (2) below.

(1)*LinxISA compilation*<br>

The attributes of the current block instruction (type, jump type, input, output, microinstruction storage address, etc.) are expressed through the pseudo-instruction sequence of header. There are two block instruction assembly layouts of LinxISA:

- Integrated block or template block: When block instruction has specific calculations, the body instructions are arranged immediately after header instruction.

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

- Separate block: When there is a specific calculation for block instruction, use the *B.TEXT* instruction to specify the starting address of the body instruction, and use *bstop* to indicate the end position of the body instruction. The separation block provides greater freedom in the arrangement of body.
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

(2) *Other architecture compilation*<br>

```
x86:   add     eax, #100
68K:   ADD     #100, D0
ARM:   add     r0, r0, 100
```