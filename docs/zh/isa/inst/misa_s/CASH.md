# CASH - 原子比较交换半字

## 指令格式

```
cash<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {t, u, Rd}, ->{t, u, Rd}
```

## 指令说明

CASH（Compare-And-Swap Halfword）指令原子地比较内存中的半字（16-bit）值与期望值，如果相等则用新值替换。无论比较是否成功，都返回内存中的旧值。

**⚠️ 重要**：目的寄存器既作为输入（新值），也作为输出（旧值），输入值会被覆盖。

## 编码格式

```
位段: 31..28 | 27 | 26 | 25 | 24..20 | 19..15 | 14..12 | 11..7  | 6..4 | 3..1 | 0
     ────────────────────────────────────────────────────────────────────────────
     0001   | f  | a  | r  | SrcR   | SrcL   | 111    | RegDst | 000  | 101  | 1
     CASH   |far | aq | rl | 比较值 | 地址   | CAS    | 复用   |原子组|      |
```

**与 CASB 的区别**：
- 31..28 = 4'b0001（半字宽度，CASB 为 0000）
- 操作 16-bit 数据（CASB 操作 8-bit）

## 汇编示例

```asm
# 基本用法
cash [x5], x6, x7, ->x7

# 带内存序
cash.aq [x10], x11, x12, ->x12
cash.aqrl [x1], x2, x3, ->x3
```

## 伪代码

```c
Atomic {
    bits(16) old_value = Mem[SrcL, 16];
    if (old_value == SrcR[15:0]) {
        Mem[SrcL, 16] = RegDst[15:0];
    }
    RegDst = ZeroExtend(old_value, 64);
}
```

## 注意事项

1. **对齐要求**：地址应 2-byte 对齐（性能最佳）
2. 其他特性与 CASB 相同，详见 [CASB 文档](CASB.md)

## 相关指令

- [CASB](CASB.md) - 原子比较交换字节（8-bit）
- [CASW](CASW.md) - 原子比较交换字（32-bit）
- [CASD](CASD.md) - 原子比较交换双字（64-bit）
