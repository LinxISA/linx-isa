# Inline assembly
In general, clang is highly compatible with GCC's inline assembly extensions, allowing the same constraints, modifiers, and operands as GCC's inline assembly. This section mainly introduces the common writing methods of inline assembly based on LinxISA. Generic inline assembly format:

```
 asm [ volatile ] (  
         汇编序列
         [ : 输出操作数 ]                      /* 可选 */
         [ : 输入操作数  ]                     /* 可选 */
         [ : list of clobbered registers ]     /* 可选 */
         );
```

The basic format mainly includes four parts, which must contain assembly sequences, and other parts are optional. The assembly diagram is as follows:

```
void foo(void)
{
   int output, val1, val2;
   ...
   asm volatile ("BSTART\n"
        "sub %1, %2, ->t\n"
        "add a1, t#1, ->%0\n"
        "BSTOP\n"
        :"=r"(output):"r"(val1),"r"(val2):);
   ...
   return;
}
```

'volatile' is an optional keyword, indicating that the compiler does not require any optimization of the following assembly code. The keyword also supports the writing methods of '__asm__' and '__volatile__'. The following table shows the operand type description and modification of the output operand:

| Operand constraints | Description |
|------------|--------------------------|
| r | Operand of register type |
| i | Operand of immediate type |
| m | Operand of memory type |


| Modification Constraints | Description |
|------------|--------------------------|
| = | Output operand (write only) |
| + | Input/output operands (read and write) |

# Parallel block inline assembly
Supports writing single-instruction parallel block inline assembly. The purpose is to facilitate support for fp8 type conversion, so that it can be supported by just modifying the library.

Input:

```c
void __vec__ foo(...) {
  asm volatile ("l.fcvt %1.fd, ->%0.fb" : "=vr"(to) : "vr"(from));
  p[...] = to;
}
```

Output:

```s
foo:
  l.fcvt vt#1.fd, ->vt.fb
  l.sb vt#1.sb, [...]
```

**Constraints:** Only a single microinstruction is supported. If multiple microinstructions are written, the backend will have an error when calculating the register index.

---

Inline assembly error reporting rules:

1. Standard block: Inline assembly starting with scalarBSTART or template block. No special checks are performed for the time being, and you can write casually.
2. Tile instruction: Inline assembly starting with Tile pseudo-instruction or BSTART.PAR. Only block modification instructions are received. When encountering microinstructions or non-block modification instructions such as the new header, an error will be reported directly.
3. Parallel block instruction multiple instructions: Start with a microinstruction. If there are multiple microinstructions, they must end with bstop. Used to hand-write complete parallel block function bodies through inline assembly
4. Parallel block instruction single instruction: only one microinstruction
5. Escape: The error reporting rules may be expanded or changed in the future. First provide the `.unsafeasm` directive to ensure that these rules can be bypassed.
> If you have any questions about parallel block inline assembly, please contact Mou Liangyu 30030301