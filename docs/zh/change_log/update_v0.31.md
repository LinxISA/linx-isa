# 0.31版本更新

日期：2023年9月18日

指令编码设计文档网页版路径请见[LinxISA Encoding-v0.31](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255902243)

v0.31版本主要是对块头编码的更新。

## 块头变化

v0.31定义了**标准块**，**标准超级块**，**标准压缩快**，**标准超级压缩块**，**标准浮点块**，**标准浮点超级块**，**内联块**，**控制块**，**模板块**以及**系统块**等10种块指令块头指令。

- 将16bit编码空间的指令放在标准压缩块和标准超级压缩块执行。
- 增加内联块，实现将指令内嵌于块头。
- 去掉了concat块，增加LBREF块，实现长跳转，长索引和循环控制。
- 删除辅助块，原辅助块内微指令移至标准块内执行。

v0.31定义的块类型如下：

|    块类型                |   解释      |  汇编标识  |
|-------------------------|------------|-------------|
| Standard Block  |  标准块  |  b.std  |
| Standard Hyper Block  |  标准超级块  |  b.stdh   |
| Standard Compressd Block  |  标准压缩块  |  b.stdc  |
| Standard Compressd Hyper Block  |  标准压缩超级块  |  b.stdhc   |
| Floating-point Block  |  标准浮点块  |  b.fp  |
| FP Hyper Block  |  标准浮点超级块  |  b.fph  |
| Inline Block  |  内联块  |  b.inl  |
| Control Block |  控制块  |  见具体块指令  |
| Template Block  |  模板块  |  见具体块指令    |
| System Block  |  系统块  |  b.sys  |
| System Hyper Block  |  系统超级块  |  b.sysh  |
