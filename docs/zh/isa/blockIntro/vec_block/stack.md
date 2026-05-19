# 栈寄存器

由于向量数据块在内部不支持直接访问内存空间，并且不引入线程栈模型，一级架构中定义了一类 [Tile寄存器](../../register/common/tilereg.md)，标识为 **S（Stack Tile Register）**。S 寄存器用于在 Tile 块指令的函数调用语义下用于保存调用参数，并作为寄存器溢出（spill）的栈空间，从而在遵循向量块指令的无直接访存约束的同时，提供必要的临时存储能力，兼顾计算性能与可编程性。

## S寄存器使用方法

块头申请寄存器的方法：

- 与其他类型的Tile寄存器一样，块指令通过[B.IOT/B.IOTI](../../header/B.IOT.md)指令来申请使用S寄存器。
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
B.IOTI T#1, U#1, ->T<16KB>
B.IOTI last,     ->S<8KB>    # 每个group申请的S-Tile空间8KB
```

块内通过形参TS访存：
```asm
// Spill
l.sd vt#1.ud, [TS, lc0.uh<<3]
// Reload
l.ld [TS, lc0.uh<<3], ->vt.d
```

## 特殊情况

由于块指令的第二个输出Tile与栈空间寄存器（S-Tile）在块内对应同一个形参寄存器TO1/TS，因此多输出且需要使用S寄存器的块指令需要将`B.IOT xx, ->S`放置在第二个输出位置，否则将导致Tile形参寄存器初始化时出现冲突，触发**非法指令异常**。

错误示例1：
```asm
# 汇编：
    VPAR xx, ->S<1KB>, T<1KB>, T<1KB>, ..., T<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系
    B.IOT xx, ->T<1KB>    # 第1个输出Tile（T）与TO建立映射关系
    B.IOT xx, ->T<1KB>    # 第2个输出Tile（T）与TO1建立映射关系，出现冲突
    ...
    B.IOT xx, ->T<1KB>    # 第n个输出Tile（T）与TO7建立映射关系
```

错误示例2：
```asm
# 汇编：
    VPAR xx, ->T<1KB>, T<1KB>, S<1KB>, ..., T<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->T<1KB>    # 第1个输出Tile（T）与TO建立映射关系
    B.IOT xx, ->T<1KB>    # 第2个输出Tile（T）与TO1建立映射关系
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系，出现冲突
    ...
    B.IOT xx, ->T<1KB>    # 第n个输出Tile（T）与TO7建立映射关系
```

正确示例：
```asm
# 汇编：
    VPAR xx, ->T<1KB>, S<1KB>, T<1KB>, ..., T<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->T<1KB>    # 第1个输出Tile（T）与TO建立映射关系
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系
    B.IOT xx, ->T<1KB>    # 第2个输出Tile（T）与TO2建立映射关系
    ...
    B.IOT xx, ->T<1KB>    # 第n个输出Tile（T）与TO7建立映射关系
```

如果一个块指令没有输出Tile寄存器，但是需要申请S寄存器空间，那么可以使用如下方式申请：
```asm
# 汇编：
    VPAR xx, ->S<1KB>

# 展开指令：
    BSTART.VPAR
    B.IOT xx, ->S<1KB>    # 栈空间寄存器S与TS(TO1)建立映射关系
```
