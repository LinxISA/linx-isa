## 通用系统寄存器

通用系统寄存器可被所有ACR访问。这些SSR分成4个类别：

- 运行寄存器：这些寄存器可以认为是使用不频繁的GPR，使用0x0000-0x000f范围的空间。
- 时钟寄存器：这些寄存器用于记录处理器的全局时间戳，使用0x0010-0x001f范围的空间。
- 静态配置寄存器：这些寄存器主要用于读取全局信息。使用0x0020-0x002f范围的空间。
- 循环控制寄存器，这些寄存器用于并行块或LOOP块指令的执行控制，使用0x0050-0x005f范围的空间。

## 运行寄存器

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0x0000  |  [TP](./TP.md)  |  Thread Pointer Register  |  线程基址寄存器  |
|  0x0001  |  [GP](./GP.md)  |  Global Pointer Register  |  全局基址寄存器  |

## 时钟寄存器

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0x0010  |  [TIME](./TIME.md)    |  Timer Counter Register  |  定时器计数寄存器  |
|  0x0011  |  [CYCLE](./CYCLE.md)  |  Cycle Counter Register  |  核级时间戳  |

## 静态配置寄存器

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0x0020  |  [CSTATE](./CSTATE.md)  |  Common State Register  |  公共状态寄存器  |
|  0x0021  |  [LXLCID](./LXLCID.md)  |  Linx Logical Core ID Register  |  灵犀逻辑核ID寄存器  |
|  0x0022  |  [VENDOR](./VENDOR.md)  |  Vendor ID Register  |  供应商ID寄存器  |
|  0x0023  |  [VERSION](./VERSION.md)  |  Linx Core Version Register  |  灵犀逻辑核版本寄存器  |
|  0x0024  |  [LCFR](./LCFR.md)      |  Linx Core Features Register  |  灵犀核特征寄存器  |
|  0x0025  |  [LCFR_EN](./LCFR_EN.md)  | Linx Core Feature Enable Register  |  灵犀核特征使能寄存器  |

## 动态配置寄存器

|  SSR ID  |   简称   |    Name        |    名称         |
|----------|----------|---------------|------------------|
|  0x0050  |  [BLOCKNUM](./BLOCKNUM.md)  |  Block Number Register  |  逻辑核总数寄存器  |
|  0x0051  |  [BLOCKID](./BLOCKID.md)  |  Block ID Register  |  逻辑核ID寄存器  |
