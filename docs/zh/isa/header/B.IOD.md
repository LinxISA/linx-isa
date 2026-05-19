# B.IOD

## 说明

B.IOD(*Block Input and Output Dependency*)<br>
本指令用于并行块指令中表达对前序指令的依赖以及对后序指令产生屏障作用。

软件可以通过该指令表达并行块指令之间的依赖信息，避免块指令间过度并行化导致执行出错。

## 汇编语法

```asm
    B.IOD DepSrc, ->DepDst
```

## 汇编符号

- **DepSrc**：表示本块指令对前序输出至D的块指令的依赖。
- **DepDst**：表示本块指令对后序引用该标识的块指令的屏障。

## 编码格式

![B.IOD](../../figs/bitfield/svg/BlockHeader_32bit/B.IOD.svg)

依赖关系表:

| 输入输出编码 | DepSrc  | DepDst  |
|-------------|---------|---------|
| 5'b00000    | 无依赖   | 无输出  |
| 5'b00001    | D#1     | D       |
| 5'b00010    | D#2     | reserve |
| 5'b00011    | D#3     | reserve |
| 5'b00100    | D#4     | reserve |
| 5'b00101    | D#5     | reserve |
| 5'b00110    | D#6     | reserve |
| 5'b00111    | D#7     | reserve |
| 5'b01000    | D#8     | reserve |
| others      | reserve | reserve |

## 汇编示例

示例：
```asm
    ...
    TSTORE T#1, [a2], ->D            ; I0
    TLOAD [a3], D#1,  ->T<64B>       ; I1, 等待I0提交后执行
    TABS    T#1,        ->T<64B>       ; I2
    TLOAD [a3], D#1,  ->T<128B>, D   ; I3, 等待I0提交后执行
    ...
    TSTORE T#1, [a0], D#1            ; I4, 等待I3提交后执行
```
