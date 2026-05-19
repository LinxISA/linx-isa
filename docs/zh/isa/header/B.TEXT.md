# B.TEXT

## 说明

块体偏移(*Block Text*)
本指令用于分离块块头中指定**块体的位置**，块体位置通过程序标签表达。

## 汇编语法

```asm
    B.TEXT label
```

## 汇编符号

- label表示块体起始位置的地址标签，其相对于本指令PC的偏移量除以2后编码于simm25字段。

## 编码格式

![B.TEXT](../../figs/bitfield/svg/BlockHeader_32bit/B.TEXT.svg)

## 块体起止PC

**块体的起始PC**
```
    // 块体中第一条微指令的TPC
    BTextOffset = simm25 << 1;
    START_TPC = B.TEXT_PC + BTextOffset;
```
**块体的结束PC**：分离块块体结束由BSTOP指令指示，块体的结束PC为BSTOP指令的PC。

## 备注

- 本指令仅用于分离块的块头中。
- 本指令必须作为块头中最后一条指令，否则后序指令会被视为无效。
