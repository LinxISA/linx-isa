# Block Rename

## 功能

对块头进行重命名  

## 实现

![BREN](../../figs/model/model_detail/BREN.svg)

### 重命名流水线【1】——将块头的GetMask和SetMask分离成多个GET和SET重命名请求【*convertBitMask()*】

### 重命名流水线【2】——重命名

- GET重命名【*getReq = renameGet(renameGetNum);*】（从投机映射表SMAP读取物理寄存器编号PTAG【*uint32_t ptag = next.smap[req.atag];*】，写入寄存器映射表【*insertGETPRFTable(req, ptag);*】）；

- SET重命名【*setReq = renameSet(renameSetNum);*】  （从空闲物理寄存器列表获得一项【*uint32_t ptag = getFreeList(index);*】，写入寄存器映射表【*insertSETPRFTable(req, ptag);*】）。

- 标记块重命名完成【*getOutputQ.write(req.bid); setOutputQ.write(req.bid);*】

## 备注

重命名流水线【2】中每周期处理重命名请求的个数限制为brnu_rename_width。
