# ESAVE

## 说明

**异常保存块（Exception Save）**

`ESAVE` 用于 [向量数据块](../../blockIntro/vec_block/intro.md) 或 [访存数据块](../../blockIntro/mem_block/intro.md) 执行过程中遇到异常或中断时，保存块内所有的上下文到指定的Tile寄存器中。如果软件需要进一步修改或查看这些状态，可通过 [TSTORE](../tileblock/TSTORE.md) 指令将保存至Tile寄存器的内容搬移到内存空间中。

`ESAVE`是一条多输出指令，其中：

- 第一个输出Tile寄存器用于保存异常块块内的私有寄存器，包括LB/LC寄存器、标量寄存器、向量寄存器、掩码寄存器等。
- 其他输出Tile寄存器用于保存异常块自身的输出Tile寄存器内容。

当前版本，由于向量数据块和访存Tile块最多可以有4个输出Tile寄存器，因此ESAVE指令最多可以有5个输出Tile寄存器。

## 汇编格式

```asm
ESAVE , ->DstTile0<32KB>, DstTile1<32KB>, ..., DstTile4<32KB>
```

## 汇编符号说明

| 寄存器 | 说明 | 是否可选 |
|---------|--------|---------|
| **DstTile0** | 第一个输出Tile寄存器。用于保存异常块的块内私有寄存器 | 否 |
| **DstTile1** | 第二个输出Tile寄存器。用于保存异常块的第一个输出Tile寄存器内容。 | 是，如果异常块无输出Tile则不加该参数。|
| **DstTile2** | 第三个输出Tile寄存器。用于保存异常块的第二个输出Tile寄存器内容。 | 是，如果异常块没有第二个输出Tile则不加该参数。|
| **DstTile3** | 第四个输出Tile寄存器。用于保存异常块的第三个输出Tile寄存器内容。 | 是，如果异常块没有第三个输出Tile则不加该参数。|
| **DstTile4** | 第五个输出Tile寄存器。用于保存异常块的第四个输出Tile寄存器内容。 | 是，如果异常块没有第四个输出Tile则不加该参数。|

## 指令编码

本块指令将拆分成以下指令进行编码：

- BSTART.TEPL `ESAVE`
- [B.IOT](../../header/B.IOT.md) `, ->DstTile0<32KB>`
- [B.IOT](../../header/B.IOT.md) `, ->DstTile1<32KB>`
- [B.IOT](../../header/B.IOT.md) `, ->DstTile2<32KB>`
- [B.IOT](../../header/B.IOT.md) `, ->DstTile3<32KB>`
- [B.IOT](../../header/B.IOT.md) `last, ->DstTile4<32KB>`

BSTART.TEPL指令编码如下：

![BSTART.TEPL](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.TEPL.svg)

其中function字段编码方式为：

| function | 指令/PTO | 说明 |
|----------|----------|---------|
| 0-29 | RESERVE | 保留 |
| 30   | **ESAVE**   | 异常保存块，用于保存发生异常的Tile块的块内状态 |
| 31   | **ERCOV**   | 异常恢复块，用于恢复发生异常的Tile块的块内状态 |

## 执行示例

ESAVE模版块保存异常块内状态的过程，通过伪代码示意如下：

### 保存块内私有寄存器

将异常块的块内私有寄存器状态保存至ESAVE的第一个输出Tile寄存器中：
```c++
/* --- 步骤1：保存Group间共享的寄存器状态 --- */
dst_addr = base address of DstTile0;
// 保存LB寄存器
for (int i = 0; i < 3; i++) do
   DstTile[dst_addr + 2*i] = LB<i>;
end for
// 保存RI0~RI11, RO0~RO3
dst_addr += 8;
for (int i = 0; i < 16; i++) do
   if (i < 12)
      DstTile[dst_addr + 8*i] = RI<i>;
   else
      DstTile[dst_addr + 8*i] = RO<i-12>; 
end for

/* --- 步骤2：保存每个Group内私有的寄存器状态 --- */
dst_addr += 128;
// group_num是处理器中并行Group的数量。对于group间串行的块，该值固定为1。
for (int gid = 0; gid < group_num; gid++) do
   // 保存当前Group的TPC
   DstTile[dst_addr + 0] = TPC;

   // 保存LC寄存器
   dst_addr += 8;
   for (int i = 0; i < 3; i++) do
      DstTile[dst_addr + 2*i] = LC<i>;
   end for

   // 保存P寄存器
   DstTile[dst_addr + 8] = P;

   // 保存标量寄存器
   dst_addr += 16;
   for (int i = 0; i < 8; i++) do
      if (i < 4) then
         DstTile[dst_addr + 8*i] = T#<4-i>;
      else
         DstTile[dst_addr + 8*i] = U#<8-i>;
   end for

   // 保存向量寄存器
   dst_addr += 64;
   for (int i = 0; i < 16; i++) do
      if (i < 4)
         DstTile[dst_addr + 256*i] = VT#<4-i>;
      else if(i < 8)
         DstTile[dst_addr + 256*i] = VU#<8-i>;
      else if(i < 12)
         DstTile[dst_addr + 256*i] = VM#<12-i>;
      else
         DstTile[dst_addr + 256*i] = VN#<16-i>;
   end for

   // 更新dst_addr为下个group的首地址
   dst_addr += 4184;
end for
```

### 保存输出Tile的内容

由于发生异常或中断时，异常块的输出Tile寄存器的内容还没有更新/提交到一层架构状态中，如果此时进行状态迁移以及调度，那么发生异常前已经写过的Tile寄存器的内容将丢失。因此这些状态需要通过ESAVE模版块保存起来。

保存内容如下：
```
DstTile1(ESAVE) <- Output Tile0(Exception Block);
DstTile2(ESAVE) <- Output Tile1(Exception Block);
DstTile3(ESAVE) <- Output Tile2(Exception Block);
DstTile4(ESAVE) <- Output Tile3(Exception Block);
```

## 备注

异常数据块状态恢复过程请见[ERCOV](./ERCOV.md)模版块介绍。
