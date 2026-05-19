# Block Issue Queue

## 功能

挑选块头发射到对应的PE

## 实现

![BIQ](../../figs/model/model_detail/BIQ.svg)

### 发射流水线【1】

检查块重命名的结果，将对应表项状态置为“已重命名”【*checkRename();*】

### 发射流水线【2】

将块发射【*issueBlock();*】

1. 选择一个可用的PE。
2. 选择一个可发射的块。在BROB中，从最老块开始顺序查询每个块的状态，遇到需要刷掉的块就停止查询，之后的块都会被刷掉；略过已发射的块。
3. 发射。在与当前PE绑定的BIQ中查找该块，如果存在，则产生PEControlBus并发送至绑定的PE【*bcc_pe_req_array[pe]->write(peReq);*】；若不存在继续步骤 1。
