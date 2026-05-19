# body address indication command: **B.TEXT**

```
B.TEXT <label>
```

Used to tell the assembler the location of the body instruction corresponding to this block instruction. <label> can be a symbol or an address value.

Example:<br>

```
B.TEXT .LBB0    /* ZXTERMZH40QXZ的第一条微指令的地址为‘.LBB0’ */
B.TEXT 0x20000  /* ZXTERMZH40QXZ的第一条微指令的地址为0x20000 */
```