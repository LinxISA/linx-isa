# 地址计算类

地址计算类指令用于计算指定位置的地址以及PC-relative相对寻址。

| 微指令 | 汇编格式                | 描述                                              |
| ------ | ----------------------- | ------------------------------------------------- |
| ADDTPC | addtpc simm, ->{t,u,Rd} | 本指令TPC与左移12位的有符号立即数相加，结果写入目的寄存器中  |
| SETRET | setret uimm, ->ra       | 本指令TPC与左移1位的无符号立即数相加，结果写入全局ra寄存器中 |

编码格式如下：

![PC-Arithmetic](../../../figs/bitfield/svg/Introduction_32bit/PC-Arithmetic.svg)
