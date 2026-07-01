# CASW - 原子比较交换字

## 指令格式

```
casw<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}
```

## 指令说明

CASW（Compare-And-Swap Word）指令原子地比较内存中的字（32-bit）值与期望值，如果相等则用新值替换。无论比较是否成功，都返回内存中的旧值。

**⚠️ 重要**：目的寄存器既作为输入（新值），也作为输出（旧值），输入值会被覆盖。

## 编码格式

```
位段: 31..28 | 27 | 26 | 25 | 24..20 | 19..15 | 14..12 | 11..7  | 6..4 | 3..1 | 0
     ────────────────────────────────────────────────────────────────────────────
     0010   | f  | a  | r  | SrcR   | SrcL   | 111    | RegDst | 000  | 101  | 1
     CASW   |far | aq | rl | 比较值 | 地址   | CAS    | 复用   |原子组|      |
```

**与 CASB 的区别**：
- 31..28 = 4'b0010（字宽度，CASB 为 0000）
- 操作 32-bit 数据（CASB 操作 8-bit）

## 汇编示例

```asm
# 基本用法
casw [x5], x6, x7, ->x7

# 带内存序
casw.aq [x10], x11, x12, ->x12
casw.aqrl [x1], x2, x3, ->x3
```

## 伪代码

```c
Atomic {
    bits(32) old_value = Mem[SrcL, 32];
    if (old_value == SrcR[31:0]) {
        Mem[SrcL, 32] = RegDst[31:0];
    }
    RegDst = ZeroExtend(old_value, 64);
}
```

## 使用场景

CASW 是最常用的 CAS 指令，适用于：
- 32-bit 指针的原子更新（32-bit 地址空间）
- 整数计数器
- 状态机变量

## 注意事项

1. **对齐要求**：地址应 4-byte 对齐（性能最佳）
2. 其他特性与 CASB 相同，详见 [CASB 文档](CASB.md)

## 相关指令

- [CASB](CASB.md) - 原子比较交换字节（8-bit）
- [CASH](CASH.md) - 原子比较交换半字（16-bit）
- [CASD](CASD.md) - 原子比较交换双字（64-bit）
