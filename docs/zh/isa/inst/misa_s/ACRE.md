# ACRE

## 说明

ACR切换(*ACR Enter*)  
ACRE指令设置当前块的ACR切换要求。用于立即提交当前块并执行ACR_ENTER流程，把当前ARC切换为目标ACR。

目标ACR由执行acre指令所在特权级的[ECSTATE](../../register/ssr/ECSTATE.md)寄存器指定。

需要特殊注意的是：本指令提交后，当前块指令将立即提交。因此本指令必须作为所在块指令的最后一条指令。

## 汇编语法

```asm
    acre RRA_Type
```

## 汇编符号

**RRA_Type** 是用于指定方法参数（Return Request Argument，简称RRA）的立即数。有效取值范围包括：

| RRA_Type类型 | 说明 |
|-------------|----------| 
| **RRAT_DEFAULT(0)** | BSTATE在提交的时候复位为默认状态。 |
| **RRAT_RESTORE(1)** | 用EBSTATE初始化BSTATE。  |
| 其他值保留 | 如果执行时遇到其他值，提交时触发**非法指令异常**。 |

## 指令编码

![ACRE](../../../figs/bitfield/svg/Instruction_32bit/ACRE.svg)

## ACR_ENTER的流程

ACR_ENTER通过acre指令请求，并在块提交的时候触发。

对于一次从`ACRn`到`ACRm`的ACR_ENTER，其具体过程为：

- 将灵犀核的ACR状态切换到当前特权级中ECSTATE指示的目标ACR。目标ACR必须和当前ACRn可比，并且当前所在的ACR等级必须大于等于目标ACR。否则触发**指令权限异常**异常。
- 用[ECSTATE_ACRn](../../register/ssr/ECSTATE.md) **恢复当前CSTATE的状态**；
- 用[EBPC_ACRn](../../register/ssr/EBPC.md) **恢复BPC的内容**，并调度该块执行。
- 根据acre的RRA参数，用EBSTATE的内容 **恢复BSTATE**。

## 汇编示例

```asm
# 异常恢复块
ERCOV                 <- 恢复异常块的块内状态
# 调用ACRE的块
BSTART.SYS
B.CATR TRAP
acre                  <- 返回异常块的BPC和异常指令的TPC
# 返回EBPC指示的块
BSTART.xx
inst                  <- 从ETPC恢复的TPC指示的指令
```

## 备注

本指令属于系统块内微指令，仅在系统块内支持使用。
