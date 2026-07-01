# 原子指令

原子指令，也称为原子操作或者是原子性指令，是指在多处理器系统或多线程环境中执行时不会被中断的操作，即操作要么完全执行，要么完全不执行。因为这些环境中可能有多个处理器或线程同时访问共享资源。原子指令可以确保这些操作不会被打断或部分执行，从而避免数据不一致和出现不可预测的结果。一条原子指令往往包含一组操作，这样可以提高指令集的效率、简化编程模型、减少指令流水线的开销、以及提高处理器的吞吐量。

系统块中原子指令目前主要包含以下几种：

## LOAD.OP类指令

LOAD.OP类指令从左源寄存器SrcL指定的内存位置读出32或64位的值，将其写入目的寄存器。然后将这个读出的值与右源寄存器SrcR的值**执行相应的操作**（例如相加，按位与等），计算结果存入SrcL寄存器指定的内存中，并且**保证这些步骤都是原子的**。

|     微指令    |         汇编格式                          |     描述       |
|--------------|-------------------------------------------|----------------|
|  LW.ADD   |  lw.add<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  **加**内存字写回，输出原内存字      |
|  LW.AND   |  lw.and<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  **与**内存字写回，输出原内存字      |
|  LW.OR    |  lw.or<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  **或**内存字写回，输出原内存字      |
|  LW.XOR   |  lw.xor<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  **异或**内存字写回，输出原内存字    |
|  LW.SMAX  |  lw.smax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存字比较**有符号最大值**写回，输出原内存字  |
|  LW.UMAX  |  lw.umax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存字比较**无符号最大值**写回，输出原内存字  |
|  LW.SMIN  |  lw.smin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存字比较**有符号最小值**写回，输出原内存字  |
|  LW.UMIN  |  lw.umin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存字比较**无符号最小值**写回，输出原内存字  |
|  LD.ADD   |  ld.add<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  **加**内存双字写回，输出原内存双字      |
|  LD.AND   |  ld.and<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  **与**内存双字写回，输出原内存双字      |
|  LD.OR    |  ld.or<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  **或**内存双字写回，输出原内存双字      |
|  LD.XOR   |  ld.xor<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  **异或**内存双字写回，输出原内存双字    |
|  LD.SMAX  |  ld.smax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存双字比较**有符号最大值**写回，输出原内存双字  |
|  LD.UMAX  |  ld.umax<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存双字比较**无符号最大值**写回，输出原内存双字  |
|  LD.SMIN  |  ld.smin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存双字比较**有符号最小值**写回，输出原内存双字  |
|  LD.UMIN  |  ld.umin<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}    |  内存双字比较**无符号最小值**写回，输出原内存双字  |

LOAD.OP类原子指令可以通过"aq"和"rl"两个后缀来添加额外的内存访问顺序限制，以保证内存访问的一致性。具体定义请见“内存访问限制参数表”。

![AtomicLoad](../../../figs/bitfield/svg/Introduction_32bit/AtomicLoad.svg)

## STORE.OP类指令

STORE.OP类指令与LOAD.OP类指令基本功能相同，只不过**没有目的寄存器**，不会返回指定内存位置上没有修改之前的值。

|     微指令    |         汇编格式                          |     描述       |
|--------------|-------------------------------------------|----------------|
|  SW.ADD   |  sw.add<{.rl}> [SrcL], SrcR   |  **加**内存字写回      |
|  SW.AND   |  sw.and<{.rl}> [SrcL], SrcR   |  **与**内存字写回      |
|  SW.OR    |  sw.or<{.rl}> [SrcL], SrcR    |  **或**内存字写回      |
|  SW.XOR   |  sw.xor<{.rl}> [SrcL], SrcR   |  **异或**内存字写回    |
|  SW.SMAX  |  sw.smax<{.rl}> [SrcL], SrcR    |  内存字比较**有符号最大值**写回  |
|  SW.UMAX  |  sw.umax<{.rl}> [SrcL], SrcR    |  内存字比较**无符号最大值**写回  |
|  SW.SMIN  |  sw.smin<{.rl}> [SrcL], SrcR    |  内存字比较**有符号最小值**写回  |
|  SW.UMIN  |  sw.umin<{.rl}> [SrcL], SrcR    |  内存字比较**无符号最小值**写回  |
|  SD.ADD   |  sd.add<{.rl}> [SrcL], SrcR   |  **加**内存双字写回      |
|  SD.AND   |  sd.and<{.rl}> [SrcL], SrcR   |  **与**内存双字写回      |
|  SD.OR    |  sd.or<{.rl}> [SrcL], SrcR    |  **或**内存双字写回      |
|  SD.XOR   |  sd.xor<{.rl}> [SrcL], SrcR   |  **异或**内存双字写回    |
|  SD.SMAX  |  sd.smax<{.rl}> [SrcL], SrcR    |  内存双字比较**有符号最大值**写回  |
|  SD.UMAX  |  sd.umax<{.rl}> [SrcL], SrcR    |  内存双字比较**无符号最大值**写回  |
|  SD.SMIN  |  sd.smin<{.rl}> [SrcL], SrcR    |  内存双字比较**有符号最小值**写回  |
|  SD.UMIN  |  sd.umin<{.rl}> [SrcL], SrcR    |  内存双字比较**无符号最小值**写回  |

STORE.OP类原子指令需要通过"rl"后缀来添加额外的内存访问顺序限制，以保证内存访问的一致性。详细定义请见“内存访问限制参数表”。

