# Block Issue Queue

## Function

Select header and launch it to the corresponding PE

## Implementation

![BIQ](../../figs/model/model_detail/BIQ.svg)

### Launch pipeline【1】

Check the result of block renaming and set the status of the corresponding entry to "Renamed" [*checkRename();*]

### Launch pipeline【2】

Emit the block [*issueBlock();*]

1. Select an available PE.
2. Select an emissible block. In BROB, the status of each block is queried sequentially starting from the oldest block. When encountering a block that needs to be flushed, the query stops, and subsequent blocks will be flushed; the emitted blocks are ignored.
3. Launch. Search the block in the BIQ bound to the current PE. If it exists, PEControlBus is generated and sent to the bound PE [*bcc_pe_req_array[pe]->write(peReq);*]; if it does not exist, continue to step 1.