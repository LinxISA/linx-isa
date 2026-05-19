# TRAPNO

异常原因寄存器（Trap Number Register）是 **可读写的(RW)** 系统寄存器，由服务请求**SERVICE_REQUEST**过程更新，用于存储发起服务的源ACR的发起原因。

![TRAPNO](../../../figs/bitfield/svg/Sysregs/TRAPNO.svg)

- **TRAPNUM**：表示陷入代号，该字段被服务请求**SERVICE_REQUEST**程序设置。
- **CAUSE**：此字段定义了服务请求的详细原因，请参阅Exception Cause部分关于 `Trap Number`和 `TrapCause Number`的所有组合。
- **E**: 当发生同步异常时，E置为1，当发生异步中断时，E置为0。

## 异常原因

<table border="2">
<caption>异常原因表</caption>
  <tr>
    <th >陷入代号</th>
    <th >含义</th>
    <th colspan="2">原因代号</th>
    <th colspan="2">含义</th>
  </tr>
  <tr>
    <td rowspan="8">E_INST(0)</td>
    <td rowspan="8">指令相关异常</td>
    <td colspan="2">EC_ACCESS_FAULT(0)</td>
    <td colspan="2">指令访问异常</td>
  </tr>
  <tr>
    <td colspan="2">EC_TRANS_FAULT(1)</td>
    <td colspan="2">指令翻译异常</td>
  </tr>
  <tr>
    <td colspan="2">EC_MISALIGNED(2)</td>
    <td colspan="2">指令不对齐</td>
  </tr>
  <tr>
    <td colspan="2">EC_ILLEGAL(3)</td>
    <td colspan="2">非法指令</td>
  </tr>
  <tr>
    <td colspan="2">EC_PERM(4)</td>
    <td colspan="2">指令权限异常</td>
  </tr>
  <tr>
    <td colspan="2">EC_PF(5)</td>
    <td colspan="2">指令页非法</td>
  </tr>
  <tr>
    <td colspan="2">EC_BUS(6)</td>
    <td colspan="2">总线异常</td>
  </tr>
  <tr>
    <td colspan="2">EC_PARAM(7)</td>
    <td colspan="2">非法参数</td>
  </tr>
  <tr>
    <td rowspan="8">E_DATA(1)</td>
    <td rowspan="8">数据访问相关异常</td>
    <td colspan="2">EC_LOAD(0)</td>
    <td colspan="2">内存读取异常</td>
  </tr>
  <tr>
    <td colspan="2">EC_MISALIGNED(1)</td>
    <td colspan="2">内存读取不对齐</td>
  </tr>
  <tr>
    <td colspan="2">EC_LOAD_PAGE(2)</td>
    <td colspan="2">读操作页非法</td>
  </tr>
  <tr>
    <td colspan="2">EC_STORE_A_ACCESS(3)</td>
    <td colspan="2">内存写访问异常</td>
  </tr>
  <tr>
    <td colspan="2">EC_STORE_A_MISALIGNED(4)</td>
    <td colspan="2">内存写地址不齐</td>
  </tr>
  <tr>
    <td colspan="2">EC_STORE_A_PF(5)</td>
    <td colspan="2">写操作页非法</td>
  </tr>
  <tr>
    <td colspan="2">EC_RANGE(6)</td>
    <td colspan="2">访问范围非法</td>
  </tr>
  <tr>
    <td colspan="2">EC_BUS(7)</td>
    <td colspan="2">总线异常</td>
  </tr>
  <tr>
    <td rowspan="5">E_BLOCK(4)</td>
    <td rowspan="5">块格式异常</td>
    <td colspan="2">EC_INVAL_SET(0)</td>
    <td colspan="2">输出未指定的输出寄存器</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_GET(1)</td>
    <td colspan="2">读取未指定的输入寄存器</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_PARM(2)</td>
    <td colspan="2">非法参数</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_DOUBLESET(3)</td>
    <td colspan="2">块内重复设置寄存器</td>
  </tr>
  <tr>
    <td colspan="2">EC_INVAL_FIXUP(4)</td>
    <td colspan="2">不正确的子修复块参数</td>
  </tr>
  <tr>
    <td rowspan="5">E_FLOAT(5)</td>
    <td rowspan="5">浮点例外</td>
    <td colspan="2">EC_INVAL_OPERATION(0)</td>
    <td colspan="2">非法操作例外</td>
  </tr>
  <tr>
    <td colspan="2">EC_DIVISION_BY_ZERO(1)</td>
    <td colspan="2">被0除例外</td>
  </tr>
  <tr>
    <td colspan="2">EC_OVERFLOW(2)</td>
    <td colspan="2">上溢例外</td>
  </tr>
  <tr>
    <td colspan="2">EC_UNDERFLOW(3)</td>
    <td colspan="2">下溢例外</td>
  </tr>
  <tr>
    <td colspan="2">EC_INEXACT(4)</td>
    <td colspan="2">不精确例外</td>
  </tr>
  <tr>
    <td rowspan="1">E_ASSERT (15)</td>
    <td colspan="6">断言异常 (产生原理请参考assert指令的定义)</td>
  </tr>
  <tr>
    <td rowspan="1">E_SCALL(16)</td>
    <td colspan="6">软件主动异常（系统调用）</td>
  </tr>
  <tr>
    <td rowspan="1">E_BREAKPOINT(17)</td>
    <td colspan="6">软件断点</td>
  </tr>
  <tr>
    <td rowspan="1">18-61</td>
    <td colspan="6">保留</td>
  </tr>
  <tr>
    <td rowspan="1">E_ISSR(62)</td>
    <td colspan="6">非法SSR异常</td>
  </tr>
  <tr>
    <td rowspan="1">E_NIL(63)</td>
    <td colspan="6">本值用于表示异常分类无效</td>
  </tr>
</table>

!!! note "注意"

    EC_前缀名称是异常原因名称，仅在特定`Trap Number`中有效。

## 地址空间

该寄存器在每个ACR中的命名和寻址空间有所差别，具体如下：

| ACR层级 | 寄存器名 | 地址空间 |
|---------|---------|---------|
| ACR0   | TRAPNO_ACR0  | 0x0f02 |
| ACR1   | TRAPNO_ACR1  | 0x1f02 |
| ACR2   | TRAPNO_ACR2  | 0x2f02 |
| ...   | ...  | ... |
| ACRn   | TRAPNO_ACRn  | 0xnf02 |

其中，“_ACR{m}”后缀表示该寄存器从ACR{m}访问。
