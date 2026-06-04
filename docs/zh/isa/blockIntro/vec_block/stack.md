# 栈寄存器

由于向量数据块在内部不支持直接访问内存空间，并且不引入线程栈模型，一级架构中定义了一类 [Tile寄存器](../../register/common/tilereg.md)，标识为 **S（Stack Tile Register）**。S 寄存器用于在 Tile 块指令的函数调用语义下用于保存调用参数，并作为寄存器溢出（spill）的栈空间，从而在遵循向量块指令的无直接访存约束的同时，提供必要的临时存储能力，兼顾计算性能与可编程性。

## S寄存器使用方法

块头申请寄存器的方法：

- 与其他类型的 Tile 寄存器一样，块指令通过规范的 [B.IOT](../../header/B.IOT.md) 描述符来申请使用 S 寄存器。
- S寄存器被申请它的块指令所私有，即S寄存器只对本块可见，其他块不可见。
- S寄存器随着申请它的块指令提交而释放。
- B.IOT指令上申请的是一个Group内使用的栈空间大小，S寄存器总空间大小需要硬件计算。
  
注意：**S寄存器Group容量乘以Group的个数得到的S寄存器的总空间大小，并且该空间大小不能超过512KB**。

块内使用形参寄存器访存：

- 申请了S寄存器的块指令，其块内通过形参寄存器 **TS** 与S寄存器建立映射关系。
- 块内可以通过load/store local指令对 TS 寄存器进行读或写。
- TS指向当前group内对应的栈空间。

注意：**如果块内读取的是未初始化的TS，返回值是不确定的**。

## 编程示例

块指令申请`S寄存器`的示例如下：
```
VPAR <LB0:64, LB1:64>, T#1, U#1, ->T<16KB>, S<8KB>
// 展开形式
BSTART.VPAR
B.DIM zero, 64,  ->LB0
B.DIM zero, 64,  ->LB1
B.IOT T#1, U#1, ->T<16KB>
B.IOT last,     ->S<8KB>    # 每个group申请的S-Tile空间8KB
```

块内通过形参TS访存：
```asm
// Spill
l.sd vt#1.ud, [TS, lc0.uh<<3]
// Reload
l.ld [TS, lc0.uh<<3], ->vt.d
```

## S-Tile 与输出 Tile 的关系

TS 是独立的栈空间形参寄存器，与输出形参寄存器（TO~TO3）不再共用槽位。因此 S-Tile 的申请位置不受输出 Tile 的数量和顺序限制，可以任意放置在输出列表中。

任意位置申请 S 寄存器的示例：
```asm
# 多输出 + 栈空间 — S 可放在任意位置
    VPAR xx, ->T<1KB>, S<1KB>, T<1KB>, ..., T<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->T<1KB>    # 第1个输出Tile（T）与TO建立映射关系
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS建立映射关系（独立于输出）
    B.IOT xx, ->T<1KB>    # 第2个输出Tile（T）与TO1建立映射关系
    ...
    B.IOT xx, ->T<1KB>    # 第n个输出Tile（T）与TO3建立映射关系
```

无输出仅申请栈空间：
```asm
# 汇编：
    VPAR xx, ->S<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS建立映射关系
```
