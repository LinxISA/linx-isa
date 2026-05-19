# Example

block instruction of LinxISA consists of header and optional microinstruction part. If block instruction requires some specific calculation operations, header needs to be linked to the corresponding microinstructions. Currently, two layout forms are supported: one is an integrated block, that is, header instruction is followed by the microinstruction; the other is a separated block, which determines the location of the microinstruction by adding a pointer to the starting address of the microinstruction in header. Among the assembly instructions corresponding to the separated block, the corresponding microinstruction can be found through the label given by 'B.TEXT'.

Example of assembly input for a block:
```
.foo:
    BSTART               /* 跳转类型为FALL的标准块*/
    微指令
    BSTART IND           /* 跳转类型为间接跳转的标准块*/
    微指令
    setc.tgt t#1
    ...
    BSTOP
```

Assembly input example for separated blocks:

header：

```
...
...
    BSTART
    loop.set a0, 0, ->LC0
.foo:
    BSTART.SIMT FALL
    B.TEXT .Lbody.bstart
    BSTOP
...
...
```

Microinstructions:
```
...
...
.Lbody.bstart:
    微指令
    lbstop
...
...
```