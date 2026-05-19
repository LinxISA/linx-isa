# 0.51版本更新

更新日期：2025年6月11日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.51](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100980339929)

灵犀指令集0.51版本最主要的变动是**引入并行块设计**，并围绕并行块的内容补充架构状态的定义。

并行块指令由0.4版本的SIMT块指令演化而来，为了避免专利与知识产权问题，0.51版本中SIMT块命名改为**并行块**。在此基础上，架构状态中增加Tile Register的设计以及刷新向量指令的定义，从而使得并行块可以更高效的承载人工智能、图形渲染及高性能计算领域等包含大规模计算的任务。

![ParallelBlock](../figs/isa/version/parblock.png)

## 更新概要

| 分类 | 说明 |
|-------|-------|
| 第一层架构状态 | 增加32个Tile Register: <br>1.T#1-T#8<br>U#1-U#8<br>M#1-M#8<br>N#1-N#8 |
| 并行块内状态   | 增加8个标量寄存器：T#1-T#4, U#1-U#4 |
| 并行块内状态   | 向量寄存器从32个减少至16个：VT#1-VT#4, VU#1-VU#4, VM#1-VM#4, VN#1-VN#4 |
| 并行块内状态   | 循环控制寄存器改为块内状态：LB0-LB2, LC0-LC2 |
| 并行块内状态   | 增加掩码寄存器：P寄存器 |
| 增加块头指令   | B.DIM, C.B.DIM, C.B.DIMI, B.IOT |
| 恢复块内跳转指令编码 | b.eq, b.ne, b.lt, bge, b.ltu, b.geu, jr, j |
| 增加两条跳转指令 | b.z, b.nz |
| 标量寄存器修改 | T和U寄存器修改为不固定位宽 |
| 增加8条shuffle指令 | shfl.up, shfl.down, shfl.bfly, shfl.idx, shfli.up, shfli.down, shfli.bfly, shfli.idx |
| ALU类指令修改 | 对输入恢复可选参数（.neg和.not） |
| 指令输入输出 | 部分指令增加P寄存器输入输出 |
| 指令行为定义 | reduce指令输出行为重定义 |
| 删除指令 | loop.get, loop.set |
| 删除系统寄存器 | LPCB0, LPCE0, LPCB1, LPCE1, LPCB2, LPCE2 |
