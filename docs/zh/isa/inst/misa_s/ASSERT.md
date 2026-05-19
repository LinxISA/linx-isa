# ASSERT

## 说明
断言指令(*Assertion instruction*)  
如果输入寄存器SrcL的值为0，则触发断言异常。该异常可以被自修复块捕获。

## 汇编语法

```
    assert SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![ASSERT](../../../figs/bitfield/svg/Instruction_32bit/ASSERT.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) operand = R[m, datawidth];

    if operand == 0 then
        assert();
```

## 示例

该指令需要配合cmp指令使用，用于检查比较结果是否为真。

```asm
    # 两寄存器比较
    cmp.eq a1, a2, ->a1
    assert a1
    cmp.eq a1, a2, ->t
    assert t#1
    cmp.eq a1, a2, ->u
    assert u#1
    # 寄存器与立即数比较
    cmp.nei a1, 0x80, ->a1
    assert a1
    cmp.nei a1, 0x80, ->t
    assert t#1
    cmp.nei a1, 0x80, ->u
    assert u#1
```

如果本块指令内有Fixup，则跳转到Fixup指定的label上。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
