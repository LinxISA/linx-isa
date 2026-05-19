## BSIDE (Branch Prediction Side)

* uBTB
提供0-cycle的跳转方向、跳转目标地址、跳转属性的快速预测。

* RAS
返回地址栈RAS本质上类似一个环形buffer,用于预测跟踪call（也叫push,压栈）和return（也叫pop,出栈）指令对，及存储返回地址。每个RAS的表项（entry）存在2个域段: backlink和target,其中,backlink域存储的是每次执行call指令时对应的栈顶指针TOS, target域存储的是每次执行return指令时给出的目标地址(VA)。如果RAS每次预测是一个call(push)指令时,将会把一个返回地址存入RAS中; 如果RAS每次预测是一个return(pop)指令时,将会把一个返回地址从RAS中弹出;

![RAS_FIG](../figs/uArch/RAS_FIG.PNG){ width="800" } 

图: RAS微架构示意图

* GHR
用于存储每拍跳转指令最后的预测结果（跳转/不跳转），并根据过去的结果预测一个新的GHR值和IHR值，分别送往TAGE和IBTB模块进行哈希操作，以计算出折叠过后的查询序号，并对应上正确的跳转。

* TAGE
用于对跳转方向的预测。其中有四个预测表 (编号0~3) 和一个基础表。每个表中的每个表项存储了针对不同跳转的方向预测。每个表都由不同的序号索引，其中序号是通过全局的跳转历史与当前块的 PC 进行哈希计算得到。编号越大的表，会加入更长的跳转历史进行哈希，所以越准确。

* iBTB
在流水线F2阶段，如果iside侧的pre_decode模块解析得到块的跳转属性为间接跳转类型（含间接跳转INDIR、间接调用INDCALL），则会在iBTB提供一个较为准确的预测的目标地址。

* PRED 预测内部竞争逻辑
在流水线F3阶段，主预测器PRED会产生整个BFU模块最后的最为准确的预测信息。预测信息有3个：块跳转类型、块跳转方向、块跳转目标地址。
对于块跳转类型来说，静态预测器（static predictor）通过解析块头获得的块跳转类型是最准确的，因此直接将块属性传给主预测器（PRED）模块，用于最终的预测。
对于块跳转目标地址来说，静态预测器通过解析块头获得的块跳转目标地址在特定情况下才可信，即块跳转类型为FALL,DIRECT,CONCAT,CALL,COND时，通过解析块头，能够得到正确的跳转目标地址，其余情况，静态预测器得到的目标地址不可信。若为RET类型，则RAS在F1阶段预测后打两拍的结果最可信；若为INDIRECT或INDCALL类型，则iBTB得到的结果最可信；否则使用uBTB的结果。
对于块跳转方向来说，如果是COND块类型，则使用TAGE的预测结果；如果块类型为FALL,CALL,CONCAT类型，则视为不跳，其余情况都视为跳。

* BRQ
分支队列BRQ本质上类似一个FIFO,用于存储分支预测器的实时运行信息,并在必要时(例如mis-predict等)作为依据,用于分支预测器的更新和恢复。

![RAS_FIG](../figs/uArch/BRQ_FIG.PNG){ width="800" } 

 图 BRQ_TOP模块架构框图
BRQ的每个条目中的数据都很宽。我们需要在某些不同条件下获取一个条目的不同部分信息（Rob刷新/Bru刷新/BRQ正确解析），并将其翻转到下一个周期。如下所示，“√”代表在这种情况下将读取字段:

| BRQ ENT GRP | BRQ ENT Field | rob_flush | bru_flush | Bru correct resolve | width | start bit | end bit |
| ----------- | ------------- | --------- | --------- | ------------------- | ----- | --------- | ------- |
| GHR         | GHRQ_RIDX     | √       | √       | √                 | 8     | 0         | 7       |
| IHR         | BASE          | √       | √       | √                 | 12    | 20        | 27      |
| TAGE        | StartPos      |           | √       | √                 | 3     | 8         |         |
| TAGE        | STR           |           | √       | √                 | 1     | 11        |         |
| TAGE        | TNT           |           | √       | √                 | 1     | 19        |         |
| TAGE        | U_b3w0        |           | √       | √                 | 2     | 21        |         |
| TAGE        | CTR_b3w0      |           | √       | √                 | 2     | 23        |         |
| TAGE        | POS_b3w0      |           | √       | √                 | 2     | 25        |         |
| TAGE        | HIT_b3w0      |           | √       | √                 | 1     | 26        |         |
| TAGE        | U_b2w0        |           | √       | √                 | 2     | 28        |         |
| TAGE        | CTR_b2w0      |           | √       | √                 | 2     | 30        |         |
| TAGE        | POS_b2w0      |           | √       | √                 | 2     | 32        |         |
| TAGE        | HIT_b2w0      |           | √       | √                 | 1     | 33        |         |
| TAGE        | U_b1w0        |           | √       | √                 | 2     | 35        |         |
| TAGE        | CTR_b1w0      |           | √       | √                 | 2     | 37        |         |
| TAGE        | POS_b1w0      |           | √       | √                 | 2     |    39     |         |
| TAGE        | HIT_b1w0      |           | √       | √                 | 1     | 40        |         |
| TAGE        | U_b0w0        |           | √       | √                 | 2     | 42        |         |
| TAGE        | CTR_b0w0      |           | √       | √                 | 2     | 44        |         |
| TAGE        | POS_b0w0      |           | √       | √                 | 2     | 46        |         |
| TAGE        | HIT_b0w0      |           | √       | √                 | 1     | 47        |         |
| RS          | TOS           | √       | √       |                     | 6     | 53        |         |
| RS          | WPTR          | √       | √       |                     | 6     | 59        |         |
| IBTB        | HIT_BNK       |           | √       | √                 | 2     | 61        | 62      |
