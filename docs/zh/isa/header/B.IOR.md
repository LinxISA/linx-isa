# B.IOR

## 说明

B.IOR(*Block Input and Output Register*)<br>
本指令用于分离块块头中定义块指令输入和输出的[全局寄存器](../register/common/ggpr.md)。每条指令最多指定三个输入寄存器，一个输出寄存器。

通过解析该指令提供的寄存器使用信息，处理器可以更早地解除块指令之间的寄存器依赖，调度块指令并行执行。

## 汇编语法

```asm
    B.IOR SrcReg0, SrcReg1, SrcReg2, ->RegDst
```

## 汇编符号

- **SrcReg0, SrcReg1, SrcReg2**：表示本块指令输入的3个[全局寄存器](../register/common/ggpr.md)。
- **RegDst**：表示本块指令输出的[全局寄存器](../register/common/ggpr.md)。

## 编码格式

![B.IOR](../../figs/bitfield/svg/BlockHeader_32bit/B.IOR.svg)

- **RegSrc0，RegSrc1和RegSrc2**：这3字段分别用于编码输入寄存器，编码为0时表示无效。
- **RegDst**：该字段用于编码输出寄存器，编码为0时表示无效。

输入输出寄存器字段的编码方式如下：

| 编码 | RegSrc | RegDst |
|------|--------|---------|
| 0 | invalid | invalid |
| n = [1, 23] | R[n] | R[n] |
| >23 | reserve | reserve

## 汇编示例

在块头中使用B.IOR指令指定三个输入`a0, a1, a4`和两个输出`a2, a3`。
```asm
    BSTART.VPAR
    B.IOR a0, a1, a4, ->a2
    B.IOR , ->a3
    B.TEXT 1f
    ...
```

系统调用块XB中B.IOR的使用：
```asm
    XB ACR0, 20
    B.IOR a0, a2, ->a1
    BSTOP 或 BSTART
```

## 注意事项

1. 允许一个块指令使用多条B.IOR指令编码本块的输入输出寄存器。
2. B.IOR指令定义了重复的输入寄存器或重复的输出寄存器，那么汇编器应报错。
3. B.IOR指令定义了重复的输入寄存器或重复的输出寄存器，硬件解析后应报异常。
4. 分离块块体中访问了没有使用B.IOR定义的寄存器，硬件应报异常。
5. 本指令用于一体块会导致输入输出寄存器定义状态不可知。
