# Decode & Dispatch【*BCtrlUnit::decodeBlockHeader()*】

## Function

Further decode and distribute header to BROB and BIQ bound to PE.

## Implementation

![Decode](../../figs/model/model_detail/Decode.svg)

### 1) Get header【*FullBlockHeader header = blockFetchUnit.getBlockHeader(pos);*】
    Get the pre-decoded headerMachineHeader [*NS_CORE::PtrMHdr h = bfu_be_q.read();*] and convert it to FullBlockHeader [*convertHeader(fbh, h);*].

### 2) Allocate BROB table entries [*ROBID bSeq = blockROB.allocBlock(header, pos);*]

### 3) Send a rename request to the block rename module [*blockRenameUnit.renameBlock(header);*]

### 4) Make a decision to which PE to distribute to [*DispatchDecision decision = header.hyper ? blockDispatchUnit.getDispatch(header, hyper_cnt++) : blockDispatchUnit.getDispatch(header, pos);*]
    Distribution strategy: 1. Circular distribution 2. Load balancing

### 5) Send an intra-block microinstruction prefetch request to the PE IFU [*core->ifuArray[decision.peID]->setPrefetchQ(header.payloadPC, header.size);*]

### 6) Allocate BIQ table entries [*blockIssueQ.allocateBlock(header.bSeq, decision.peID, header.size);*]