# 块属性伪指令：**B.CATR**

```
B.CATR {TRAP, ATOMIC, <AQ, RL, AQRL>, FAR}
```

'B.CATR'指令告诉汇编器块属性：

- 不支持缺省写法，无额外块属性，则无需使用该指令
- 仅支持上述块属性的编码

支持的操作对象有{TRAP, ATOMIC, &lt;AQ, RL, AQRL&gt;, FAR}。原子属性的具体解释请见[块属性](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/header/B.CATR/)

示例：

```
B.CATR ATOMIC, AQ           /* 表示该块指令的属性是atomic+acquire属性，如果有多个属性，则用逗号进行分割*/
```