![AtomicStore](../../../figs/bitfield/svg/Introduction_32bit/AtomicStore.svg)

## 原子交换指令

原子交换指令从寄存器SrcL指定的内存位置读取`8,16,32或64位`的值，将其写入目的寄存器。然后再将寄存器SrcR中8,16,32或64位的值存入寄存器SrcL指定的内存中，并且**保证这些步骤都是原子的**。

|     微指令    |         汇编格式                          |     描述       |
|--------------|-------------------------------------------|----------------|
|  SWAPB   | swapb<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  内存与寄存器交换**字节**   |
|  SWAPH   | swaph<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  内存与寄存器交换**半字**   |
|  SWAPW   | swapw<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  内存与寄存器交换**字**     |
|  SWAPD   | swapd<{.aq,.rl,.aqrl}> [SrcL], SrcR, ->{t, u, Rd}   |  内存与寄存器交换**双字**   |

原子交换操作指令可以通过”aq”和”rl”两个后缀来添加额外的内存访问顺序限制，以保证内存访问的一致性。具体定义请见”内存访问限制参数表”。

![AtomicSwap](../../../figs/bitfield/svg/Introduction_32bit/AtomicSwap.svg)

## 原子比较交换指令

原子比较交换指令从寄存器SrcL指定的内存位置读取`8,16,32或64位`的值，然后再用这个读出的值和寄存器SrcR比较，如果它们相同的话，就把目的寄存器（RegDst）中的值作为新值写入内存。最后不管前面比较的结果相不相同，都把从内存读取的原始值写入目的寄存器中，并且**保证这些步骤都是原子的**。

**⚠️ 注意：目的寄存器既作为输入（交换值），也作为输出（旧值），输入值会被覆盖。**

|     微指令    |         汇编格式                          |     描述       |
|--------------|-------------------------------------------|----------------|
|  CASB   | casb<{.aq,.rl,.f,.aqrl,.aqf,.rlf,.aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}   |  内存与寄存器比较交换**字节**   |
|  CASH   | cash<{.aq,.rl,.f,.aqrl,.aqf,.rlf,.aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}   |  内存与寄存器比较交换**半字**   |
|  CASW   | casw<{.aq,.rl,.f,.aqrl,.aqf,.rlf,.aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}   |  内存与寄存器比较交换**字**     |
|  CASD   | casd<{.aq,.rl,.f,.aqrl,.aqf,.rlf,.aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}   |  内存与寄存器比较交换**双字**   |

### 操作数说明

- **[SrcL]**：内存地址
- **SrcR**：期望值（expected value），用于与内存中的旧值比较
- **{t, u, Rd}**：目的寄存器，**同时作为输入和输出**
  - **输入**：交换值（new value），当比较成功时写入内存
  - **输出**：内存旧值（old value），无论比较是否成功都返回

### 伪代码

```
old_value = Mem[SrcL]           // 读取内存旧值
expected = SrcR                 // 期望值
new_value = RegDst              // 读取交换值（输入）

if (old_value == expected) {    // 比较
    Mem[SrcL] = new_value       // 比较成功则写入新值
}

RegDst = old_value              // 总是返回旧值（覆盖输入）
```

### 汇编示例

```asm
# 基本用法
casb [x5], x6, x7, ->x7         # x7 既是输入也是输出

# 如需保留交换值
mov x8, x7                      # 先备份交换值
casb [x5], x6, x7, ->x7         # x7 被覆盖为旧值
# 此时: x7=旧值, x8=交换值

# 带内存序标志
casw.aq [x10], x11, x12, ->x12  # acquire 语义
casd.aqrl [x1], x2, x3, ->x3    # 完整内存屏障
casb.f [x20], x21, x22, ->x22   # 远程缓存访问
```

### 与 48-bit HL.CAS 的区别

LinxISA 提供两种 CAS 指令：

| 特性 | 32-bit CAS | 48-bit HL.CAS |
|------|-----------|---------------|
| 指令长度 | 32 bits | 48 bits |
| 寄存器 | 3个（RegDst 复用） | 4个（完全独立） |
| 交换值 | 被覆盖 | 保留 |
| 代码密度 | 高 | 低 |
| 使用场景 | 高频原子操作 | 寄存器压力大的场景 |

**选择建议**：
- 代码密度优先 → 使用 32-bit CAS
- 需保留交换值 → 使用 48-bit HL.CAS
- 高频调用 → 使用 32-bit CAS（更短）

![AtomicCompareandSwap](../../../figs/bitfield/svg/Introduction_32bit/AtomicCompareandSwap.svg)

原子比较交换指令可以通过”aq”、”rl”和”f”后缀来添加额外的内存访问顺序限制，以保证内存访问的一致性。具体定义请见”内存访问限制参数表”。

## 内存访问限制参数表

|   aq  |  rl    |  含义                             |
|-------|--------|-------------------------------------|
|  0  |  0  | 没有顺序限制                        |
|  0  |  1  | 表示该指令的前序所有访问内存的指令的结果必须在该指令执行之前被观察到  |
|  1  |  0  | 表示该指令的后序所有访问内存的指令必须等该指令执行完成后才开始执行    |
|  1  |  1  | 表示该指令的前序所有访问内存的指令的结果必须在该指令执行之前被观察到，该指令的后序所有访问内存的指令必须等该指令执行完成后才开始执行    |
