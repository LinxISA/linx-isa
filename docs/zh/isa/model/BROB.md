# BROB

## 功能
维护块指令顺序，实现精确异常。

## 实现

![BROB](../../figs/model/model_detail/BROB.svg)

### 块提交流水线——【commitBlock()】

    检查块的状态，根据块的状态进行不同操作。

    当块正常完成时（COMPLETE状态），增长ROB提交指针【*incROBID(next.commitPtr, next.entry.size());*】，  
    向其他模块发出块退休信号，释放块指令占用的空间以及更新分支预测信息。  
    【*top->blockRenameUnit.retireBlock(current.commitPtr);  
    【top->blockIssueQ.releaseEntry(current.commitPtr);  
    【top->blockFetchUnit.retireBlock(bentry.header);  
    【top->core->sRenameUnit->setBlockRetire(current.commitPtr);*】。

## 备注

处理器异常还未实现。
