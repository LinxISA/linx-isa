# BCC(Block Control Core)

本章节目的是为了帮助快速了解LinxISA微架构的实现。

## 主要内容

1. 块指令级别的流水线
2. 简要说明BCC主要模块的功能或目的[【详见：块控制核BCC介绍】](../../bcc/overview.md)以及实现其功能的代码说明。

## 说明

数据流向下一流水级的方式：  
（1）写入下一流水级的next状态；  
（2）写入一个队列（此队列输入的数据下一周期才可见）；  
（3）为每一流水级设有一个状态，工作完成后赋给下一流水级。

## BCC整体流水线

- **BCC流水线**

![BCC流水线](../../figs/model/model_detail/BCC.svg)

## BPC复位——执行第一个块

*sim->core->setBPC(start_addr);*  
\=> *bctrl->interrupt(req);*  
\===> *blockFetchUnit.jumpTo(req.initPC);*  
\=====> *bfu->createNewF0(bpc, 0, true); // 依据BPC设置第一级流水*

## 各阶段执行

- [查看BIFU](./BIFU.md)
- [查看Decode](./BCTRL.md)
- [查看BRename](./BRename.md)
- [查看BIssue](./BIssue.md)
- [查看BROB](./BROB.md)

