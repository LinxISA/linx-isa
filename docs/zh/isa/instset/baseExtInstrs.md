# 基础扩展指令集

基础扩展指令集作为[基础指令集](./baseInstrs.md)的补充，用于提供通用运算之外的扩展功能，如除法求余操作等。

基础扩展指令集的指令长度统一为32位，并且可用于不同类型的块指令块体中。

指令列表如下：

| 分类 | 指令 |
|-----|------|
| **除法操作** | [DIV](../inst/misa_g/DIV.md), [DIVU](../inst/misa_g/DIVU.md), [DIVW](../inst/misa_g/DIVW.md), [DIVUW](../inst/misa_g/DIVUW.md) |
| **求余操作** | [REM](../inst/misa_g/REM.md), [REMU](../inst/misa_g/REMU.md), [REMW](../inst/misa_g/REMW.md), [REMUW](../inst/misa_g/REMUW.md) |
| **条件选择** | [CSEL](../inst/misa_g/CSEL.md) |
