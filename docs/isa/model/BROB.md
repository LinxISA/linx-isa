# BROB

## Function
Maintain block instruction sequence to achieve accurate exception.

## Implementation

![BROB](../../figs/model/model_detail/BROB.svg)

### Block submission pipeline——[commitBlock()]

    Check the status of the block and perform different operations based on the status of the block.

    When the block is completed normally (COMPLETE state), increase the ROB submission pointer [*incROBID(next.commitPtr, next.entry.size());*],
    Send block retirement signals to other modules, release the space occupied by block instruction and update branch prediction information.  
    【*top->blockRenameUnit.retireBlock(current.commitPtr);
    【top->blockIssueQ.releaseEntry(current.commitPtr);
    【top->blockFetchUnit.retireBlock(bentry.header);
    [top->core->sRenameUnit->setBlockRetire(current.commitPtr);*].

## Remarks

Processor exception has not yet been implemented.