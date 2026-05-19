# Block attribute directive: **B.CATR**

```
B.CATR {TRAP, ATOMIC, <AQ, RL, AQRL>, FAR}
```

The 'B.CATR' directive tells the assembler about block attributes:

- The default writing method is not supported and there is no additional block attribute, so there is no need to use this command.
- Only encodings for the above block attributes are supported

Supported operation objects are {TRAP, ATOMIC, <AQ, RL, AQRL>, FAR}. For a detailed explanation of atomic attributes, please see [Block Attributes](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/header/B.CATR/)

Example:

```
B.CATR ATOMIC, AQ           /* 表示该ZXTERMZH32QXZ的属性是atomic+acquire属性，如果有多个属性，则用逗号进行分割*/
```