# ACRC

## 说明

系统调用(*ACR Call*)<br>
ACRC指令设置当前块的系统调用状态，立即提交当前块并发起一次 **系统请求**。

需要特殊注意的是：ACRC指令是一条带有BSTOP语义的指令，因此必须作为所在块指令的最后一条指令。

## 汇编语法

```asm
    acrc request_type
```

## 汇编符号

**request_type** 表示系统请求类型，针对不同的当前ACR有不同的含义。

- 对于**ACR1**支持如下分类：
    - **SCT_MAC (0)**: 整机（Machine）请求。通常用于对BIOS发起请求。
    - **SCT_SEC (2)**: 安全调用。通常用于对安全软件发起请求。
- 对于**ACR2**，有效取值为：
    - **SCT_MAC (0)**: 同ACR1的对应定义。
    - **SCT_SYS (1)**: 系统调用。通常用于用户程序对操作系统发请求。
    - **SCT_SEC (2)**: 同ACR1的对应定义。

其他ACR的请求在当前版本被认为无效。

不同的取值可能会被路由到不同的目标ACR执行或处理：

- ACR2的**SCT_SYS路由到ACR1**。
- **其他的所有有效类型都路由到ACR0**。

如果取值不在这个范围内。本指令本身触发**非法指令异常**。

## 指令编码

![ACRC](../../../figs/bitfield/svg/Instruction_32bit/ACRC.svg)

RqtType字段用于编码参数request_type。

## 应用示例

本指令触发系统请求后，硬件将保存 `acrc所在块的BPC至EBPC` 以及 `acrc的TPC至ETPC`。那么在返回到用户态前：

- 软件如果不做修改，将返回到acrc的原地址处，重新发起一次系统请求（redo syscall）。
- 如果期望返回到acrc下一条指令继续执行，那么软件需要将EBPC和ETPC内的地址改为ETPC原值加4（即acrc的指令长度）。

示例：
```asm
    BSTART.SYS        <--- BPC
    B.CATR TRAP
    ldi [a0, 8],  ->t
    ldi [a0, 16], ->t
    mul t#1, t#2, ->t
    acrc SCT_SYS      <--- TPC
    BSTART.STD        <--- NextBPC       
    ...
```

ACRC触发系统调用后如何继续执行的方式说明如下：

| 异常保存寄存器 | 硬件保存 | 软件不修改，重新发起请求 | 软件修改，返回执行下一条指令 |
|---------------------|----------|-----------------------|----------------------------|
| [EBPC](../../register/ssr/EBPC.md) | BPC | BPC | TPC+4 |
| [ETPC](../../register/ssr/ETPC.md) | TPC | TPC | TPC+4 |

## 备注

本指令属于系统块内微指令，仅在系统块内支持使用。
