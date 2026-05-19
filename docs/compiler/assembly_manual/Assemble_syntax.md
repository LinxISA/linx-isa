The LinxISA assembler source file consists of a series of assembly statements, one statement per line. Each line of statement has three optional parts, in the following order:<br>

```
标签: 指令 /* 注释 */

```

**Tag** identifies the address of this instruction and is then used as the target for branch instructions or load and store instructions. **Instructions** can be LinxISA assembly instructions or assembler built-in instructions (the assembler built-in instructions are pseudo-instructions used to tell the assembler itself to perform segment alignment or create data, see the assembler built-in instructions section below for details). Use "/*" and "*/" as comment separators.

As shown in the following block assembly statement:<br>

```
.Ltmp0:                   /* 标签     */
...
BSTART.STD COND, .Ltmp0   /*  指令   */
addi zero,32, ->t
sll t#1, a0, ->t
sra t#1,t#2, ->u
addi zero,32, ->t
sll u#1, t#1, ->t
srli t#1,30, ->u
1: addi a1,4,->a3         /* 数字标签 + 指令 */
...
BSTOP
```