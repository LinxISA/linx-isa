# ERCOV

## 说明

**异常恢复块（Exception Recovery）**

`ERCOV` 用于[向量数据块](../../blockIntro/vec_block/intro.md)或[访存数据块](../../blockIntro/mem_block/intro.md) 异常或中断处理完成后，从指定的Tile寄存器中恢复块内所有的上下文状态。

如果软件在异常处理过程中，将保存的异常块状态搬移至内存并做了修改，那么需要先通过[TLOAD](../tileblock/TLOAD.md)指令将异常块状态从内存空间加载到Tile寄存器中。然后再通过ERCOV恢复异常块的状态。

`ERCOV`是一条多输入指令，其中：

- 第一个输入Tile寄存器用于恢复异常块块内的私有寄存器，包括LB/LC寄存器、标量寄存器、向量寄存器、掩码寄存器等。
- 其他输入Tile寄存器用于恢复异常块自身的输出Tile寄存器内容。

与[ESAVE](./ESAVE.md)指令的输出Tile数量匹配，当前版本ERCOV指令最多有5个输入Tile寄存器。

## 汇编格式

```asm
ERCOV SrcTile0, SrcTile1, ..., SrcTile4
```

## 汇编符号说明

| 寄存器 | 说明 | 是否可选 |
|---------|--------|---------|
| **SrcTile0** | 第一个输入Tile寄存器。用于恢复异常块的块内私有寄存器 | 否 |
| **SrcTile1** | 第二个输入Tile寄存器。用于恢复异常块的第一个输出Tile寄存器内容。 | 是，如果异常块无输出Tile则不加该参数。|
| **SrcTile2** | 第三个输入Tile寄存器。用于恢复异常块的第二个输出Tile寄存器内容。 | 是，如果异常块没有第二个输出Tile则不加该参数。|
| **SrcTile3** | 第四个输入Tile寄存器。用于恢复异常块的第三个输出Tile寄存器内容。 | 是，如果异常块没有第三个输出Tile则不加该参数。|
| **SrcTile4** | 第五个输入Tile寄存器。用于恢复异常块的第四个输出Tile寄存器内容。 | 是，如果异常块没有第四个输出Tile则不加该参数。|

## 指令编码

本块指令将拆分成以下指令进行编码：

- BSTART.TEPL `ERCOV`
- [B.IOT](../../header/B.IOT.md) `SrcTile0, SrcTile1`
- [B.IOT](../../header/B.IOT.md) `SrcTile2, SrcTile3`
- [B.IOT](../../header/B.IOT.md) `SrcTile4, last`

BSTART.TEPL指令编码如下：

![BSTART.TEPL](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.TEPL.svg)

其中function字段编码方式为：

| function | 指令/PTO | 说明 |
|----------|----------|---------|
| 0-29 | RESERVE | 保留 |
| 30   | **ESAVE**   | 异常保存块，用于保存发生异常的Tile块的块内状态 |
| 31   | **ERCOV**   | 异常恢复块，用于恢复发生异常的Tile块的块内状态 |

## 执行示例

ERCOV模版块恢复异常块内状态的过程，通过伪代码示意如下：

### 恢复块内私有寄存器

```c++
/* --- 步骤1: 恢复Group间共享的寄存器状态 --- */
src_addr = base address of SrcTile;
// 恢复LB寄存器
for (int i = 0; i < 3; i++) do
    LB<i> = SrcTile[src_addr + 2*i];
end for

// 恢复形参寄存器：RI0~RI11，RO0~RO3
src_addr += 8;
for (int i = 0; i < 16; i++) do
    if (i < 12)
        RI<i> = SrcTile[src_addr + 8*i];
    else
        RO<i-12> = SrcTile[src_addr + 8*i]; 
end for

/* --- 步骤2. 恢复每个Group内私有的寄存器状 --- */
src_addr += 128;
// group_num是处理器中并行Group的数量。对于group间串行的块，该值固定为1。
for (int gid = 0; gid < group_num; gid++) do
    // 恢复当前Group的TPC
    TPC = SrcTile[src_addr + 0];

    // 恢复LC寄存器
    src_addr += 8;
    for (int i = 0; i < 3; i++) do
        LC<i> = SrcTile[src_addr + 2*i];
    end for

    // 恢复P寄存器
    P = SrcTile[src_addr + 8];

    // 恢复标量寄存器
    src_addr += 16;
    for (int i = 0; i < 8; i++) do
        if (i < 4) then
            T#<4-i> = SrcTile[src_addr + 8*i];
        else
            U#<8-i> = SrcTile[src_addr + 8*i];
    end for

    // 恢复向量寄存器
    src_addr += 64;
    for (int i = 0; i < 16; i++) do
        if (i < 4)
            VT#<4-i> = SrcTile[src_addr + 256*i];
        else if(i < 8)
            VU#<8-i> = SrcTile[src_addr + 256*i];
        else if(i < 12)
            VM#<12-i> = SrcTile[src_addr + 256*i];
        else
            VN#<16-i> = SrcTile[src_addr + 256*i];
    end for
    // 更新src_addr为下个group的首地址
    src_addr += 4184;
end for
```

### 恢复输出Tile寄存器状态

恢复异常块的Output Tile内容:
```
Output Tile0(Exception Block) <- SrcTile1(ERCOV);
Output Tile1(Exception Block) <- SrcTile2(ERCOV);
Output Tile2(Exception Block) <- SrcTile3(ERCOV);
Output Tile3(Exception Block) <- SrcTile4(ERCOV);
```

## 备注

异常数据块状态保存过程请见[ESAVE](./ESAVE.md)模版块介绍。
