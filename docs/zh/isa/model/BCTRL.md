# Decode & Dispatch【*BCtrlUnit::decodeBlockHeader()*】

## 功能

进一步解码，将块头分发至BROB、与PE绑定的BIQ。

## 实现

![Decode](../../figs/model/model_detail/Decode.svg)

### 1）获取块头【*FullBlockHeader header = blockFetchUnit.getBlockHeader(pos);*】
    获取预解码过的块头MachineHeader【*NS_CORE::PtrMHdr h = bfu_be_q.read();*】，转换为FullBlockHeader【*convertHeader(fbh, h);*】。

### 2）分配BROB表项【*ROBID bSeq = blockROB.allocBlock(header, pos);*】

### 3）向块重命名模块发出重命名请求【*blockRenameUnit.renameBlock(header);*】

### 4）作出分发至哪个PE的决定【*DispatchDecision decision = header.hyper ? blockDispatchUnit.getDispatch(header, hyper_cnt++) : blockDispatchUnit.getDispatch(header, pos);*】
    分配策略：1. 循环分配 2. 负载均衡

### 5）向PE IFU发出块内微指令预取请求【*core->ifuArray[decision.peID]->setPrefetchQ(header.payloadPC, header.size);*】

### 6）分配BIQ表项【*blockIssueQ.allocateBlock(header.bSeq, decision.peID,header.size);*】
