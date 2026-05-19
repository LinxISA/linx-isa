# 管理者ACR专用系统寄存器

管理者ACR专用的SSR的编址空间对所有ACR可见，但仅被部分具有管理功能的ACR所支持。

这些SSR遵循如下规则：

- 这些寄存器**仅在ACR0和ACR1中可访问**，其他ACR访问该范围可能无效果，也可能触发非法SSR异常。
- 这些寄存器针对不同的ACR有不同的编址。
- "_ACRn" 后缀表示这个功能必须从ACRn访问，从不同ACR访问可以表现不同的行为。

## 中断异常管理寄存器

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0xnf00  | [ECSTATE_ACRn](./ECSTATE.md)   |  Exception State Register |  异常状态寄存器  |
|  0xnf01  | [EVBASE_ACRn](./EVBASE.md)     |  Exception Vector Base Register |  异常向量基址寄存器  |
|  0xnf02  | [TRAPNO_ACRn](./TRAPNO.md)     |  Trap Number Register |  异常原因寄存器  |
|  0xnf03  | [TRAPARG0_ACRn](./TRAPARG0.md) |  Trap Argument 0 Register |  异常参数0寄存器  |
|  0Xnf04  | 保留  | - | - |
|  0xnf05  | [ETEMP_ACRn](./ETEMP.md)       |  Exception Temporary Register  |  异常上下文保存临时寄存器  |
|  0xnf06  | [FUTO_ACRn](./FUTO.md)         |  Fixup Takeover Register  |  异常修复接管寄存器  |
|  0xnf07  | [ECONFIG_ACRn](./ECONFIG.md)   |  Exception Configuration Register  |  异常配置寄存器  |
|  0xnf08  | [IPENDING_ACRn](./IPENDING.md) |  Interrupt Pending Register  |  中断挂起寄存器  |
|  0xnf09  | [TOPEI_ACRn](./TOPEI.md)       |  Top Interrupt ID Register  |  TOP中断ID寄存器  |
|  0xnf0a  | [EOIEI_ACRn](./EOIEI.md)       |  End of Interrupt Register  |  中断结束寄存器  |
|  0xnf0b  | [EBPC_ACRn](./EBPC.md)         | BPC of Exception Block | 异常块指令的BPC |
|  0xnf0c  | [EBARG_ACRn](./EBARG.md)       | Arguments of Exception Block | 异常块指令的参数 |
|  0xnf0d  | [ETPC_ACRn](./ETPC.md)         | TPC of Exception Instruction | 异常微指令的TPC  |
|  0xnf0e  | [EBPCN_ACRn](./EBPCN.md)       | Next BPC of Exception Block  | 异常块指令下个块的BPC |

## 内存管理寄存器

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0x1f10  |  [MMTBASE_ACR1](./MMTBASE.md)  |  Memory Management Translation Base Register for ACR1 |  内存管理翻译库寄存器  |
|  0x1f11  |  [MMCONFIG_ACR1](./MMCONFIG.md)  |  Memory Management Configuration Register for ACR1 |  内存管理配置寄存器  |

## 时钟管理寄存器

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0xnf20  |  [TIMER_TIME_ACRn](./TIMER_TIME.md)  |  Timer Register  |  定时器寄存器  |
|  0xnf21  |  [TIMER_TIMECMP_ACRn](./TIMER_TIMECMP.md)  |  Timer Compare Register  |  定时器比较器寄存器  |

## 其他

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0xnf30  |  [XBINFO_ACRn](./XBINFO.md)  |  Cross Block Info Register  |  XB块初始化寄存器  |
|  0xnf31  |  [ACR_PARAM_ACRn](./ACR_PARAM.md)  |  ACR Parameter Register  |  ACRn LxLC参数寄存器  |

* n是所述管理者ACR的ACR ID。
