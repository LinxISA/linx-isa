# TRAPNO

陷入编号寄存器是服务请求进入时写入的管理 ACR 可读写寄存器。

## 线级布局

| 字段 | 位 | 含义 |
| --- | --- | --- |
| `E` | `[63]` | `1`：同步异常；`0`：异步中断 |
| `ARGV` | `[62]` | `1`：`TRAPARG0` 有效 |
| `CAUSE` | `[47:24]` | 由所选异常大类解释的原因编码 |
| `TRAPNUM` | `[5:0]` | 陷入大类数值 |

未列出的位在当前 profile 中保留。

VECTOR/CUBE 首次使用扩展不修改既有 bring-up 陷入编号表。PTO 定义的 `EBREAK` 行为以及现有 ASSERT、E_DATA、E_BLOCK、系统调用和调试异常编号均不属于本次重编号范围。

## VECTOR/CUBE 首次使用

| 字段 | 数值 |
| --- | --- |
| `E` | `1` |
| `ARGV` | `1` |
| `TRAPNUM` | `E_INST (0)` |
| `CAUSE` | `EC_PERM (4)` |
| `TRAPARG0` | VECTOR 为 `0`；CUBE 为 `1` |
| `ECSTATE.BI` | `0` |

该完整组合唯一标识首次使用异常。归档中的 `EC_PERM` 旧拼写不是活动别名。
