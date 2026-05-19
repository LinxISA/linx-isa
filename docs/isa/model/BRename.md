# BlockRename

## Function

Rename header

## Implementation

![BREN](../../figs/model/model_detail/BREN.svg)

### Rename pipeline [1] - separate the GetMask and SetMask of header into multiple GET and SET rename requests [*convertBitMask()*]

### Rename pipeline [2]——Rename

- GET rename [*getReq = renameGet(renameGetNum);*] (read the physical register number PTAG from the speculative mapping table SMAP [*uint32_t ptag = next.smap[req.atag];*], write to the register mapping table [*insertGETPRFTable(req, ptag);*]);

- SET rename [*setReq = renameSet(renameSetNum);*] (obtain an item from the free physical register list [*uint32_t ptag = getFreeList(index);*] and write it to the register map table [*insertSETPRFTable(req, ptag);*]).

- Mark block renaming completed [*getOutputQ.write(req.bid); setOutputQ.write(req.bid);*]

## Remarks

The number of rename requests processed per cycle in the rename pipeline [2] is limited to brnu_rename_width.